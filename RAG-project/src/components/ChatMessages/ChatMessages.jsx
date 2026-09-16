import "./ChatMessages.jsx";
import UserProfileImage from "../../assets/placeholder.webp";
function ChatMessages({ text, sender }) {
  return (
    <div className="text-gray-100 flex items-center">
      <img
        src={UserProfileImage}
        alt="userImage"
        width="42"
        height="42"
        className="rounded-full outline-1 outline-gray-300"
      />
      <p className="bg-slate-500 p-2 rounded-lg ml-1.5">{text}</p>
    </div>
  );
}
export default ChatMessages;
