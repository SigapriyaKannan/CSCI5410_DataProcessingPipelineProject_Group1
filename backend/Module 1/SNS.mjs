import AWS from 'aws-sdk';

const sns = new AWS.SNS();

export const handler = async (event) => {

    const { email, message, subject } = event;
    const topicName = email.replace(/[^\w\-]/g, '_');

    try {
        const existingTopics = await sns.listTopics().promise();
        const topicExists = existingTopics.Topics.some(topic => topic.TopicArn.endsWith(topicName));

        if (topicExists) {

            const topicArn = existingTopics.Topics.find(topic => topic.TopicArn.endsWith(topicName)).TopicArn;

            await sns.publish({
                Message: message,
                TopicArn: topicArn,
            }).promise();

            return {
                statusCode: 200,
                status: "Success",
                message: "Email sent successfully.",
            };
        } else {
            const createTopicResponse = await sns.createTopic({ Name: topicName }).promise();
            const topicArn = createTopicResponse.TopicArn;

            await sns.subscribe({
                Protocol: 'email',
                TopicArn: topicArn,
                Endpoint: email,
            }).promise();

            return {
                statusCode: 200,
                status: "Success",
                message: "Topic created successfully.",
            };
        }
    } catch (error) {
        console.error('Error processing request:', error);
        return {
            statusCode: 500,
            status: "Failure",
            message: "Failed to process request",
        };
    }
};