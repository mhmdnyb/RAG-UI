import { Outlet, Navigate } from "react-router";
import { useAuth } from "../../../context/useAuth";
import Loading from "../../Loading/Loading";

function PublicRoute() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="w-screen h-dvh flex items-center justify-center bg-dominant">
        <Loading />
      </div>
    );
  }

  return isAuthenticated ? <Navigate to="/chat" replace /> : <Outlet />;
}

export default PublicRoute;
