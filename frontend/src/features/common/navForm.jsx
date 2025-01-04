"use client";

import apiClient from "@/utils/axios";
import React, { useState, useEffect } from "react";
import { useRouter } from "next/navigation";

function NavForm() {
    const [userEmail, setUserEmail] = useState("");
    const router = useRouter();

    useEffect(() => {
        const fetchUserInfo = async () => {
            try {
                const response = await apiClient.get("/api/accountapp/me/");
                setUserEmail(response.data.email);
            } catch (error) {
                setUserEmail("");
            }
        };

        fetchUserInfo();
    }, [router]);

    const handleLogout = async () => {
        try {
            await apiClient.post("/api/accountapp/auth/logout/");
            setUserEmail("");
            router.push("/");
        } catch (error) {
            console.error("Logout failed:", error);
        }
    };

    return (
        <div className="nav-container">
            <div className="nav-wrapper">
                <span>{userEmail ? userEmail : "You have to login."}</span>
                {userEmail && <button onClick={handleLogout}>Logout</button>}
            </div>
        </div>
    );
}

export default NavForm;
