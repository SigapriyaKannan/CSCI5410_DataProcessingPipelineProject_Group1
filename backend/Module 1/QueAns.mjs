import AWS from 'aws-sdk';

const dynamoDB = new AWS.DynamoDB.DocumentClient();
const cognito = new AWS.CognitoIdentityServiceProvider();
const userPoolId = process.env.USER_POOL_ID;
const tableName = process.env.DYNAMODB_TABLE;

export const handler = async (event) => {
    try {
        
        const { email, securityQuestion1, securityAnswer1, securityQuestion2, securityAnswer2 } = event;
        
        if (!email || !securityQuestion1 || !securityAnswer1 || !securityQuestion2 || !securityAnswer2) {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email, and Secuity Questions and Answers are required fields.",
            };
        }
        
        if (email.trim() === "" || securityQuestion1.trim() === "" || securityAnswer1.trim() === "" || securityQuestion2.trim() === "" || securityAnswer2.trim() === "") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email, and Secuity Questions and Answers cannot be empty.",
            };
        }
        
        const userParams = {
            UserPoolId: userPoolId,
            Username: email,
        };
        
        const userResponse = await cognito.adminGetUser(userParams).promise();

        const userStatus = userResponse.UserStatus;
        if (userStatus !== 'UNCONFIRMED') {
            return {
                statusCode: 400,
                status: "Failure",
                message: "User already set security questions.",
            };
        }
        

        const item = {
            email: email,
            securityQuestion1: securityQuestion1,
            securityAnswer1: securityAnswer1,
            securityQuestion2: securityQuestion2,
            securityAnswer2: securityAnswer2,
        };

        const params = {
            TableName: tableName,
            Item: item,
        };

        await dynamoDB.put(params).promise();

        return {
            statusCode: 201,
            status: "Success",
            message: "Security questions and answers stored successfully",
        };
    } catch (error) {
        return {
            statusCode: 400,
            status: "Failure",
            message: error.message,
        };
    }
};