import "./ChatPage.css";
import ChatInput from "../../components/ChatInput/ChatInput";
import ChatMessages from "../../components/ChatMessages/ChatMessages";
import Header from "../../components/Header/Header";
import Loading from "../../components/Loading/Loading";
import { ChatProvider } from "../../context/ChatContext";
import { useChat } from "../../context/useChat";
import { useEffect, useRef } from "react";
import uscLogo from "../../assets/usc.png";

function ChatContent() {
  const chatRef = useRef(null);
  const {
    messages,
    isLoadingMessages,
    activeConversationId,
    createConversation,
    sendMessage,
    isSending,
  } = useChat();

  useEffect(() => {
    if (chatRef.current) {
      chatRef.current.scrollTo({
        top: chatRef.current.scrollHeight,
        behavior: "smooth",
      });
    }
  }, [messages, isSending]);

  const quickPrompts = [
    "شرایط مشروطی و حداقل معدل قبولی چیست؟",
    "سقف مجاز انتخاب واحد در هر نیم‌سال چقدر است؟",
    "نحوه حذف و اضافه و مهلت‌های آموزشی چگونه است؟",
    "برنامه کلاسی و اساتید دروس ارائه شده این ترم",
  ];

  return (
    <div className="flex flex-col h-dvh overflow-hidden bg-dominant text-thirtypercent">
      <title>گفتگو با دستیار هوشمند دانشگاه علم و فرهنگ</title>
      <Header />

      <main
        ref={chatRef}
        className="flex-1 overflow-y-auto px-4 py-4 w-full max-w-4xl mx-auto"
        dir="rtl"
      >
        {isLoadingMessages ? (
          <div className="h-full flex flex-col items-center justify-center gap-y-2 text-thirtypercent-muted">
            <Loading />
            <span className="text-sm">در حال دریافت تاریخچه پیام‌ها...</span>
          </div>
        ) : !activeConversationId ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-md mx-auto space-y-4">
            <img src={uscLogo} alt="لوگوی دانشگاه" className="h-20 object-contain opacity-80" />
            <h2 className="text-xl font-semibold text-thirtypercent">به دستیار دانشگاه خوش آمدید</h2>
            <p className="text-sm text-thirtypercent-muted leading-relaxed">
              برای شروع پرسش و پاسخ پیرامون آیین‌نامه‌ها، قوانین و برنامه‌های کلاسی، یک گفتگوی جدید ایجاد کنید.
            </p>
            <button
              type="button"
              onClick={createConversation}
              className="bg-tenpercent hover:bg-tenpercent-dark text-dominant font-semibold py-2 px-6 rounded-lg transition-all shadow-md active:scale-95 cursor-pointer text-sm"
            >
              شروع گفتگوی جدید
            </button>
          </div>
        ) : messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-lg mx-auto space-y-6">
            <div className="space-y-2">
              <img src={uscLogo} alt="لوگوی دانشگاه" className="h-16 object-contain mx-auto opacity-90" />
              <h2 className="text-lg font-semibold text-thirtypercent">
                دستیار هوشمند دانشگاه علم و فرهنگ
              </h2>
              <p className="text-xs text-thirtypercent-muted leading-relaxed">
                من می‌توانم با استناد به اسناد رسمی، آیین‌نامه‌های دانشجویی و برنامه‌های کلاسی دانشگاه به پرسش‌های شما پاسخ دهم.
              </p>
            </div>

            <div className="w-full space-y-2">
              <div className="text-xs text-thirtypercent-muted text-right font-medium">
                پرسش‌های متداول برای شروع:
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-right">
                {quickPrompts.map((prompt, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => sendMessage(prompt)}
                    className="p-2.5 rounded-lg bg-dominant-surface/80 border border-tenpercent/20 hover:border-tenpercent/50 text-thirtypercent hover:text-white text-xs leading-relaxed transition-all cursor-pointer text-right active:scale-95"
                  >
                    {prompt}
                  </button>
                ))}
              </div>
            </div>
          </div>
        ) : (
          <div className="space-y-3 pb-2">
            {messages.map((msg, index) => (
              <ChatMessages
                key={msg.messageId || msg.tempId || index}
                message={msg}
                isLatest={index === messages.length - 1}
              />
            ))}
          </div>
        )}
      </main>

      <ChatInput />
    </div>
  );
}

function ChatPage() {
  return (
    <ChatProvider>
      <ChatContent />
    </ChatProvider>
  );
}

export default ChatPage;
