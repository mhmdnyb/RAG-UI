import "./App.css";
import { Route, Routes } from "react-router";
import ChatPage from "./pages/ChatPage/ChatPage";
function App() {
  return (
    <Routes>
      <Route index element={<h1>home</h1>}></Route>
      <Route path={"/chat"} element={<ChatPage></ChatPage>}></Route>
    </Routes>
  );
}

export default App;
