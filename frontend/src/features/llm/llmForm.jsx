"use client";

import React, { useState, useEffect } from "react";
import apiClient from "@/utils/axios";
import styles from "./LLMForm.module.css";
import ChatUI from "@/features/llm/chatUI";

function LLMForm() {
  const [isPdfUploaded, setIsPdfUploaded] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [progress, setProgress] = useState(0); // 진행률
  const [isLoading, setIsLoading] = useState(false);
  const [pdfId, setPdfId] = useState(null); // 업로드된 PDF ID
  const [chatSessionId, setChatSessionId] = useState(null); // 채팅 세션 ID

  const handlePdfUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) {
      setUploadStatus("파일을 선택해주세요.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);

    try {
      setIsLoading(true);
      setUploadStatus(""); // 상태 초기화

      const response = await apiClient.post("/api/llmapp/upload/", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      if (response.status === 200) {
        setIsPdfUploaded(true);
        setUploadStatus("PDF 업로드 중...");
        setPdfId(response.data.pdf_id);
        pollProgress(response.data.pdf_id);
      }
    } catch (error) {
      console.error("PDF 업로드 실패:", error);
      setUploadStatus(
        error.response?.data?.error || "PDF 업로드 중 오류가 발생했습니다."
      );
    } finally {
      setIsLoading(false);
    }
  };

  const pollProgress = (id) => {
    const interval = setInterval(async () => {
      try {
        const response = await apiClient.get(`/api/llmapp/progress/${id}/`);
        const progress = response.data.progress;
        setProgress(progress);

        if (progress === 100) {
          clearInterval(interval);
          setUploadStatus("PDF 처리가 완료되었습니다!");
          startChatSession(id); // 채팅 세션 시작
        }
      } catch (error) {
        console.error("진행률 확인 실패:", error);
        clearInterval(interval);
      }
    }, 1000); // 1초 간격으로 진행률 확인
  };

  const startChatSession = async (pdfId) => {
    try {
      const response = await apiClient.post("/api/llmapp/start_chat/", {
        pdf_id: pdfId,
      });

      if (response.status === 200) {
        setChatSessionId(response.data.chat_session_id);
      }
    } catch (error) {
      console.error("채팅 세션 시작 실패:", error);
    }
  };

  return (
    <div className={styles.container}>
      <main className={styles.main}>
        <h1 className={styles.header}>
          {isPdfUploaded ? "무엇을 도와드릴까요?" : "PDF를 업로드하세요"}
        </h1>

        {!isPdfUploaded && (
          <div className={styles.pdfUploadContainer}>
            <input
              type="file"
              accept=".pdf"
              onChange={handlePdfUpload}
              className={styles.pdfInput}
              disabled={isLoading} // 로딩 중에는 비활성화
            />
            <p className={styles.pdfUploadText}>PDF 파일을 선택해주세요.</p>
            {uploadStatus && <p className={styles.statusText}>{uploadStatus}</p>}
          </div>
        )}

        {/* 진행률 바 */}
        {isPdfUploaded && progress < 100 && (
          <div className={styles.progressBarContainer}>
            <div
              className={styles.progressBar}
              style={{ width: `${progress}%` }}
            ></div>
            <p className={styles.progressText}>{progress}%</p>
          </div>
        )}

        {progress === 100 && chatSessionId && (
          <div className={styles.chatContainer}>
            <p className={styles.statusText}>채팅 세션이 시작되었습니다!</p>
            <ChatUI sessionId={chatSessionId} />
          </div>
        )}
      </main>
    </div>
  );
}

export default LLMForm;
