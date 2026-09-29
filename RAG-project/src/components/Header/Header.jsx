import { useState } from "react";
import "./Header.css";
import Sidebar from "../Sidebar/Sidebar";
function Header() {
  const [show, setShow] = useState(false);

  function handleShow() {
    setShow((prev) => !prev);
  }

  return (
    <header
      className="w-full h-10 bg-linear-to-br from-thirtypercent to-thirtypercent-muted rounded-b-sm backdrop-blur-2xl border border-white/30 relative z-30 flex items-center px-2"
      dir="ltr"
    >
      <button
        onClick={handleShow}
        className="ml-auto relative z-50 p-1 cursor-pointer flex items-center justify-center"
      >
        {show ? (
          <svg
            width="24px"
            height="24px"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M6 6L18 18M18 6L6 18"
              stroke="#00aab2"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        ) : (
          <svg
            width="24px"
            height="24px"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M4 7H20M4 12H20M4 17H20"
              stroke="#00aab2"
              strokeWidth="2"
              strokeLinecap="round"
            />
          </svg>
        )}
      </button>

      {show && <Sidebar></Sidebar>}
    </header>
  );
}

export default Header;
