import AWS from 'aws-sdk';

const cognito = new AWS.CognitoIdentityServiceProvider();
const dynamoDB = new AWS.DynamoDB.DocumentClient();
const userPoolId = process.env.USER_POOL_ID;
const tableName = process.env.DYNAMODB_TABLE;

export const handler = async (event) => {
    try {
        
        const { email, status } = event;
        
        if (!email || !status) {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email and status are required fields.",
            };
        }
        
        if (email.trim() === "" || status.trim() === "") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email and status cannot be empty.",
            };
        }
        
        if (status !== "Confirmed" && status !== "Not Confirmed") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Invalid Status",
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
                message: "User didn't set security questions!",
            };
        }

        if (status === 'Confirmed') {
            
            const params = {
                UserPoolId: userPoolId,
                Username: event['email'],
                UserAttributes: [
                    {
                        Name: 'email_verified',
                        Value: 'true',
                    },
                ],
            };

            await cognito.adminUpdateUserAttributes(params).promise();
            
            const confirmParams = {
                UserPoolId: userPoolId,
                Username: event['email'],
            };

            await cognito.adminConfirmSignUp(confirmParams).promise();

            return {
                statusCode: 200,
                status: "Success",
                message: `User ${event['email']} has been successfully verified.`,
            };
        } else {
            return {
                statusCode: 400,
                status: "Failure",
                message: 'Status is not confirmed, cannot verify the user.',
            };
        }
    } catch (error) {
        return {
            statusCode: 500,
            status: "Failure",
            message: error.message,
        };
    }
};