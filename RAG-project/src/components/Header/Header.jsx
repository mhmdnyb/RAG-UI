import { useState } from "react";
import "./Header.css";
function Header() {
  const [show, setShow] = useState(false);
  function handleShow() {
    if (show) {
      setShow(false);
    } else {
      setShow(true);
    }
  }
  return (
    <div
      className="w-full h-10 bg-linear-to-br from-thirtypercent to-thirtypercent-muted rounded-b-sm backdrop-blur-2xl border border-white/30 relative"
      dir="ltr"
    >
      {show && (
        <div className="absolute z-10 -left-1 -top-1 h-dvh w-50 bg-dominant-surface backdrop-blur-2xl rounded-r-sm animate-sidebar border border-tenpercent-dark/30"></div>
      )}
      {show ? (
        <svg
          className="ml-auto"
          onClick={() => {
            handleShow();
          }}
          width="30px"
          height="30px"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
          <g
            id="SVGRepo_tracerCarrier"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></g>
          <g id="SVGRepo_iconCarrier">
            {" "}
            <path
              d="M6 6L18 18"
              stroke="#00aab2"
              strokeLinecap="round"
            ></path>{" "}
            <path
              d="M18 6L6.00001 18"
              stroke="#00aab2"
              strokeLinecap="round"
            ></path>{" "}
          </g>
        </svg>
      ) : (
        <svg
          className="ml-auto"
          onClick={() => {
            handleShow();
          }}
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
          width="30px"
          height="30px"
        >
          <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
          <g
            id="SVGRepo_tracerCarrier"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></g>
          <g id="SVGRepo_iconCarrier">
            {" "}
            <path
              d="M20 7L4 7"
              stroke="#00aab2"
              stroke-width="1.5"
              strokeLinecap="round"
            ></path>{" "}
            <path
              d="M20 12L4 12"
              stroke="#00aab2"
              strokeWidth="1.5"
              strokeLinecap="round"
            ></path>{" "}
            <path
              d="M20 17L4 17"
              stroke="#00aab2"
              strokeWidth="1.5"
              strokeLinecap="round"
            ></path>{" "}
          </g>
        </svg>
      )}
    </div>
  );
}
export default Header;
