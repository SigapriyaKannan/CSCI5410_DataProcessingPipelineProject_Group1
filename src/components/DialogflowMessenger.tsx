'use client'
import { useEffect } from 'react';

const DialogflowMessenger = () => {
  useEffect(() => {
    // Add the Dialogflow styles dynamically to the document
    const dfStyle = document.createElement("link");
    dfStyle.rel = "stylesheet";
    dfStyle.href = "https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/themes/df-messenger-default.css";
    document.head.appendChild(dfStyle);

    // Add the Dialogflow script dynamically to the document
    const dfScript = document.createElement("script");
    dfScript.src = "https://www.gstatic.com/dialogflow-console/fast/df-messenger/prod/v1/df-messenger.js";
    document.head.appendChild(dfScript);

    // Wait for the script to load, then create the <df-messenger> element
    dfScript.onload = () => {
      const dfMessenger = document.createElement("df-messenger");

      // Set attributes for the Dialogflow messenger
      dfMessenger.setAttribute("location", "us-central1");
      dfMessenger.setAttribute("project-id", "data-processing-project-442819");
      dfMessenger.setAttribute("agent-id", "6c27a25b-88af-450b-b764-306ef9ff4847");
      dfMessenger.setAttribute("language-code", "en");
      dfMessenger.setAttribute("max-query-length", "-1");
      dfMessenger.setAttribute("storage-option", "none");
      dfMessenger.setAttribute("INTENT", "WELCOME");

      // Add event listener to capture user query
      dfMessenger.addEventListener('df-request-sent', function(event:any) {
        const userEmail = localStorage.getItem("user_email");

        // Add user_email to session parameters
        event.detail.requestBody.queryInput = {
          ...event.detail.requestBody.queryInput,
          text: {
            text: event.detail.requestBody.queryInput.text.text + " , " + userEmail,
          },
        };
      });

      // Create the chat bubble configuration
      const dfChatBubble = document.createElement("df-messenger-chat-bubble");
      dfChatBubble.setAttribute("chat-title", "QuickDataProcessor Assistant");
      dfMessenger.appendChild(dfChatBubble);

      // Apply custom styles
      const customStyle = `
        df-messenger {
          z-index: 999;
          position: fixed;
          --df-messenger-font-color: #000;
          --df-messenger-font-family: Google Sans;
          --df-messenger-chat-background: #f3f6fc;
          --df-messenger-message-user-background: #d3e3fd;
          --df-messenger-message-bot-background: #fff;
          bottom: 16px;
          right: 16px;
        }
      `;

      // Add custom styles to the page
      const styleTag = document.createElement("style");
      styleTag.textContent = customStyle;
      document.head.appendChild(styleTag);

      // Append the Dialogflow messenger to the body
      document.body.appendChild(dfMessenger);
    };
  }, []);

  return null; // This component does not render anything directly
};

export default DialogflowMessenger;
