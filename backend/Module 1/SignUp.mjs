import AWS from 'aws-sdk';
const { CognitoIdentityServiceProvider } = AWS;

const cognito = new CognitoIdentityServiceProvider();
const clientId = process.env.CLIENT_ID;

export const handler = async (event) => {
    try {
        
        const { email, password, role } = event;
        
        if (!email || !password || !role) {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email, password, and role are required fields.",
            };
        }
        
        if (email.trim() === "" || password.trim() === "" || role.trim() === "") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Email, password, and role cannot be empty.",
            };
        }
        
        if (role !== "Guest" && role !== "Registered" && role !== "Agent") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Invalid Role",
            };
        }

        const signUpParams = {
            ClientId: clientId,
            Username: email,
            Password: password,
            UserAttributes: [
                { Name: 'email', Value: email },
                { Name: 'custom:role', Value: role },
            ],
        };

        const signUpResponse = await cognito.signUp(signUpParams).promise();

        return {
            statusCode: 201,
            status: "Success",
            message: signUpResponse.UserSub,
        };
    } catch (error) {
        return {
            statusCode: 400,
            status: "Failure",
            message: error.message,
        };
    }
};