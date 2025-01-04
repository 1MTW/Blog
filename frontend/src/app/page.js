import Image from "next/image";
import styles from "./page.module.css";

export default function Home() {
  return (
    <div className={styles.page}>
      <main className={styles.main}>
        <h1 style={{fontSize: "2.5rem"}}>ExactLLM</h1>
        <ol>
          <li>
            Upload PDF.
          </li>
          <li>Chat with your PDF and get exact information.</li>
        </ol>

        <div className={styles.ctas}>
          <a
            className={styles.primary}
            href="http://localhost:8000/api/accountapp/auth/login/?next=http://localhost:3000/llm"
            target="_blank"
            rel="noopener noreferrer"
          >
            <Image
              className={styles.logo}
              src="/vercel.svg"
              alt="Vercel logomark"
              width={20}
              height={20}
            />
            Google Login
          </a>
          <a
            href="https://github.com/Aiden-Kwak"
            target="_blank"
            rel="noopener noreferrer"
            className={styles.secondary}
          >
            My Github
          </a>
        </div>
      </main>
    </div>
  );
}
