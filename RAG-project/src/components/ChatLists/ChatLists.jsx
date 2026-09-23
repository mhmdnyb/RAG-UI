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
          <h1 key={index} className="text-gray-100">
            {list.name}{" "}
          </h1>
        );
      })}
    </>
  );
}
export default ChatLists;
