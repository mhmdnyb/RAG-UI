import "./ChatInput.css";
import { useState, useRef } from "react";
import { useChat } from "../../context/useChat";

function ChatInput() {
  const [text, setText] = useState("");
  const { sendMessage, isSending } = useChat();
  const inputRef = useRef(null);

  function handleSend() {
    const trimmed = text.trim();
    if (!trimmed || isSending) return;
    sendMessage(trimmed);
    setText("");
    if (inputRef.current) {
      inputRef.current.focus();
    }
  }

  function handleKeyDown(e) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  }

  return (
    <div className="w-full max-w-3xl mx-auto px-4 pb-4 pt-2">
      <div className="relative flex items-center bg-dominant-surface/90 border border-thirtypercent/20 focus-within:border-tenpercent focus-within:ring-2 focus-within:ring-tenpercent/30 transition-all rounded-xl shadow-xl backdrop-blur-md px-3 py-2">
        <input
          ref={inputRef}
          type="text"
          name="message"
          id="message"
          dir="rtl"
          value={text}
          onChange={(e) => setText(e.target.value)}
          onKeyDown={handleKeyDown}
          disabled={isSending}
          placeholder="سوال خود درباره آیین‌نامه‌ها، قوانین یا برنامه‌های کلاسی را بپرسید..."
          className="w-full bg-transparent text-thirtypercent placeholder-thirtypercent-muted/50 focus:outline-none text-sm py-1.5 px-2 disabled:opacity-50"
        />

        <button
          type="button"
          onClick={handleSend}
          disabled={!text.trim() || isSending}
          title="ارسال پیام"
          className="shrink-0 p-2 rounded-lg bg-tenpercent text-dominant hover:bg-tenpercent-dark disabled:opacity-40 disabled:hover:bg-tenpercent disabled:cursor-not-allowed transition-all duration-200 shadow-sm active:scale-95 cursor-pointer flex items-center justify-center"
        >
          {isSending ? (
            <div className="size-5 rounded-full border-2 border-dominant border-r-transparent animate-spin" />
          ) : (
            <svg
              className="size-5 transition-transform duration-200 rotate-180"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                fillRule="evenodd"
                clipRule="evenodd"
                d="M3.3938 2.20468C3.70395 1.96828 4.12324 1.93374 4.4679 2.1162L21.4679 11.1162C21.7953 11.2895 22 11.6296 22 12C22 12.3704 21.7953 12.7105 21.4679 12.8838L4.4679 21.8838C4.12324 22.0662 3.70395 22.0317 3.3938 21.7953C3.08365 21.5589 2.93922 21.1637 3.02382 20.7831L4.97561 12L3.02382 3.21692C2.93922 2.83623 3.08365 2.44109 3.3938 2.20468ZM6.80218 13L5.44596 19.103L16.9739 13H6.80218ZM16.9739 11H6.80218L5.44596 4.89699L16.9739 11Z"
                fill="currentColor"
              />
            </svg>
          )}
        </button>
      </div>
    </div>
  );
}

export default ChatInput;
