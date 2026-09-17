import "./App.css";
import { Route, Routes } from "react-router";
import ChatPage from "./pages/ChatPage/ChatPage";
import { Navigate } from "react-router";
function App() {
  return (
    <Routes>
      <Route
        index
        element={<Navigate to={"/chat"} replace={true}></Navigate>}
      ></Route>
      <Route path={"/chat"} element={<ChatPage></ChatPage>}></Route>
    </Routes>
  );
}

export default App;
