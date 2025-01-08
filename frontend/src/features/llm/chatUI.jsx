import React, { useState, useEffect } from "react";
import apiClient from "@/utils/axios";
import styles from "./ChatUI.module.css";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import rehypeRaw from "rehype-raw"; 

function ChatUI({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

  // 세션 초기화 시 대화 기록 불러오기
  useEffect(() => {
    const fetchHistory = async () => {
      try {
        const response = await apiClient.get(`/api/llmapp/chat/${sessionId}/history/`);
        if (response.status === 200) {
          setMessages(response.data.history);
        }
      } catch (error) {
        console.error("대화 기록 불러오기 실패:", error);
      }
    };

    fetchHistory();
  }, [sessionId]);

  const sendMessage = async () => {
    try {
      const response = await apiClient.post(`/api/llmapp/chat/`, {
        session_id: sessionId,
        message: newMessage,
      });
      setMessages([
        ...messages,
        { sender: "user", message: newMessage },
        { sender: "system", message: response.data.response },
      ]);
      setNewMessage("");
    } catch (error) {
      console.error("메시지 전송 실패:", error);
    }
  };

  return (
    <div className={styles.chatContainer}>
      <div className={styles.messageList}>
        {messages.map((msg, index) => (
          <div key={index} className={styles.message}>
            <span className={styles.messageUser}>
              {msg.sender === "user" ? "You" : "System"}
            </span>
            <ReactMarkdown 
                remarkPlugins={remarkGfm} 
                rehypePlugins={[rehypeRaw]} 
                className={styles.messageText}
            >
              {msg.message}
            </ReactMarkdown>
          </div>
        ))}
      </div>
      <div className={styles.chatInputContainer}>
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="메시지를 입력하세요..."
          className={styles.chatInput}
        />
        <button onClick={sendMessage} className={styles.sendButton}>
          보내기
        </button>
      </div>
    </div>
  );
}

export default ChatUI;
