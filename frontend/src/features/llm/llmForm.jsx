"use client";

import React, { useState, useEffect } from "react";
import apiClient from "@/utils/axios";
import styles from "./LLMForm.module.css";
import ChatUI from "@/features/llm/chatUI";
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeRaw from 'rehype-raw';

function LLMForm() {
  const [isPdfUploaded, setIsPdfUploaded] = useState(false);
  const [uploadStatus, setUploadStatus] = useState("");
  const [progress, setProgress] = useState(0); // 진행률
  const [isLoading, setIsLoading] = useState(false);
  const [pdfId, setPdfId] = useState(null); // 업로드된 PDF ID
  const [chatSessionId, setChatSessionId] = useState(null); // 채팅 세션 ID
  const [pdfList, setPdfList] = useState([]); // 이전 PDF 목록
  const [selectedPdfId, setSelectedPdfId] = useState(null); // 선택된 PDF
  const [chatHistory, setChatHistory] = useState([]); // 선택된 PDF의 대화 내역

  useEffect(() => {
    fetchUploadedPDFs();
  }, []);

  const fetchUploadedPDFs = async () => {
    try {
      const response = await apiClient.get("/api/llmapp/uploaded_pdfs/");
      setPdfList(response.data);
    } catch (error) {
      console.error("PDF 목록 불러오기 실패:", error);
    }
  };

  const fetchChatHistory = async (pdfId) => {
    try {
      const response = await apiClient.get(`/api/llmapp/chat/history/${pdfId}/`);
      setChatHistory(response.data);
      setSelectedPdfId(pdfId);
    } catch (error) {
      console.error("대화 내역 불러오기 실패:", error);
    }
  };

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
      setUploadStatus("");

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
        fetchUploadedPDFs(); // 업로드 후 목록 갱신
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
    }, 1000);
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

        {/* 좌측: 이전 PDF 목록 */}
        <div className={styles.pdfListContainer}>
          <h2>이전 업로드된 PDF 목록</h2>
          <ul className={styles.pdfList}>
            {pdfList.map((pdf) => (
              <li
                key={pdf.id}
                onClick={() => fetchChatHistory(pdf.id)}
                className={selectedPdfId === pdf.id ? styles.selectedPdf : ""}
              >
                {decodeURI(pdf.file.split("/").pop())}
              </li>
            ))}
          </ul>
        </div>

        {/* 우측: PDF 업로드 또는 채팅 */}
        {!isPdfUploaded && (
          <div className={styles.pdfUploadContainer}>
            <input
              type="file"
              accept=".pdf"
              onChange={handlePdfUpload}
              className={styles.pdfInput}
              disabled={isLoading}
            />
            <p className={styles.pdfUploadText}>PDF 파일을 선택해주세요.</p>
            {uploadStatus && <p className={styles.statusText}>{uploadStatus}</p>}
          </div>
        )}

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

        {selectedPdfId && (
          <div className={styles.chatHistory}>
            <h3>이전 대화 내역</h3>
            {chatHistory.map((session, index) => (
              <div key={index}>
                <h4>세션 ID: {session.session_id}</h4>
                <ul>
                  {session.messages.map((msg, idx) => (
                    <li key={idx}>
                      <strong>{msg.sender}:</strong> 
                      <ReactMarkdown 
                          remarkPlugins={[remarkGfm]}
                          rehypePlugins={[rehypeRaw]}
                      
                      >
                          {msg.message}
                      </ReactMarkdown>
                    </li>
                  ))}
                </ul>
              </div>
            ))}
          </div>
        )}
      </main>
    </div>
  );
}

export default LLMForm;
