import AWS from 'aws-sdk';

const cognito = new AWS.CognitoIdentityServiceProvider();
const dynamoDB = new AWS.DynamoDB.DocumentClient();
const userPoolId = process.env.USER_POOL_ID;
const tableName = process.env.DYNAMODB_TABLE;

export const handler = async (event) => {
    try {
        
        const { email } = event;
        
        if (!email) {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email is required fields.",
            };
        }
        
        if (email.trim() === "") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email cannot be empty.",
            };
        }
        
        const cognitoParams = {
            UserPoolId: userPoolId,
            Filter: `email = "${email}"`,
        };

        const cognitoResult = await cognito.listUsers(cognitoParams).promise();

        if (cognitoResult.Users.length === 0) {
            return {
                statusCode: 404,
                status: "Failure",
                message: "User not found in Cognito user pool.",
            };
        }
        
        const getParams = {
            TableName: tableName,
            Key: {
                email: email,
            },
        };

        const dynamoResult = await dynamoDB.get(getParams).promise();

        if (!dynamoResult.Item) {
            return {
                statusCode: 404,
                status: "Failure",
                message: "Users security questions not found!",
            };
        }
        
        const operand1 = Math.floor(Math.random() * 100) + 1;
        const operand2 = Math.floor(Math.random() * 100) + 1;
        const isAddition = Math.random() >= 0.5;

        let answer;
        let operation;

        if (isAddition) {
            answer = operand1 + operand2;
            operation = "addition";
        } else {
            answer = operand1 - operand2;
            operation = "subtraction";
        }

        return {
            statusCode: 200,
            status: "Success",
            message: "Math skill generated successfully.",
            operand: operation,
            operands: [operand1, operand2],
            answer: answer,
        };
        
    } catch (error) {
        return {
            statusCode: 500,
            status: "Failure",
            message: error.message,
        };
    }
};