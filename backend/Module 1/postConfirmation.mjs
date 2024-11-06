import AWS from 'aws-sdk';

const dynamoDb = new AWS.DynamoDB.DocumentClient();
const tableName = process.env.USER_TABLE;

export const handler = async (event) => {
    
    const userId = event.request.userAttributes.sub;
    const email = event.request.userAttributes.email;
    const role = event.request.userAttributes['custom:role'];

    const params = {
        TableName: tableName,
        Item: {
            userId: userId,
            email: email,
            role: role,
        },
    };

    try {
        await dynamoDb.put(params).promise();
        
    } catch (error) {
        console.error('Error saving user details:', error);
    }
    
    return event;
};