import React, { useState } from "react";
import apiClient from "@/utils/axios";
import styles from "./ChatUI.module.css";

function ChatUI({ sessionId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState("");

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
      {/* 메시지 목록 */}
      <div className={styles.messageList}>
        {messages.map((msg, index) => (
          <div key={index} className={styles.message}>
            <span className={styles.messageUser}>
              {msg.sender === "user" ? "You" : "System"}
            </span>
            <p className={styles.messageText}>{msg.message}</p>
          </div>
        ))}
      </div>

      {/* 채팅 입력 필드 */}
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
