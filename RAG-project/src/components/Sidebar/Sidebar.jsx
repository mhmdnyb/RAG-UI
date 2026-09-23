import "./Sidebar.css";
import { Suspense } from "react";
import ChatLists from "../ChatLists/ChatLists";
import Loading from "../Loading/Loading";
function Sidebar() {
  return (
    <aside className="fixed inset-y-0 -left-0.5 -top-1 z-40 h-dvh sm:w-60 w-50 bg-dominant-surface backdrop-blur-2xl rounded-r-sm animate-sidebar border-r border-tenpercent-dark/30 shadow-xl">
      <Suspense
        fallback={
          <div className="w-full h-full flex items-center justify-center">
            <Loading></Loading>
          </div>
        }
      >
        <ChatLists></ChatLists>
      </Suspense>
    </aside>
  );
}
export default Sidebar;
