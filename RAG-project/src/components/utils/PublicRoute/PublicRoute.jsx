import { useEffect, useState } from "react";
import { Outlet, Navigate } from "react-router";
function PublicRoute() {
  const [isLogged, setisLogged] = useState(null);

  useEffect(() => {
    async function checkAuth() {
      try {
        const response = await fetch("http://localhost:8080/login", {
          headers: { Authorization: `Bearer ${document.cookie.split("=")[1]}` },
        });
        if (response.ok) {
          setisLogged(false);
        } else {
          setisLogged(true);
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
    <Navigate to={"/chat"} replace={"true"}></Navigate>
  );
}
export default PublicRoute;
