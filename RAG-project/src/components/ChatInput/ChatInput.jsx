import "./ChatInput.css";
function ChatInput() {
  return (
    <>
      <title>Chat</title>
      <div className="sm:w-md w-90 h-12 ring-1 ring-white/50 has-focus:ring-white/60 has-focus:ring-2 transition-all rounded-md text-gray-100 flex items-center bg-linear-to-bl from-black/30 to-black/10 backdrop-blur-2xl shadow-2xs shadow-white/30 mx-auto mb-20 duration-100">
        <input
          type="text"
          name="message"
          id="message"
          className="w-full rounded-md focus:outline-0 py-2 pl-1.5"
          placeholder={"Ask"}
        />
        <svg
          className="mr-1.5 cursor-pointer opacity-80 active:opacity-100 transition-opacity"
          width="30px"
          height="30px"
          viewBox="0 0 24 24"
          fill="none"
          xmlns="http://www.w3.org/2000/svg"
        >
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M3.3938 2.20468C3.70395 1.96828 4.12324 1.93374 4.4679 2.1162L21.4679 11.1162C21.7953 11.2895 22 11.6296 22 12C22 12.3704 21.7953 12.7105 21.4679 12.8838L4.4679 21.8838C4.12324 22.0662 3.70395 22.0317 3.3938 21.7953C3.08365 21.5589 2.93922 21.1637 3.02382 20.7831L4.97561 12L3.02382 3.21692C2.93922 2.83623 3.08365 2.44109 3.3938 2.20468ZM6.80218 13L5.44596 19.103L16.9739 13H6.80218ZM16.9739 11H6.80218L5.44596 4.89699L16.9739 11Z"
            fill="#fff"
          />
        </svg>
      </div>
    </>
  );
}
export default ChatInput;
