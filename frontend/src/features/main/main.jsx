"use client";

import React, { useState, useEffect } from "react";
import apiClient from "@/utils/axios";
import Writing from "@/features/main/writing";
import "./main.css";

function Main() {
  const [categories, setCategories] = useState([]); // 카테고리 목록
  const [posts, setPosts] = useState([]); // 전체 포스팅
  const [filteredPosts, setFilteredPosts] = useState([]); // 필터링된 포스팅
  const [selectedCategory, setSelectedCategory] = useState(null); // 선택된 카테고리
  const [isWriting, setIsWriting] = useState(false); // 글쓰기 상태
  const [selectedPost, setSelectedPost] = useState(null); // 선택된 포스트

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await apiClient.get("/api/blog/history/");
      
      // 고유한 category_name 목록 추출
      const categories = [...new Set(response.data.map((item) => item.category_name))];
      const posts = response.data;
  
      setCategories(categories); // 고유한 카테고리 이름 목록 저장
      setPosts(posts);           // 전체 포스트 저장
      setFilteredPosts(posts);   // 초기 필터링된 포스트 설정
    } catch (error) {
      console.error("블로그 히스토리 불러오기 실패:", error);
    }
  };

  const handleAddCategory = async (e) => {
    e.preventDefault(); // 페이지 리로드 방지
    const newCategory = e.target.elements.category.value.trim(); // 입력 값 가져오기

    if (!newCategory) {
      alert("카테고리 이름을 입력해주세요.");
      return;
    }

    if (categories.includes(newCategory)) {
      alert("이미 존재하는 카테고리입니다.");
      return;
    }

    try {
      const response = await apiClient.post("/api/blog/category/create/", {
        category: newCategory,
      });

      if (response.status === 201) {
        setCategories([...categories, newCategory]); // 새 카테고리 추가
        e.target.reset(); // 입력 필드 초기화
      } else {
        alert("카테고리 추가 중 문제가 발생했습니다.");
      }
    } catch (error) {
      console.error("카테고리 추가 실패:", error);
      alert("카테고리 추가에 실패했습니다. 다시 시도해주세요.");
    }
  };

  const handleCategoryClick = (category) => {
    setSelectedCategory(category);
    if (category) {
      setFilteredPosts(posts.filter((post) => post.category_name === category));
    } else {
      setFilteredPosts(posts);
    }
  };

  const handleWritingClick = () => {
    setIsWriting(true);
    setSelectedPost(null); // 글쓰기 모드로 전환 시 선택된 포스트 초기화
  };

  const handlePostClick = (post) => {
    setSelectedPost(post); // 선택된 포스트 설정
    setIsWriting(false); // 글쓰기 모드에서 나가기
  };

  const handleRefiningClick = () => {
    if (selectedPost) {
      setIsWriting(true);
    }
  };

  return (
    <div className="main-container">
      <div className="category-container">
        <h2>Categories</h2>
        {categories && categories.length > 0 ? (
          <ul className="category-list">
            {categories.map((category) => (
              <li
                key={category}
                onClick={() => handleCategoryClick(category)}
                className="category-item"
              >
                {category}
              </li>
            ))}
          </ul>
        ) : (
          <p>No categories available.</p>
        )}
        <form onSubmit={handleAddCategory} className="category-form">
          <input
            type="text"
            name="category"
            placeholder="새 카테고리를 입력하세요"
            className="category-input"
          />
          <button type="submit" className="category-button">추가</button>
        </form>
      </div>

      {isWriting ? (
        <Writing
          post={selectedPost}
          onSuccess={() => {
            setIsWriting(false);
            fetchHistory(); // 목록 갱신
          }}
          onCancel={() => setIsWriting(false)}
        />
      ) : selectedPost ? (
        <div className="post-container">
          <h1>{selectedPost.title}</h1>
          <p>{selectedPost.content}</p>
          <button
            onClick={() => setSelectedPost(null)}
            className="back-button"
          >
            뒤로 가기
          </button>
          <button onClick={handleRefiningClick} className="edit-button">
            수정
          </button>
        </div>
      ) : (
        <div className="post-list">
          <h1>Blog Posts</h1>
          <button onClick={handleWritingClick} className="create-post-button">
            포스트 생성
          </button>
          {filteredPosts && filteredPosts.length > 0 ? (
            filteredPosts.map((post) => (
              <div
                key={post.id}
                onClick={() => handlePostClick(post)}
                className="post-preview"
              >
                <h3>{post.title}</h3>
                <p>{post.content.substring(0, 100)}...</p>
              </div>
            ))
          ) : (
            <p>No posts available for the selected category.</p>
          )}
        </div>
      )}
    </div>
  );
}

export default Main;