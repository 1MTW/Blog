"use client";

import { useState, useEffect } from "react";
import apiClient from "@/utils/axios";

function AuthStatus({ onStatusChange }) {
  const [isLoggedIn, setIsLoggedIn] = useState(null); // 초기값을 null로 설정

  useEffect(() => {
    const checkLoginStatus = async () => {
      try {
        const response = await apiClient.get("/api/accountapp/me/");
        const loggedIn = response.status === 200;
        setIsLoggedIn(loggedIn);
        onStatusChange(loggedIn); // 상태 변경 시 부모에게 알림
      } catch (error) {
        setIsLoggedIn(false);
        onStatusChange(false); // 상태 변경 시 부모에게 알림
      }
    };

    checkLoginStatus();
  }, [onStatusChange]);

  if (isLoggedIn === null) {
    return <div>Loading...</div>; // 로딩 중 상태
  }

  return null; // 상태만 업데이트하고 렌더링은 하지 않음
}

export default AuthStatus;
