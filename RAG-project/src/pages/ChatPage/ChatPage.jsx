import "./ChatPage.css";
import ChatInput from "../../components/ChatInput/ChatInput";
import ChatMessages from "../../components/ChatMessages/ChatMessages";
function ChatPage() {
  return (
    <div className="flex flex-col justify-between h-dvh">
      <section className="overflow-y-auto sm:w-lg w-96 h-full mx-auto mt-4  space-y-2">
        <ChatMessages text={"hello"} sender={"user"}></ChatMessages>
        <ChatMessages text={"hello"} sender={"bot"}></ChatMessages>
      </section>
      <ChatInput></ChatInput>
    </div>
  );
}
export default ChatPage;
