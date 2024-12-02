# Use the Amazon Linux base image for Lambda
FROM public.ecr.aws/lambda/python:3.9

# Set environment variables for the S3 bucket name and DynamoDB table
ENV S3_BUCKET_NAME=upload-bucket-nerprocess
ENV DYNAMODB_TABLE=NamedEntities

# Install spaCy
RUN pip install boto3 spacy requests_toolbelt

# Install English model for spaCy
RUN python -m spacy download en_core_web_sm

# Copy the function code to the /var/task directory
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

# Set the Lambda handler
CMD ["lambda_function.lambda_handler"]