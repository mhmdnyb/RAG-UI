import "./RegisterPage.css";
import uscLogo from "../../assets/usc.png";
import { useRef, useState } from "react";
import Notification from "../../components/Notification/Notification";
function RegisterPage() {
  const [modal, setModal] = useState(false);
  const formRef = useRef();
  async function register(credentials) {
    try {
      const response = await fetch("http://localhost:8080/register", {
        method: "POST",

        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
      });
      if (response.ok) {
        const data = await response.json();
        setModal(true);
        console.log(data);
      }
    } catch (error) {
      console.log(error);
    }
  }
  return (
    <>
      {modal && <Notification text={"test"} setModal={setModal}></Notification>}
      <title>Register</title>
      <section className="w-screen h-dvh flex items-center justify-center bg-dominant text-thirtypercent">
        <form
          ref={formRef}
          action="index.php"
          className="bg-dominant-surface/80 backdrop-blur-md border border-thirtypercent/20 shadow-xl rounded-xl space-y-4 p-6"
        >
          <img src={uscLogo} alt="usclogo" className="mx-auto  mb-2" />

          <div className="w-64 rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent">
            <input
              autoComplete="name"
              type="text"
              name="name"
              id="name"
              placeholder="Name"
              className="w-full bg-dominant/60 text-thirtypercent placeholder-thirtypercent-muted/60 rounded-md focus:outline-none py-1.5 px-2.5 text-sm"
            />
          </div>

          <div className="w-64 rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent">
            <input
              autoComplete="tel"
              type="text"
              name="phoneNumber"
              id="phoneNumber"
              placeholder="Phone Number"
              className="w-full bg-dominant/60 text-thirtypercent placeholder-thirtypercent-muted/60 rounded-md focus:outline-none py-1.5 px-2.5 text-sm"
            />
          </div>

          <div className="w-64 rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent">
            <input
              autoComplete="new-password"
              type="password"
              name="password"
              id="password"
              placeholder="Password"
              className="w-full bg-dominant/60 text-thirtypercent placeholder-thirtypercent-muted/60 rounded-md focus:outline-none py-1.5 px-2.5 text-sm"
            />
          </div>

          <button
            onClick={(e) => {
              e.preventDefault();
              const form = new FormData(formRef.current);
              const data = Object.fromEntries(form);
              register(data);
            }}
            type="submit"
            className="bg-tenpercent text-dominant font-semibold py-2 px-8 rounded-md hover:bg-tenpercent-dark transition-colors shadow-sm block mx-auto cursor-pointer"
          >
            Register
          </button>
        </form>
      </section>
    </>
  );
}

export default RegisterPage;
