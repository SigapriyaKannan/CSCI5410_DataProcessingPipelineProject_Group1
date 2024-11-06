import AWS from 'aws-sdk';

const cognito = new AWS.CognitoIdentityServiceProvider();

export const handler = async (event) => {
    try {
        const { token } = event;

        if (!token || token.trim() === "") {
            return {
                statusCode: 400,
                status: "Failure",
                message: "Token is required for logout.",
            };
        }

        const globalSignOutParams = {
            AccessToken: token,
        };

        await cognito.globalSignOut(globalSignOutParams).promise();

        return {
            statusCode: 200,
            status: "Success",
            message: "User has been logged out successfully.",
        };

    } catch (error) {
        return {
            statusCode: 500,
            status: "Failure",
            message: error.message,
        };
    }
};