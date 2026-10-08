import "./Notification.css";
function Notification({ text, setModal }) {
  setTimeout(() => {
    setModal(false);
  }, 2500);
  return (
    <div className="text-tenpercent absolute z-10 left-1/2 top-6 bg-thirtypercent-light rounded-sm animate-notification px-5 py-2 -translate-x-1/2 flex items-center justify-center gap-x-0.5">
      <svg
        width="25px"
        height="25px"
        viewBox="0 0 24 24"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        stroke="#0efb49"
      >
        <g id="SVGRepo_bgCarrier" stroke-width="0"></g>
        <g
          id="SVGRepo_tracerCarrier"
          strokeLinecap="round"
          strokeLinejoin="round"
        ></g>
        <g id="SVGRepo_iconCarrier">
          <path
            d="M5 13.3636L8.03559 16.3204C8.42388 16.6986 9.04279 16.6986 9.43108 16.3204L19 7"
            stroke="#00aab2"
            strokeWidth="2"
            strokeLinecap="round"
            strokeLinejoin="round"
          ></path>
        </g>
      </svg>

      <p className="font-bold text-xl">{text}</p>
    </div>
  );
}
export default Notification;
