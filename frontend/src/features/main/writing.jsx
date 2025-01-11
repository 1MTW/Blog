"use client";

import React, { useState, useEffect } from "react";
import apiClient from "@/utils/axios";
import "./writing.css";

function Writing({ post, onSuccess, onCancel}) {
  const [title, setTitle] = useState("");
  const [content, setContent] = useState("");
  const [category_name, setCategoryName] = useState("");

  useEffect(() => {
    if (post) {
      setTitle(post.title || ""); 
      setContent(post.content || ""); 
      setCategoryName(post.category_name || ""); 
    }
  }, [post]);

  const sendPost = async () => {
    if (!title.trim() || !content.trim()) {
      alert("제목과 내용을 모두 입력해주세요.");
      return;
    }
    try {
      if (post) {
        // 수정 모드
        await apiClient.put(`/api/blog/search/${post.id}/`, {
          title,
          content,
          category_name,
        });
        alert("포스팅이 성공적으로 수정되었습니다!");
      } else {
        // 새 글쓰기 모드
        await apiClient.post(`/api/blog/post/`, {
          title,
          content,
          category_name,
        });
        alert("포스팅이 성공적으로 업로드되었습니다!");
      }
      setTitle("");
      setContent("");
      setCategoryName("");
      if (onSuccess){
        onSuccess();
      }
    } catch (error) {
      console.error("포스팅 처리 실패:", error);
      alert("작업 중 오류가 발생했습니다. 다시 시도해주세요.");
    }
  };

  return (
    <div className="writing-container">
      <div className="input-group">
        <input
          type="text"
          value={title}
          onChange={(e) => setTitle(e.target.value)}
          placeholder="블로그 제목을 입력하세요..."
          className="title-input"
        />
      </div>
      <div className="input-group">
        <input
          type="text"
          value={category_name}
          onChange={(e) => setCategoryName(e.target.value)}
          placeholder="카테고리를 입력하세요"
          className="category-input"
        />
      </div>
      <div className="textarea-group">
        <textarea
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder="게시물을 입력하세요..."
          className="content-textarea"
        />
      </div>
      <button onClick={sendPost} className="send-button">
        보내기
      </button>
      <button onClick={onCancel}>취소</button>
    </div>
  );
}

export default Writing;
