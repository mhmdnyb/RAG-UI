import { use } from "react";

async function getList() {
  try {
    const response = await fetch("http://localhost:8080/chat-list", {
      headers: {
        Authorization: `Bearer ${document.cookie.split("=")[1]}`,
        "Content-Type": "application/json",
      },
    });
    if (response.ok) {
      const data = await response.json();
      return data;
    }
  } catch (error) {
    console.log(error);
  }
}
const prm = getList();
function ChatLists() {
  const temp = use(prm);
  return (
    <>
      {" "}
      {temp?.data.map((list, index) => {
        return (
          <div
            key={index}
            className="text-gray-100 bg-linear-to-bl from-white/60 to-white/50 border-white/40 backdrop-blur-2xl shadow-xs shadow-black/30 rounded-lg flex items-center justify-center w-full"
          >
            <p className="text-center">{list.name}</p>
          </div>
        );
      })}
    </>
  );
}
export default ChatLists;
