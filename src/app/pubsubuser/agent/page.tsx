'use client';

import { useState, useEffect } from 'react';
import axios from 'axios';

export default function AgentChatPage() {

  const [processCodes, setProcessCodes] = useState<string[]>([]);
  const [selectedProcessCode, setSelectedProcessCode] = useState<string>('');
  const [chatMessages, setChatMessages] = useState<{ sender: string; message: string }[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingProcessCodes, setIsFetchingProcessCodes] = useState(false);
  const [isEndingChat, setIsEndingChat] = useState(false); // To track if the agent is ending the chat
  const [processCodeForEndChat, setProcessCodeForEndChat] = useState<string>(''); // Store process code when ending chat
  const [agentEmail, setAgentEmail] = useState<string | null>(null); // State to hold agent email
  const [role, setRole] = useState<string>('agent'); // State to hold role

  // Use effect to safely access localStorage only on the client side
  useEffect(() => {
    const userInfo = JSON.parse(localStorage.getItem('user') || '{}');
    const agentEmailFromStorage = userInfo.email;
    const roleFromStorage = userInfo.role;

    if (agentEmailFromStorage) {
      setAgentEmail(agentEmailFromStorage);
    }

    if (roleFromStorage) {
      setRole(roleFromStorage);
    } else {
      setRole('agent'); // Default role if not found
    }
  }, []); // Empty dependency array ensures this runs only once on the client side

  useEffect(() => {
    if (!agentEmail) {
      // console.error('Agent email is not available in localStorage');
      return;
    }
    fetchProcessCodes();
  }, [agentEmail]);

  useEffect(() => {
    if (!selectedProcessCode) return;

    // Initial call to refresh chat
    refreshChat();

    // Poll every 20 seconds
    const intervalId = setInterval(() => {
      refreshChat();
    }, 20000);

    // Cleanup the interval when the component unmounts or selectedProcessCode changes
    return () => {
      clearInterval(intervalId);
    };
  }, [selectedProcessCode]);

  // Fetch process codes assigned to the agent
  const fetchProcessCodes = async () => {
    if (!agentEmail) {
      console.error('Agent email is not available in localStorage');
      return;
    }
  
    setIsFetchingProcessCodes(true);
    try {
      console.log('Fetching process codes for agent:', agentEmail);
      const response = await axios.post(
        'https://northamerica-northeast2-serverless-440903.cloudfunctions.net/getAgentConversationsAPI',
        { agent_email: agentEmail },
        { headers: { 'Content-Type': 'application/json' } }
      );
  
      console.log('Process codes received:', response.data);
  
      if (response.status === 200) {
        setProcessCodes(response.data.conversations || []);
      } else if (response.status === 404) {
        const errorMessage = response.data.message || 'No conversations found for the agent.';
        console.error('Error:', errorMessage);
        alert(errorMessage); // Show error message
        setProcessCodes([]);  // Clear process codes
      } else {
        console.error('Unexpected response status:', response.status, response.data);
      }
    } catch (error) {
      // Handle Axios error response
      if (error) {
        // Axios error response contains more info like status and message
        console.error('Error response:', error);
        // alert(`Error: ${error.data?.message || error.message}`);
      } else {
        // General error handling
        console.error('Error fetching process codes:', error);
        alert('An error occurred while fetching process codes.');
      }
    } finally {
      setIsFetchingProcessCodes(false);
    }
  };
  


  // Send a message from the agent
  const sendMessage = async () => {
    if (!selectedProcessCode || !newMessage) {
      console.error('Selected process code or message is missing');
      return;
    }

    setIsLoading(true);
    try {
      if (!agentEmail) {
        console.error('Agent email is not available in localStorage');
        return;
      }

      const payload = {
        agent_email: agentEmail,
        process_code: selectedProcessCode,
        message: newMessage,
      };

      console.log('Request Payload:', payload);

      const response = await axios.post(
        'https://northamerica-northeast2-serverless-440903.cloudfunctions.net/AgentReplyFunction',
        payload,
        { headers: { 'Content-Type': 'application/json' } }
      );

      console.log('Response from agent_reply function:', response.data);

      if (response.status === 200) {
        alert(response.data.message); // Toast message for user
        setNewMessage('');
        await refreshChat(); // Fetch updated messages
      } else {
        console.error('Error sending message:', response.data);
      }
    } catch (error) {
      console.error('Error during sendMessage execution:', error);
    } finally {
      setIsLoading(false);
    }
  };

  // Refresh chat messages
  const refreshChat = async () => {
    if (!selectedProcessCode) return;

    try {
      console.log('Refreshing chat for process code:', selectedProcessCode);
      const response = await axios.post(
        'https://northamerica-northeast2-serverless-440903.cloudfunctions.net/RefreshChatFunction',
        { process_code: selectedProcessCode },
        { headers: { 'Content-Type': 'application/json' } }
      );

      console.log('Chat messages refreshed:', response.data);
      setChatMessages(response.data.messages || []);
    } catch (error) {
      console.error('Error refreshing chat:', error);
    }
  };

  // End the chat conversation
  const endChat = async () => {
    
    // Prompt the agent to choose Yes/No and enter the process code
    setIsEndingChat(true);  // Display Yes/No options for ending the chat
  };

  // Handle the agent's confirmation (Yes/No)
  const handleEndChatConfirmation = async (status: string) => {
    // if (!processCodeForEndChat || !role) {
    //   console.error('Process code or role is missing');
    //   return;
    // }

    setIsEndingChat(false); // Hide the confirmation options

    const payload = {
      process_code: selectedProcessCode, // Use the process code entered by the agent
      role: role || 'agent',  // Use role from localStorage or default to 'agent'
      status: status,  // Use "yes" or "no" based on the agent's choice
    };

    try {
      console.log('Ending chat for process code:', selectedProcessCode, JSON.stringify(payload));

      const response = await axios.post(
        'https://northamerica-northeast2-serverless-440903.cloudfunctions.net/EndConversationApi',
        payload,  // Ensure the payload is stringified as JSON
        { headers: { 'Content-Type': 'application/json' } }
      );

      console.log('Response from end conversation function:', response.data);
      alert(response.data.message);  // Show confirmation message

      // Optionally, clear the chat messages or redirect the user
      setChatMessages([]);
      setSelectedProcessCode('');
      fetchProcessCodes();
    } catch (error) {
      console.error('Error ending chat:', error);
    }
  };

  return (
    <div className="chat-container">
      <h1 className="text-center text-3xl font-bold mb-6">Agent Chat</h1>

      {/* Button to fetch process codes */}
      <div className="mb-4 text-center">
        <button
          onClick={fetchProcessCodes}
          disabled={isFetchingProcessCodes}
          className={`${
            isFetchingProcessCodes ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'
          } text-white p-2 rounded-lg`}
        >
          {isFetchingProcessCodes ? 'Fetching Process Codes...' : 'Fetch Assigned Conversations'}
        </button>
      </div>

      {/* Process Code Selection */}
      <label className="block mb-4">
        <span className="text-lg">Select Process Code:</span>
        <select
          value={selectedProcessCode}
          onChange={(e) => setSelectedProcessCode(e.target.value)}
          disabled={isFetchingProcessCodes || isLoading}
          className="w-full p-2 mt-2 border rounded-lg"
        >
          <option value="">-- Select Process Code --</option>
          {processCodes.map((code) => (
            <option key={code} value={code}>
              {code}
            </option>
          ))}
        </select>
      </label>

      {/* Chat Messages */}
      <div className="chat-messages bg-gray-100 p-4 rounded-lg max-h-96 overflow-y-auto mb-6">
        {chatMessages.length > 0 ? (
          chatMessages.map((msg, index) => (
            <div
              key={index}
              className={`message ${
                msg.sender === 'agent' ? 'bg-blue-300' : 'bg-green-300'
              } p-2 my-2 rounded`}
            >
              <strong>{msg.sender === 'agent' ? 'Agent' : 'User'}:</strong> {msg.message}
            </div>
          ))
        ) : (
          <p>No messages yet.</p>
        )}
      </div>

      {/* New Message Input */}
      <div className="flex items-center gap-4">
        <input
          type="text"
          placeholder="Type your message"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          disabled={isLoading}
          className="p-2 w-full border rounded-lg"
        />
        <button
          onClick={sendMessage}
          disabled={!selectedProcessCode || !newMessage || isLoading}
          className={`${
            isLoading ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'
          } text-white p-2 rounded-lg`}
        >
          {isLoading ? 'Sending...' : 'Send'}
        </button>
      </div>

            {/* End Chat Button */}
            <div className="mt-6 text-center">
            <button
        onClick={endChat}
        disabled={!selectedProcessCode || isLoading}
        className="mt-4 bg-red-500 text-white p-2 rounded-lg w-full"
      >
        End Chat
      </button>
      </div>

      {/* Confirmation Dialog for Ending Chat */}
      {isEndingChat && (
        <div className="confirmation-dialog fixed top-0 left-0 right-0 bottom-0 bg-gray-500 bg-opacity-50 flex justify-center items-center">
          <div className="bg-white p-6 rounded-lg w-1/3">
            <h2 className="text-xl font-bold mb-4">Are you sure you want to end the chat?</h2>
            <div className="mb-4">
              <label className="block text-lg mb-2">Enter Process Code to Confirm:</label>
              {/* <input
                type="text"
                value={processCodeForEndChat}
                onChange={(e) => setProcessCodeForEndChat(e.target.value)}
                className="w-full p-2 border rounded-lg"
                placeholder="Process Code"
              /> */}
            </div>
            <div className="flex justify-around">
              <button
                onClick={() => handleEndChatConfirmation('yes')}
                className="bg-green-500 hover:bg-green-600 text-white py-2 px-4 rounded-lg"
              >
                Yes
              </button>
              <button
                onClick={() => handleEndChatConfirmation('no')}
                className="bg-red-500 hover:bg-red-600 text-white py-2 px-4 rounded-lg"
              >
                No
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

