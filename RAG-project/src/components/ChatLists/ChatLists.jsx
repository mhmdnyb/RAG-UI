import { useChat } from "../../context/useChat";
import Loading from "../Loading/Loading";

function formatDate(dateString) {
  if (!dateString) return "";
  try {
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    return new Intl.DateTimeFormat("fa-IR", {
      month: "short",
      day: "numeric",
    }).format(date);
  } catch {
    return dateString;
  }
}

function ChatLists() {
  const {
    conversations,
    activeConversationId,
    selectConversation,
    deleteConversation,
    isLoadingConversations,
  } = useChat();

  if (isLoadingConversations) {
    return (
      <div className="w-full py-8 flex flex-col items-center justify-center gap-y-2 text-thirtypercent-muted text-sm">
        <Loading />
        <span>در حال بارگذاری گفتگوها...</span>
      </div>
    );
  }

  if (!conversations || conversations.length === 0) {
    return (
      <div className="w-full py-8 text-center text-thirtypercent-muted text-xs px-2">
        گفتگویی وجود ندارد. روی «گفتگوی جدید» کلیک کنید.
      </div>
    );
  }

  return (
    <div className="w-full space-y-1.5 overflow-y-auto px-1 py-1">
      {conversations.map((chat, index) => {
        const id = chat.conversationId || chat.id;
        const isActive = id === activeConversationId;
        const displayName = chat.name || "گفتگوی بدون عنوان";
        const dateDisplay = formatDate(chat.createdAt);

        return (
          <div
            key={id || `chat-${index}`}
            onClick={() => id && selectConversation(id)}
            className={`group relative w-full flex items-center justify-between p-2.5 rounded-lg cursor-pointer transition-all duration-150 border ${
              isActive
                ? "bg-tenpercent/20 border-tenpercent text-thirtypercent shadow-md"
                : "bg-dominant/40 border-white/10 text-thirtypercent-muted hover:bg-dominant-surface hover:text-thirtypercent"
            }`}
          >
            <div className="flex items-center gap-x-2.5 overflow-hidden">
              <svg
                width="16"
                height="16"
                viewBox="0 0 24 24"
                fill="none"
                stroke="currentColor"
                strokeWidth="2"
                className={`shrink-0 ${isActive ? "text-tenpercent" : "text-thirtypercent-muted"}`}
              >
                <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
              </svg>
              <div className="truncate text-sm font-medium">
                {displayName}
              </div>
            </div>

            <div className="flex items-center gap-x-1 shrink-0">
              {dateDisplay && (
                <span className="text-[11px] text-thirtypercent-muted/70 group-hover:hidden">
                  {dateDisplay}
                </span>
              )}
              {id && (
                <button
                  type="button"
                  title="حذف گفتگو"
                  onClick={(e) => {
                    e.stopPropagation();
                    if (window.confirm("آیا از حذف این گفتگو اطمینان دارید؟")) {
                      deleteConversation(id);
                    }
                  }}
                  className="opacity-70 md:opacity-0 md:group-hover:opacity-100 p-1 rounded hover:bg-red-500/20 hover:text-red-400 transition-opacity cursor-pointer"
                >
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="3 6 5 6 21 6" />
                    <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default ChatLists;
