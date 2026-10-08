import "./Sidebar.css";
import ChatLists from "../ChatLists/ChatLists";
import { useChat } from "../../context/useChat";
import { useAuth } from "../../context/useAuth";
import uscLogo from "../../assets/usc.png";

function Sidebar() {
  const { createConversation, setSidebarOpen } = useChat();
  const { user, logout } = useAuth();

  return (
    <aside className="fixed inset-y-0 right-0 z-40 h-dvh w-72 bg-dominant-surface/95 backdrop-blur-2xl border-l border-tenpercent/20 shadow-2xl flex flex-col justify-between p-3 animate-sidebar">
      <div className="flex flex-col gap-y-3 overflow-hidden">
        <div className="flex items-center justify-between pb-2 border-b border-white/10">
          <div className="flex items-center gap-x-2">
            <img src={uscLogo} alt="USC Logo" className="h-8 object-contain" />
            <span className="text-sm font-semibold text-thirtypercent">
              دستیار هوشمند دانشگاه
            </span>
          </div>
          <button
            type="button"
            onClick={() => setSidebarOpen(false)}
            className="p-1 rounded-md text-thirtypercent-muted hover:text-white hover:bg-white/10 transition-colors"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>

        <button
          type="button"
          onClick={createConversation}
          className="w-full flex items-center justify-center gap-x-2 bg-tenpercent/15 hover:bg-tenpercent/25 text-tenpercent border border-tenpercent/30 hover:border-tenpercent font-medium py-2 px-3 rounded-lg transition-all duration-150 shadow-sm active:scale-95 cursor-pointer"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
          >
            <line x1="12" y1="5" x2="12" y2="19" />
            <line x1="5" y1="12" x2="19" y2="12" />
          </svg>
          <span className="text-sm">گفتگوی جدید</span>
        </button>

        <div className="flex-1 overflow-y-auto">
          <ChatLists />
        </div>
      </div>

      <div className="pt-3 border-t border-white/10 flex items-center justify-between">
        <div className="flex items-center gap-x-2 overflow-hidden">
          <div className="size-8 rounded-full bg-tenpercent/20 border border-tenpercent/40 flex items-center justify-center text-tenpercent font-semibold text-xs shrink-0"></div>
          <div className="truncate text-xs">
            <div className="text-thirtypercent font-medium truncate"></div>
            <div
              className="text-thirtypercent-muted text-[11px] truncate"
              dir="ltr"
            >
              {user?.phoneNumber || ""}
            </div>
          </div>
        </div>

        <button
          type="button"
          onClick={logout}
          title="خروج از حساب"
          className="p-1.5 rounded-lg text-red-400 hover:bg-red-500/10 hover:text-red-300 transition-colors cursor-pointer"
        >
          <svg
            width="18"
            height="18"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
            <polyline points="16 17 21 12 16 7" />
            <line x1="21" y1="12" x2="9" y2="12" />
          </svg>
        </button>
      </div>
    </aside>
  );
}

export default Sidebar;
