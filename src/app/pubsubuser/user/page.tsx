'use client';

import { useState, useEffect } from 'react';
import axios from 'axios'; // Import axios

export default function UserChatPage() {
  const [processCodes, setProcessCodes] = useState<string[]>([]);
  const [selectedProcessCode, setSelectedProcessCode] = useState<string>('');
  const [chatMessages, setChatMessages] = useState<{ sender: string; message: string }[]>([]);
  const [newMessage, setNewMessage] = useState<string>('');
  const [isLoading, setIsLoading] = useState(false);
  const [isFetchingProcessCodes, setIsFetchingProcessCodes] = useState(false);

  const userEmail = localStorage.getItem('user_email'); // Retrieve user email from localStorage

  useEffect(() => {
    if (!userEmail) {
      console.error('User email is not available in localStorage');
    }
    fetchProcessCodes();
  }, [userEmail, setProcessCodes, setIsFetchingProcessCodes]);

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

  // Fetch process codes for the user manually when the button is clicked
  const fetchProcessCodes = async () => {
    if (!userEmail) {
      console.error('User email is not available in localStorage');
      return;
    }

    setIsFetchingProcessCodes(true);
    try {
      console.log('Fetching process codes for user:', userEmail);
      const response = await axios.post('https://northamerica-northeast2-serverless-440903.cloudfunctions.net/GetUserProcessCodes', {
        user_email: userEmail,
      });

      if (response.status === 200) {
        console.log('Process codes received:', response.data);
        setProcessCodes(response.data.codes || []);
      } else {
        console.error('Error fetching process codes:', response.data);
      }
    } catch (error) {
      console.error('Error fetching process codes:', error);
    } finally {
      setIsFetchingProcessCodes(false);
    }
  };

  // Function to send a message
  const sendMessage = async () => {
    if (!selectedProcessCode || !newMessage) {
      console.error('Selected process code or message is missing');
      return;
    }

    setIsLoading(true);
    console.log('Sending message...');
    console.log('Selected Process Code:', selectedProcessCode);
    console.log('New Message:', newMessage);

    try {
      if (!userEmail) {
        console.error('User email is not available in localStorage');
        return;
      }

      const payload = {
        user_email: userEmail,
        process_code: selectedProcessCode,
        message: newMessage,
      };

      console.log('Request Payload:', payload);

      const response = await axios.post(
        'https://northamerica-northeast2-serverless-440903.cloudfunctions.net/PublisherFunction',
        payload,
        {
          headers: { 'Content-Type': 'application/json' }, // Ensuring correct headers
        }
      );

      console.log('Response from PublisherFunction:', response.data);

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

  // Function to refresh chat messages
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

  // Function to end chat
  const endChat = async () => {
    if (!userEmail) {
      console.error('User email is not available in localStorage');
      return;
    }

    try {
      console.log('Ending chat for user:', userEmail);
      const response = await axios.post(
        'https://northamerica-northeast2-serverless-440903.cloudfunctions.net/EndConversationApi',
        {
            process_code: selectedProcessCode,
            role: localStorage.getItem('role'),
            status: "yes",
          
        },
        { headers: { 'Content-Type': 'application/json' } }
      );
      if (response.status === 200) {
        alert('Chat ended successfully');
        setChatMessages([]);
        setSelectedProcessCode('');
      } else {
        console.error('Error ending chat:', response.data);
      }
    } catch (error) {
      console.error('Error during endChat execution:', error);
    }
  };

  return (
    <div className="chat-container">
      <h1 className="text-center text-2xl font-bold mb-6">User Chat</h1>

      {/* Button to fetch process codes */}
      <div className="mb-4 text-center">
        <button
          onClick={fetchProcessCodes}
          disabled={isFetchingProcessCodes}
          className={`${
            isFetchingProcessCodes ? 'bg-gray-400' : 'bg-blue-500 hover:bg-blue-600'
          } text-white p-2 rounded-lg`}
        >
          {isFetchingProcessCodes ? 'Fetching Process Codes...' : 'Fetch Process Codes'}
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
      <div className="chat-messages bg-gray-100 p-4 rounded-lg max-h-60 overflow-y-auto mb-6">
        {chatMessages.length > 0 ? (
          chatMessages.map((msg, index) => (
            <div key={index} className={`message ${msg.sender === 'user' ? 'bg-blue-200' : 'bg-green-200'} p-2 my-2 rounded`}>
              <strong>{msg.sender === 'user' ? 'User' : 'Agent'}:</strong> {msg.message}
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

      {/* Refresh Button */}
      {/* <button
        onClick={refreshChat}
        disabled={!selectedProcessCode || isLoading}
        className="mt-4 bg-green-500 text-white p-2 rounded-lg w-full"
      >
        Refresh Chat
      </button> */}

      {/* End Chat Button */}
      <button
        onClick={endChat}
        disabled={!selectedProcessCode || isLoading}
        className="mt-4 bg-red-500 text-white p-2 rounded-lg w-full"
      >
        End Chat
      </button>
    </div>
  );
}
