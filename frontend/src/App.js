import React, { useState } from "react";
import axios from "axios";
import { FaPaperPlane } from "react-icons/fa";

const API_URL = "https://medical-ai-chatbot.onrender.com/ask"; // Deployed backend URL

function App() {
  const [question, setQuestion] = useState("");
  const [response, setResponse] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!question.trim()) return;

    setLoading(true);
    setResponse(null);

    try {
      const res = await axios.post(API_URL, { question });
      setResponse(res.data);
    } catch (error) {
      setResponse({ response: "Error fetching response. Try again." });
    }

    setLoading(false);
  };

  return (
    <div className="chat-container">
      <h1>Medical AI Chatbot</h1>
      
      <div className="chat-box">
        {response && (
          <div className="response">
            <strong>AI:</strong> {response.response} <br />
            {response.citation && (
              <a href={response.citation} target="_blank" rel="noopener noreferrer">
                [Source]
              </a>
            )}
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} className="chat-form">
        <input
          type="text"
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          placeholder="Ask a medical question..."
        />
        <button type="submit" disabled={loading}>
          {loading ? "Thinking..." : <FaPaperPlane />}
        </button>
      </form>
    </div>
  );
}

export default App;
