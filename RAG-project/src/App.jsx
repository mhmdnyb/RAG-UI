import "./App.css";
import { Route, Routes } from "react-router";
import ChatPage from "./pages/ChatPage/ChatPage";
import { Navigate } from "react-router";
import LoginPage from "./pages/LoginPage/LoginPage";
import RegisterPage from "./pages/RegisterPage/RegisterPage";
function App() {
  return (
    <Routes>
      <Route
        index
        element={<Navigate to={"/chat"} replace={true}></Navigate>}
      ></Route>
      <Route path={"/chat"} element={<ChatPage></ChatPage>}></Route>
      <Route path="/register" element={<RegisterPage></RegisterPage>}></Route>
      <Route path="/login" element={<LoginPage></LoginPage>}></Route>
    </Routes>
  );
}

export default App;
