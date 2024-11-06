import AWS from 'aws-sdk';

const cognito = new AWS.CognitoIdentityServiceProvider();
const dynamoDb = new AWS.DynamoDB.DocumentClient();
const clientId = process.env.CLIENT_ID;
const tableName = process.env.USER_SECURITY_TABLE;

export const handler = async (event) => {
    try {
        
        const { email, password } = event;
        
        if (!email || !password) {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email, and password are required fields.",
            };
        }
        
        if (email.trim() === "" || password.trim() === "") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email, and password cannot be empty.",
            };
        }

        const authParams = {
            AuthFlow: 'USER_PASSWORD_AUTH',
            ClientId: clientId,
            AuthParameters: {
                USERNAME: event['email'],
                PASSWORD: event['password']
            }
        };

        const authResponse = await cognito.initiateAuth(authParams).promise();
        const IdToken = authResponse.AuthenticationResult.IdToken;
        const AccessToken = authResponse.AuthenticationResult.AccessToken;

        const getUserParams = {
            TableName: tableName,
            Key: {
                email: event['email']
            }
        };

        const user = await dynamoDb.get(getUserParams).promise();

        if (!user.Item) {
            return {
                statusCode: 404,
                status: "Failure",
                message: "User security questions not found!.",
            };
        }

        const { securityQuestion1, securityAnswer1, securityQuestion2, securityAnswer2 } = user.Item;

        const randomSelection = Math.random() < 0.5 ? 
            { question: securityQuestion1, answer: securityAnswer1 } : 
            { question: securityQuestion2, answer: securityAnswer2 };

        return {
            statusCode: 200,
            status: "Success",
            message: "User logged in successfuly!",
            IdToken: IdToken,
            AccessToken: AccessToken,
            securityQuestion: randomSelection.question,
            securityAnswer: randomSelection.answer,
        };

    } catch (error) {
        return {
            statusCode: 500,
            status: "Failure",
            message: error.message,
        };
    }
};