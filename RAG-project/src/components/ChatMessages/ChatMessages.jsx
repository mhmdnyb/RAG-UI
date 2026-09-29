import "./ChatMessages.jsx";
import UserProfileImage from "../../assets/placeholder.webp";
import BotProfileImage from "../../assets/bot.jpg";
function ChatMessages({ text, sender }) {
  return (
    <div
      className={`text-gray-100 flex items-center ${sender === "bot" ? "justify-start" : "justify-end"}`}
    >
      <img
        src={sender == "bot" ? BotProfileImage : UserProfileImage}
        alt="userImage"
        width="42"
        height="42"
        className={`rounded-full outline-1 outline-gray-300 ${sender == "bot" ? "order-1" : "order-2"}`}
      />
      <p
        className={`bg-slate-500 p-2 rounded-lg mx-1.5 ${sender == "bot" ? "order-2" : "order-1"}`}
      >
        {text}
      </p>
    </div>
  );
}
export default ChatMessages;
