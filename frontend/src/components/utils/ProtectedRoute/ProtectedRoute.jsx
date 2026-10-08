import { Outlet, Navigate } from "react-router";
import { useAuth } from "../../../context/useAuth";
import Loading from "../../Loading/Loading";

function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="w-screen h-dvh flex items-center justify-center bg-dominant">
        <Loading />
      </div>
    );
  }

  return isAuthenticated ? <Outlet /> : <Navigate to="/login" replace />;
}

export default ProtectedRoute;
