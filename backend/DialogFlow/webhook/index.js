import express from "express";
import axios from "axios";
import bodyParser from "body-parser";

const app = express();

app.use(bodyParser.json());
app.use(bodyParser.urlencoded({ extended: false }));

async function getFileDetails(requestData) {
    try {
        const response = await axios.post(
            "https://q3mhoyo8i9.execute-api.us-east-1.amazonaws.com/prod/retrieve-file-by-process-code",
            requestData
        );
        console.log("Response from API:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error calling API:", error);
        return null;
    }
}

// Function to call the external API for registering a concern
async function registerConcern(requestData) {
    try {
        const response = await axios.post(
            "https://northamerica-northeast2-serverless-440903.cloudfunctions.net/PublisherFunction",
            requestData
        );
        console.log("Response from API:", response.data);
        return response.data;
    } catch (error) {
        console.error("Error calling API:", error);
        return null;
    }
}

// Webhook route
app.post("/webhook", async (request, response) => {
    let tag = request.body.fulfillmentInfo.tag;
    let jsonResponse = {};

    console.log("Dialogflow Request body:", JSON.stringify(request.body));

    if (tag === "APICallTag") {
        const user_email = request.body.sessionInfo.parameters.user_email;
        const process_code = request.body.sessionInfo.parameters.process_code;

        console.log("User Email:", user_email);
        console.log("Process Code:", process_code);

        const requestData = {
            user_email: user_email,
            process_code: process_code,
        };

        const jsonObj = await getFileDetails(requestData);

        if (jsonObj && jsonObj.processed_file_url) {
            jsonResponse = {
                fulfillment_response: {
                    messages: [
                        {
                            text: {
                                text: [
                                    `The file for process code ${process_code} is available at the following location:\n\n` +
                                    `Processed File URL: ${jsonObj.processed_file_url}`,
                                ],
                            },
                        },
                    ],
                },
            };
        } else {
            jsonResponse = {
                fulfillment_response: {
                    messages: [
                        {
                            text: {
                                text: [
                                    `Sorry, no file is available for the process code ${process_code}. Please check the code and try again.`,
                                ],
                            },
                        },
                    ],
                },
            };
        }

        response.json(jsonResponse);

    } else if (tag === "RegisterConcernTag") {
        const user_email = request.body.sessionInfo.parameters.user_email;
        const message = request.body.sessionInfo.parameters.concern;
        const process_code = request.body.sessionInfo.parameters.process_code;

        console.log("User Email:", user_email);
        console.log("Concern:", message);
        console.log("Process Code:", process_code);

        const requestData = {
            user_email: user_email,
            message: message,
            process_code: process_code,
        };

        const jsonObj = await registerConcern(requestData);

        if (jsonObj && jsonObj.status === "success") {
            jsonResponse = {
                fulfillment_response: {
                    messages: [
                        {
                            text: {
                                text: [
                                    `Your concern has been successfully registered.`,
                                ],
                            },
                        },
                    ],
                },
            };
        } else {
            jsonResponse = {
                fulfillment_response: {
                    messages: [
                        {
                            text: {
                                text: [
                                    `Failed to register your concern. Please try again later.`,
                                ],
                            },
                        },
                    ],
                },
            };
        }

        response.json(jsonResponse);

    } else {
        jsonResponse = {
            fulfillment_response: {
                messages: [
                    {
                        text: {
                            text: [
                                `There are no fulfillment responses defined for "${tag}" tag.`,
                            ],
                        },
                    },
                ],
            },
        };

        response.json(jsonResponse);
    }
});

export const webhook = app;