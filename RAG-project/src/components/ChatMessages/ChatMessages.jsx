import "./ChatMessages.css";
import UserProfileImage from "../../assets/placeholder.webp";
import BotProfileImage from "../../assets/bot.jpg";
import { useState } from "react";


function parseSources(rawSources) {
  if (!rawSources) return [];
  if (Array.isArray(rawSources)) return rawSources;
  if (typeof rawSources === "string") {
    try {
      const parsed = JSON.parse(rawSources);
      if (Array.isArray(parsed)) return parsed;
      if (typeof parsed === "object" && parsed !== null) return [parsed];
    } catch {
      return [];
    }
  }
  return [];
}

function formatDocumentName(doc) {
  if (!doc) return "مستند نامشخص";
  if (doc === "student_regulations.txt") return "آیین‌نامه آموزشی دانشجویان";
  if (doc === "classes.csv") return "برنامه کلاسی و دروس ارائه شده";
  if (doc === "sql_query") return "پایگاه داده آموزشی";
  return doc;
}

function ChatMessages({ message, isLatest }) {
  const isBot = message.botMessage || message.sender === "bot";
  const content = message.content || message.text || "";
  const status = message.status;
  const sources = parseSources(message.sources);
  const [sourcesOpen, setSourcesOpen] = useState(false);

  return (
    <div
      className={`w-full flex items-start gap-x-3 my-3 text-gray-100 ${
        isBot ? "flex-row" : "flex-row-reverse"
      }`}
    >
      <img
        src={isBot ? BotProfileImage : UserProfileImage}
        alt={isBot ? "دستیار دانشگاه" : "کاربر"}
        width="38"
        height="38"
        className="rounded-full ring-2 ring-tenpercent/40 shrink-0 shadow-md object-cover"
      />

      <div
        className={`max-w-[85%] sm:max-w-[78%] flex flex-col ${
          isBot ? "items-start" : "items-end"
        }`}
      >
        <div className="flex items-center gap-x-2 px-1 mb-1 text-xs text-thirtypercent-muted">
          <span className="font-semibold text-thirtypercent">
            {isBot ? "دستیار هوشمند دانشگاه" : "شما"}
          </span>
        </div>

        <div
          className={`p-3.5 rounded-2xl shadow-lg leading-relaxed text-sm whitespace-pre-wrap break-words ${
            isBot
              ? "bg-dominant-surface/90 border border-tenpercent/20 text-thirtypercent rounded-tr-sm"
              : "bg-tenpercent/20 border border-tenpercent/40 text-white rounded-tl-sm"
          }`}
          dir="rtl"
        >
          <div className="space-y-1">{content}</div>

          {!isBot && status === "PROCESSING" && isLatest && (
            <div className="mt-2.5 pt-2 border-t border-tenpercent/20 flex items-center gap-x-2 text-xs text-tenpercent animate-pulse">
              <span className="size-2 rounded-full bg-tenpercent"></span>
              <span>دستیار در حال بررسی و تدوین پاسخ است...</span>
            </div>
          )}

          {status === "FAILED" && (
            <div className="mt-2.5 pt-2 border-t border-red-500/30 flex items-center gap-x-1.5 text-xs text-red-400">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="12" cy="12" r="10" />
                <line x1="12" y1="8" x2="12" y2="12" />
                <line x1="12" y1="16" x2="12.01" y2="16" />
              </svg>
              <span>خطا در پردازش این پیام</span>
            </div>
          )}

          {isBot && sources.length > 0 && (
            <div className="mt-3 pt-2.5 border-t border-thirtypercent-muted/20">
              <button
                type="button"
                onClick={() => setSourcesOpen((prev) => !prev)}
                className="flex items-center gap-x-1.5 text-xs text-tenpercent hover:text-thirtypercent transition-colors cursor-pointer"
              >
                <svg
                  width="14"
                  height="14"
                  viewBox="0 0 24 24"
                  fill="none"
                  stroke="currentColor"
                  strokeWidth="2"
                  className={`transition-transform duration-200 ${sourcesOpen ? "rotate-180" : ""}`}
                >
                  <path d="M6 9l6 6 6-6" />
                </svg>
                <span>منابع استخراج‌شده ({sources.length} منبع)</span>
              </button>

              {sourcesOpen && (
                <div className="mt-2 space-y-1.5 bg-dominant/60 p-2.5 rounded-lg border border-tenpercent/10">
                  {sources.map((item, idx) => (
                    <div
                      key={idx}
                      className="flex items-center justify-between text-xs bg-dominant-surface/80 px-2 py-1.5 rounded border border-white/5"
                    >
                      <div className="flex items-center gap-x-1.5">
                        <svg
                          width="13"
                          height="13"
                          viewBox="0 0 24 24"
                          fill="none"
                          stroke="#00c6cf"
                          strokeWidth="2"
                        >
                          <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" />
                          <polyline points="14 2 14 8 20 8" />
                          <line x1="16" y1="13" x2="8" y2="13" />
                          <line x1="16" y1="17" x2="8" y2="17" />
                        </svg>
                        <span className="text-thirtypercent font-medium">
                          {formatDocumentName(item.document)}
                        </span>
                      </div>
                      {item.page != null && (
                        <span className="text-[11px] bg-tenpercent/20 text-tenpercent px-1.5 py-0.5 rounded font-mono">
                          صفحه {item.page}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default ChatMessages;
