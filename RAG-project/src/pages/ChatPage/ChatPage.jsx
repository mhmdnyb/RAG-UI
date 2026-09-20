import "./ChatPage.css";
import ChatInput from "../../components/ChatInput/ChatInput";
import ChatMessages from "../../components/ChatMessages/ChatMessages";
import { useEffect, useRef, useState } from "react";
import Header from "../../components/Header/Header";
function ChatPage() {
  const chatRef = useRef();
  const [data, setData] = useState([
    { text: "hello", sender: "user", id: 1 },
    { text: "yo bro", sender: "bot", id: 2 },
  ]);
  useEffect(() => {
    chatRef.current.scrollBy({ top: window.innerHeight, behavior: "smooth" });
  }, [data]);
  return (
    <div className="flex flex-col justify-between gap-y-1.5 h-dvh overflow-hidden relative z-10">
      <title>Chat</title>
      <Header></Header>
      <section
        dir="ltr"
        className="overflow-y-auto sm:w-lg min-w-85 h-full mx-auto px-1.5 mt-4  space-y-2"
        ref={chatRef}
      >
        {data.map((message) => {
          return (
            <ChatMessages
              text={message.text}
              sender={message.sender}
              key={message.id}
            ></ChatMessages>
          );
        })}
      </section>
      <ChatInput data={data} setData={setData}></ChatInput>
    </div>
  );
}
export default ChatPage;
