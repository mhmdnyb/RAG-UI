import "./LoginPage.css";
import uscLogo from "../../assets/usc.png";
import { useRef } from "react";
import { Link } from "react-router";
import toast from "react-hot-toast";
function LoginPage() {
  const formRef = useRef();
  function setCookie(token) {
    document.cookie = `token=${token};expires=${new Date(Date.now() + 7 * 24 * 3600 * 1000).toUTCString()};path=/;`;
  }
  async function login(credentials) {
    try {
      const response = await fetch("http://localhost:8080/login", {
        method: "POST",

        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(credentials),
      });
      if (response.ok) {
        const data = await response.json();
        setCookie(data.data.token);
        toast.success("خوش اومدی!");
        setTimeout(() => {
          window.location.reload();
        }, 2500);
      }
    } catch (error) {
      console.log(error);
    }
  }
  return (
    <>
      <title>Login</title>
      <section className="w-screen h-dvh flex items-center justify-center bg-dominant text-thirtypercent">
        <form
          ref={formRef}
          action="index.php"
          className="bg-dominant-surface/80 backdrop-blur-md border border-thirtypercent/20 shadow-xl rounded-xl space-y-4 p-6"
        >
          <img src={uscLogo} alt="usclogo" className="mx-auto  mb-2" />

          <div className="w-64 rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent flex items-center">
            <label htmlFor="phoneNumber">
              <svg
                width="25px"
                height="25px"
                viewBox="0 0 24 24"
                id="phone_number"
                data-name="phone number"
                xmlns="http://www.w3.org/2000/svg"
                fill="#00aab2"
              >
                <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
                <g
                  id="SVGRepo_tracerCarrier"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                ></g>
                <g id="SVGRepo_iconCarrier">
                  <rect
                    id="Rectangle_5"
                    data-name="Rectangle 5"
                    width="24"
                    height="24"
                    fill="none"
                  ></rect>
                  <path
                    id="Shape"
                    d="M7.02,15.976,5.746,13.381a.7.7,0,0,0-.579-.407l-1.032-.056a.662.662,0,0,1-.579-.437,9.327,9.327,0,0,1,0-6.5.662.662,0,0,1,.579-.437l1.032-.109a.7.7,0,0,0,.589-.394L7.03,2.446l.331-.662a.708.708,0,0,0,.07-.308.692.692,0,0,0-.179-.467A3,3,0,0,0,4.693.017l-.235.03L4.336.063A1.556,1.556,0,0,0,4.17.089l-.162.04C1.857.679.165,4.207,0,8.585V9.83c.165,4.372,1.857,7.9,4,8.483l.162.04a1.556,1.556,0,0,0,.165.026l.122.017.235.03a3,3,0,0,0,2.558-.993.692.692,0,0,0,.179-.467.708.708,0,0,0-.07-.308Z"
                    transform="translate(4.393 6.587) rotate(-30)"
                    fill="none"
                    stroke="#00aab2"
                    strokeMiterlimit="10"
                    strokeWidth="1.5"
                  ></path>{" "}
                </g>
              </svg>
            </label>
            <input
              autoComplete="tel"
              type="text"
              name="phoneNumber"
              id="phoneNumber"
              placeholder="شماره تلفن"
              className="w-full bg-dominant/60 text-thirtypercent placeholder-thirtypercent-muted/60 rounded-md focus:outline-none py-1.5 px-2.5 text-sm"
            />
          </div>

          <div className="w-64 rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent flex items-center">
            <label htmlFor="password">
              <svg
                width="25px"
                height="25px"
                viewBox="0 0 48 48"
                xmlns="http://www.w3.org/2000/svg"
                fill="#00aab2"
              >
                <g id="SVGRepo_bgCarrier" strokeWidth="0"></g>
                <g
                  id="SVGRepo_tracerCarrier"
                  strokeLinecap="round"
                  strokeLinejoin="round"
                ></g>
                <g id="SVGRepo_iconCarrier">
                  {" "}
                  <g id="Layer_2" data-name="Layer 2">
                    {" "}
                    <g id="invisible_box" data-name="invisible box">
                      {" "}
                      <rect width="48" height="48" fill="none"></rect>{" "}
                    </g>{" "}
                    <g id="Layer_7" data-name="Layer 7">
                      {" "}
                      <g>
                        {" "}
                        <path d="M39,18H35V13A11,11,0,0,0,24,2H22A11,11,0,0,0,11,13v5H7a2,2,0,0,0-2,2V44a2,2,0,0,0,2,2H39a2,2,0,0,0,2-2V20A2,2,0,0,0,39,18ZM15,13a7,7,0,0,1,7-7h2a7,7,0,0,1,7,7v5H15ZM37,42H9V22H37Z"></path>{" "}
                        <circle cx="15" cy="32" r="3"></circle>{" "}
                        <circle cx="23" cy="32" r="3"></circle>{" "}
                        <circle cx="31" cy="32" r="3"></circle>{" "}
                      </g>{" "}
                    </g>{" "}
                  </g>{" "}
                </g>
              </svg>
            </label>
            <input
              autoComplete="new-password"
              type="password"
              name="password"
              id="password"
              placeholder="رمز عبور"
              className="w-full bg-dominant/60 text-thirtypercent placeholder-thirtypercent-muted/60 rounded-md focus:outline-none py-1.5 px-2.5 text-sm"
            />
          </div>
          <p className="text-thirtypercent text-center">
            هنوز ثبت نام نکردید؟
            <Link
              className="text-tenpercent-dark mx-1 hover:text-tenpercent transition-colors"
              to={"/register"}
            >
              ثبت نام
            </Link>
          </p>

          <button
            onClick={(e) => {
              e.preventDefault();
              const form = new FormData(formRef.current);
              const data = Object.fromEntries(form);
              login(data);
            }}
            type="submit"
            className="bg-tenpercent text-dominant font-semibold py-2 px-8 rounded-md hover:bg-tenpercent-dark transition-all shadow-sm block mx-auto cursor-pointer active:scale-105"
          >
            ورود
          </button>
        </form>
      </section>
    </>
  );
}

export default LoginPage;
