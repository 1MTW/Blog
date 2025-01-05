"use client";

import apiClient from "@/utils/axios";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import styles from "./NavForm.module.css";
``
function NavForm() {
    const [userEmail, setUserEmail] = useState("");
    const router = useRouter();

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await apiClient.get("/api/accountapp/me/");
                setUserEmail(response.data.email);
            } catch (error) {
                // 예상된 에러는 무시
                if (error.response && error.response.status === 401) {
                    // 401 Unauthorized: 로그아웃된 상태
                    setUserEmail("");
                } else {
                    // 그 외 에러는 콘솔에 출력
                    console.error("Failed to fetch user info:", error);
                }
            }
        };

        fetchUserInfo();
    }, [router]);

    const handleLogout = async () => {
        try {
            await apiClient.post("/api/accountapp/auth/logout/");
            setUserEmail("");
            window.location.reload();
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };

    return (
        <div className={styles.navContainer}>
            <div className={styles.navWrapper}>
                <span>{userEmail ? userEmail : "You have to login."}</span>
                {userEmail && (
                    <button  className={styles.navButton} onClick={handleLogout}>
                        Logout
                    </button>
                )}
            </div>
        </div>
    );
}

export default NavForm;
