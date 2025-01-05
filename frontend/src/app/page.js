import Image from "next/image";
import styles from "./page.module.css";
import LoginButton from "@/components/loginButton";

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
          <LoginButton />
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
