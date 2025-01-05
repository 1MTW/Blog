"use client";

import React, { useState, useEffect } from "react";
import apiClient from "@/utils/axios";
import styles from "./LLMForm.module.css";

function LLMForm() {
  const [isPdfUploaded, setIsPdfUploaded] = useState(false); // PDF 업로드 상태
  const [uploadStatus, setUploadStatus] = useState(""); // 업로드 상태 메시지
  const [progress, setProgress] = useState(0); // 진행률
  const [isLoading, setIsLoading] = useState(false); // 로딩 상태
  const [pdfId, setPdfId] = useState(null); // 업로드된 PDF ID

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
        setPdfId(response.data.id); // 업로드된 PDF ID 저장
        pollProgress(response.data.id); // 진행률 확인 시작
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
        }
      } catch (error) {
        console.error("진행률 확인 실패:", error);
        clearInterval(interval);
      }
    }, 1000); // 1초 간격으로 진행률 확인
  };

  return (
    <div className={styles.container}>
      {/* Main Content */}
      <main className={styles.main}>
        <h1 className={styles.header}>
          {isPdfUploaded ? "무엇을 도와드릴까요?" : "PDF를 업로드하세요"}
        </h1>

        {/* PDF Upload Input */}
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

        {/* PDF 처리 완료 */}
        {progress === 100 && <p className={styles.statusText}>처리가 완료되었습니다!</p>}
      </main>
    </div>
  );
}

export default LLMForm;
