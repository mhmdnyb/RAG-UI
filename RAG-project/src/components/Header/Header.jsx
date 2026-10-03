import "./Header.css";
import Sidebar from "../Sidebar/Sidebar";
import { useChat } from "../../context/useChat";
import uscLogo from "../../assets/usc.png";

function Header() {
  const {
    sidebarOpen,
    setSidebarOpen,
    activeConversation,
    createConversation,
    wsConnected,
  } = useChat();

  return (
    <>
      <header
        className="w-full h-14 bg-dominant-surface/90 backdrop-blur-xl border-b border-white/10 relative z-30 flex items-center justify-between px-4 text-thirtypercent"
        dir="rtl"
      >
        <div className="flex items-center gap-x-3">
          <button
            type="button"
            onClick={() => setSidebarOpen((prev) => !prev)}
            className="p-2 rounded-lg hover:bg-white/10 text-thirtypercent transition-colors cursor-pointer"
            title="منوی گفتگوها"
          >
            <svg
              width="22px"
              height="22px"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M4 7H20M4 12H20M4 17H20"
                stroke="#00c6cf"
                strokeWidth="2"
                strokeLinecap="round"
              />
            </svg>
          </button>

          <div className="flex items-center gap-x-2">
            <img
              src={uscLogo}
              alt="لوگوی دانشگاه"
              className="h-7 object-contain"
            />
            <span className="font-semibold text-sm hidden sm:inline">
              دستیار هوشمند دانشگاه علم و فرهنگ
            </span>
          </div>
        </div>

        <div className="flex items-center gap-x-2">
          {activeConversation?.name && (
            <span className="text-xs text-thirtypercent-muted max-w-[140px] sm:max-w-xs truncate">
              {activeConversation.name}
            </span>
          )}

          <button
            type="button"
            onClick={createConversation}
            className="flex items-center gap-x-1 bg-tenpercent/20 hover:bg-tenpercent/30 text-tenpercent border border-tenpercent/40 px-2.5 py-1 rounded-md text-xs transition-colors cursor-pointer"
          >
            <svg
              width="14"
              height="14"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2.5"
            >
              <line x1="12" y1="5" x2="12" y2="19" />
              <line x1="5" y1="12" x2="19" y2="12" />
            </svg>
            <span>گفتگوی جدید</span>
          </button>
        </div>
      </header>

      {sidebarOpen && (
        <>
          <div
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/50 backdrop-blur-xs z-30 transition-opacity"
          />
          <Sidebar />
        </>
      )}
    </>
  );
}

export default Header;
