import React, { useState, useEffect, useRef } from "react";
import { v4 as uuidv4 } from "uuid";

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

interface Message {
  id: string;
  content: string;
  sender: "user" | "bot";
}

const ChatPage: React.FC = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [ws, setWs] = useState<WebSocket | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const token = localStorage.getItem("access_token");
  const userId = localStorage.getItem("user_id");

  console.log("Token:", token);
  console.log("User ID:", userId);
  console.log("API_URL:", API_URL);

  useEffect(() => {
    if (!token || !userId) {
      console.error("No token or user_id found in localStorage");
      return;
    }

    const startChat = async () => {
      try {
        console.log("Starting chat for user:", userId);

        const res = await fetch(`${API_URL}/gpt_module/start-chat/${userId}`, {
          method: "POST",
          headers: {
            Authorization: `Bearer ${token}`,
          },
        });

        const data = await res.json();
        console.log("Start chat response:", data);

        if (!data.chat_id) {
          console.error("Failed to get chat_id", data);
          return;
        }

        const wsProtocol = API_URL.startsWith("https") ? "wss" : "ws";
        const wsHost = new URL(API_URL).host;
        const wsUrl = `${API_URL.replace(/^http/, "ws")}/gpt_module/ws/${data.chat_id}`;

        console.log("Connecting WebSocket to:", wsUrl);

        const socket = new WebSocket(wsUrl);

        socket.onopen = () => {
          console.log("WebSocket connected");
        };

        socket.onmessage = (event) => {
          console.log("Received message:", event.data);

          const msg: Message = {
            id: uuidv4(),
            content: event.data,
            sender: "bot",
          };

          setMessages((prev) => [...prev, msg]);
        };

        socket.onerror = (err) => {
          console.error("WebSocket error:", err);
        };

        socket.onclose = () => {
          console.log("WebSocket closed");
        };

        setWs(socket);
      } catch (err) {
        console.error("Error starting chat:", err);
      }
    };

    startChat();
  }, [token, userId]);

  const sendMessage = () => {
    if (ws && input.trim()) {
      ws.send(input);

      const msg: Message = {
        id: uuidv4(),
        content: input,
        sender: "user",
      };

      setMessages((prev) => [...prev, msg]);
      setInput("");
      console.log("Sent:", msg.content);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      sendMessage();
    }
  };

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  return (
    <div className="flex flex-col h-screen bg-gradient-to-br from-purple-400 to-purple-600 p-4">
      <h1 className="text-3xl text-white text-center font-semibold mb-4">
        Therapy Chat
      </h1>

      <div className="flex-1 overflow-y-auto bg-purple-300/30 backdrop-blur-md rounded-lg p-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`my-2 p-2 rounded-lg max-w-xs ${
              msg.sender === "user"
                ? "bg-purple-500 text-white self-end"
                : "bg-white text-gray-800 self-start"
            }`}
          >
            {msg.content}
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="mt-4 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message..."
          className="flex-1 p-3 rounded-lg bg-purple-200/40 text-white placeholder-white/70 focus:outline-none focus:ring-2 focus:ring-white"
        />
        <button
          onClick={sendMessage}
          className="bg-purple-500 hover:bg-purple-600 text-white font-medium px-4 rounded-lg transition-colors"
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatPage;
