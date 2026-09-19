import { useEffect, useState } from "react";
import { Outlet, Navigate } from "react-router";
function ProtectedRoute() {
  const [isLogged, setisLogged] = useState(null);

  useEffect(() => {
    async function checkAuth() {
      try {
        const response = await fetch("http://localhost:8080/login", {
          headers: { Authorization: `Bearer ${document.cookie.split("=")[1]}` },
        });
        if (response.ok) {
          setisLogged(true);
        } else {
          setisLogged(false);
        }
      } catch (error) {
        console.log(error);
      }
    }
    checkAuth();
  });
  if (isLogged === null) {
    return <div>Loading...</div>; // Or your loading spinner component
  }
  return isLogged ? (
    <Outlet></Outlet>
  ) : (
    <Navigate to={"/register"} replace={"true"}></Navigate>
  );
}
export default ProtectedRoute;
