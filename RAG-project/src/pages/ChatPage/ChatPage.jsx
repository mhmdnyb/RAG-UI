import "./ChatPage.css";
import ChatInput from "../../components/ChatInput/ChatInput";
import ChatMessages from "../../components/ChatMessages/ChatMessages";
import { useEffect, useRef, useState } from "react";
function ChatPage() {
  const chatRef = useRef();
  const [data, setData] = useState([
    { text: "hello", sender: "user" },
    { text: "yo bro", sender: "bot" },
  ]);
  useEffect(() => {
    chatRef.current.scrollBy({ top: window.innerHeight, behavior: "smooth" });
  }, [data]);
  return (
    <div className="flex flex-col justify-between gap-y-1.5 h-dvh">
      <section
        className="overflow-y-auto sm:w-lg w-96 h-full mx-auto mt-4  space-y-2"
        ref={chatRef}
      >
        {data.map((message) => {
          return (
            <ChatMessages
              text={message.text}
              sender={message.sender}
            ></ChatMessages>
          );
        })}
      </section>
      <ChatInput data={data} setData={setData}></ChatInput>
    </div>
  );
}
export default ChatPage;
