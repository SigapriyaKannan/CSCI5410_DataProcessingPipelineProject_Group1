import sys
import time
import json
import boto3
import uuid
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *

# Get job arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME', 's3_input_key', 'dynamodb_table_name', 'bucket_name', 'user_email'])
print("Job Name: ", args['JOB_NAME'])

# Initialize Spark and Glue contexts
sc = SparkContext.getOrCreate()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# AWS S3 and DynamoDB Connection setup
s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(args['dynamodb_table_name'])
print("AWS S3 and DynamoDB Connection established")

# Get the S3 input key and bucket name from job arguments
s3_input_key = args['s3_input_key']
bucket_name = args['bucket_name']
file_path = f"s3://{bucket_name}/{s3_input_key}"

# Read the input JSON file from S3
df = spark.read.option("multiline", "true").json(file_path)


def get_original_column_order(bucket_name, s3_input_key):
    s3_object = s3.get_object(Bucket=bucket_name, Key=s3_input_key)
    json_content = json.loads(s3_object['Body'].read())
    if isinstance(json_content, list):
        return list(json_content[0].keys())
    elif isinstance(json_content, dict):
        return list(json_content.keys())
    else:
        raise ValueError("Unexpected JSON format in the input file")


# Function to check if the DataFrame is flattened
def is_flattened(df):
    for field in df.schema.fields:
        if isinstance(field.dataType, (StructType, ArrayType, MapType)):
            return False
    return True


# Function to flatten the JSON DataFrame
def flatten_json(df):
    while not is_flattened(df):
        columns_to_process = 2
        columns_to_drop = []
        processed_columns = 0

        for col_name, col_type in df.dtypes:
            if processed_columns >= columns_to_process:
                break

            field_type = df.schema[col_name].dataType

            if isinstance(field_type, StructType):
                for field in field_type.fields:
                    new_col_name = f"{col_name}_{field.name}"
                    df = df.withColumn(
                        new_col_name,
                        when(col(col_name).isNotNull(), col(col_name).getItem(field.name)).otherwise(lit(None))
                    )
                columns_to_drop.append(col_name)
                processed_columns += 1

            elif isinstance(field_type, ArrayType):
                df = df.withColumn(col_name, explode(coalesce(col(col_name), array(lit(None)))))
                processed_columns += 1

            elif isinstance(field_type, MapType):
                df = df.withColumn(col_name, explode(coalesce(col(col_name), lit({}))))
                processed_columns += 1

        df = df.drop(*columns_to_drop)

    return df


if is_flattened(df):
    original_column_order = get_original_column_order(bucket_name, s3_input_key)
    if original_column_order:
        df = df.select([col for col in original_column_order if col in df.columns])
else:
    df = flatten_json(df)

# flattened data write as CSV to S3
csv_filename = s3_input_key.replace('.json', '.csv')
output_path = f"s3://{bucket_name}/output/{csv_filename}"
df.write.mode("overwrite").option("header", "true").csv(output_path)

# Introduce a delay to account for writing the CSV to S3
time.sleep(60)

# Read the CSV back to extract metadata
csv_df = spark.read.option("header", "true").csv(output_path)
row_count = csv_df.count()
column_list = csv_df.columns
schema_types = [(field.name, str(field.dataType)) for field in csv_df.schema.fields]

# Save metadata and job status in DynamoDB
job_status = "SUCCEEDED"
table.put_item(
    Item={
        'user_email': args['user_email'],  # Partition key
        'processed_file_name': csv_filename,
        'S3JsonFilePath': file_path,
        'S3CsvFilePath': output_path,
        'JobStatus': job_status,
        'RowCount': row_count,
        'Columns': column_list,
        'SchemaTypes': json.dumps(schema_types),
        'Timestamp': int(time.time()),
        'process_code': str(uuid.uuid4())
    }
)
print(
    f"Metadata saved to DynamoDB for {s3_input_key}: Status - {job_status}, Rows - {row_count}, Columns - {column_list}")

# Glue job Completion
job.commit()