"use client";

import { useState } from "react";
import AuthStatus from "@/utils/authStatus";
import Image from "next/image";
import styles from "@/app/page.module.css";

function LoginButton() {
  const [isLoggedIn, setIsLoggedIn] = useState(false);

  return (
    <>
      {/* AuthStatus가 상태를 업데이트 */}
      <AuthStatus onStatusChange={setIsLoggedIn} />
      <a
        className={styles.primary}
        href={
          isLoggedIn
            ? "/llm" // 로그인 상태일 때
            : "http://localhost:8000/api/accountapp/auth/login/?next=http://localhost:3000/llm" // 비로그인 상태일 때
        }
        target={isLoggedIn ? "_self" : "_blank"}
        rel="noopener noreferrer"
      >
        <Image
          className={styles.logo}
          src="/vercel.svg"
          alt="Vercel logomark"
          width={20}
          height={20}
        />
        {isLoggedIn ? "Start Chat" : "Google Login"}
      </a>
    </>
  );
}

export default LoginButton;
