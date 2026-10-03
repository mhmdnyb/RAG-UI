import "./App.css";
import { Route, Routes, Navigate } from "react-router";
import ChatPage from "./pages/ChatPage/ChatPage";
import LoginPage from "./pages/LoginPage/LoginPage";
import RegisterPage from "./pages/RegisterPage/RegisterPage";
import ProtectedRoute from "./components/utils/ProtectedRoute/ProtectedRoute";
import PublicRoute from "./components/utils/PublicRoute/PublicRoute";
import { AuthProvider } from "./context/AuthContext";
import { Toaster } from "react-hot-toast";

function App() {
  return (
    <AuthProvider>
      <Toaster
        position="top-center"
        toastOptions={{
          duration: 3000,
          style: {
            background: "#1e1e1e",
            color: "#d3fbd8",
            border: "1px solid rgba(0, 198, 207, 0.3)",
            fontFamily: "Lalezar, sans-serif",
          },
        }}
      />
      <Routes>
        <Route index element={<Navigate to="/chat" replace />} />
        <Route element={<ProtectedRoute />}>
          <Route path="/chat" element={<ChatPage />} />
          <Route path="/chat/:chatId" element={<ChatPage />} />
        </Route>
        <Route element={<PublicRoute />}>
          <Route path="/register" element={<RegisterPage />} />
          <Route path="/login" element={<LoginPage />} />
        </Route>
        <Route path="*" element={<Navigate to="/chat" replace />} />
      </Routes>
    </AuthProvider>
  );
}

export default App;
