import "./RegisterPage.css";
import uscLogo from "../../assets/usc.png";
import { useState } from "react";
import { Link, useNavigate } from "react-router";
import toast from "react-hot-toast";
import { authApi } from "../../services/api";

function RegisterPage() {
  const [name, setName] = useState("");
  const [phoneNumber, setPhoneNumber] = useState("");
  const [password, setPassword] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();

    const cleanName = name.trim();
    const cleanPhone = phoneNumber.trim();

    if (!cleanName) {
      toast.error("لطفا نام خود را وارد کنید");
      return;
    }

    if (!cleanPhone) {
      toast.error("لطفا شماره تلفن را وارد کنید");
      return;
    }

    if (!password || password.length < 4) {
      toast.error("رمز عبور باید حداقل ۴ نویسه باشد");
      return;
    }

    setIsSubmitting(true);
    try {
      await authApi.register(cleanName, cleanPhone, password);
      toast.success("ثبت‌نام با موفقیت انجام شد! لطفا وارد شوید.");
      setTimeout(() => {
        navigate("/login");
      }, 1200);
    } catch (error) {
      if (error?.code === "001" || error?.data?.code === "001") {
        toast.error("این شماره تلفن قبلا ثبت شده است");
      } else {
        toast.error(error.message || "خطا در ثبت نام");
      }
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <>
      <title>ثبت‌نام | دستیار هوشمند دانشگاه</title>
      <section className="w-screen h-dvh flex items-center justify-center bg-dominant text-thirtypercent px-4">
        <form
          onSubmit={handleSubmit}
          className="w-full max-w-sm bg-dominant-surface/80 backdrop-blur-md border border-thirtypercent/20 shadow-xl rounded-xl space-y-4 p-6"
        >
          <img src={uscLogo} alt="لوگوی دانشگاه علم و فرهنگ" className="mx-auto mb-2 h-16 object-contain" />
          <h1 className="text-center text-lg text-thirtypercent font-medium">ایجاد حساب در دستیار دانشگاه</h1>

          <div className="w-full rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent flex items-center px-2 bg-dominant/60">
            <label htmlFor="name" className="cursor-pointer">
              <svg
                width="22px"
                height="22px"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <circle cx="12" cy="6" r="4" stroke="#00aab2" strokeWidth="1.5" />
                <path
                  d="M19.9975 18C20 17.8358 20 17.669 20 17.5C20 15.0147 16.4183 13 12 13C7.58172 13 4 15.0147 4 17.5C4 19.9853 4 22 12 22C14.231 22 15.8398 21.8433 17 21.5634"
                  stroke="#00aab2"
                  strokeWidth="1.5"
                  strokeLinecap="round"
                />
              </svg>
            </label>
            <input
              autoComplete="name"
              type="text"
              name="name"
              id="name"
              placeholder="نام و نام خانوادگی"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full bg-transparent text-thirtypercent placeholder-thirtypercent-muted/60 focus:outline-none py-2 px-2 text-sm"
            />
          </div>

          <div className="w-full rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent flex items-center px-2 bg-dominant/60">
            <label htmlFor="phoneNumber" className="cursor-pointer">
              <svg
                width="22px"
                height="22px"
                viewBox="0 0 24 24"
                fill="none"
                xmlns="http://www.w3.org/2000/svg"
              >
                <path
                  d="M7.02,15.976,5.746,13.381a.7.7,0,0,0-.579-.407l-1.032-.056a.662.662,0,0,1-.579-.437,9.327,9.327,0,0,1,0-6.5.662.662,0,0,1,.579-.437l1.032-.109a.7.7,0,0,0,.589-.394L7.03,2.446l.331-.662a.708.708,0,0,0,.07-.308.692.692,0,0,0-.179-.467A3,3,0,0,0,4.693.017l-.235.03L4.336.063A1.556,1.556,0,0,0,4.17.089l-.162.04C1.857.679.165,4.207,0,8.585V9.83c.165,4.372,1.857,7.9,4,8.483l.162.04a1.556,1.556,0,0,0,.165.026l.122.017.235.03a3,3,0,0,0,2.558-.993.692.692,0,0,0,.179-.467.708.708,0,0,0-.07-.308Z"
                  transform="translate(4.393 6.587) rotate(-30)"
                  fill="none"
                  stroke="#00aab2"
                  strokeMiterlimit="10"
                  strokeWidth="1.5"
                />
              </svg>
            </label>
            <input
              autoComplete="tel"
              type="text"
              name="phoneNumber"
              id="phoneNumber"
              placeholder="شماره تلفن (مثال: 09121234567)"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="w-full bg-transparent text-thirtypercent placeholder-thirtypercent-muted/60 focus:outline-none py-2 px-2 text-sm text-left"
              dir="ltr"
            />
          </div>

          <div className="w-full rounded-md transition-all ring-1 ring-thirtypercent/30 has-focus:ring-2 has-focus:ring-tenpercent flex items-center px-2 bg-dominant/60">
            <label htmlFor="password" className="cursor-pointer">
              <svg
                width="22px"
                height="22px"
                viewBox="0 0 48 48"
                xmlns="http://www.w3.org/2000/svg"
                fill="#00aab2"
              >
                <path d="M39,18H35V13A11,11,0,0,0,24,2H22A11,11,0,0,0,11,13v5H7a2,2,0,0,0-2,2V44a2,2,0,0,0,2,2H39a2,2,0,0,0,2-2V20A2,2,0,0,0,39,18ZM15,13a7,7,0,0,1,7-7h2a7,7,0,0,1,7,7v5H15ZM37,42H9V22H37Z" />
                <circle cx="15" cy="32" r="3" />
                <circle cx="23" cy="32" r="3" />
                <circle cx="31" cy="32" r="3" />
              </svg>
            </label>
            <input
              autoComplete="new-password"
              type="password"
              name="password"
              id="password"
              placeholder="رمز عبور"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-transparent text-thirtypercent placeholder-thirtypercent-muted/60 focus:outline-none py-2 px-2 text-sm text-left"
              dir="ltr"
            />
          </div>

          <p className="text-thirtypercent-muted text-center text-sm">
            قبلاً ثبت‌نام کرده‌اید؟
            <Link
              className="text-tenpercent font-medium mx-1 hover:text-thirtypercent transition-colors"
              to="/login"
            >
              ورود
            </Link>
          </p>

          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full bg-tenpercent text-dominant font-semibold py-2 px-4 rounded-md hover:bg-tenpercent-dark transition-all shadow-md flex items-center justify-center cursor-pointer active:scale-95 disabled:opacity-50 disabled:pointer-events-none"
          >
            {isSubmitting ? (
              <div className="size-5 rounded-full border-2 border-dominant border-r-transparent animate-spin" />
            ) : (
              "ثبت‌نام"
            )}
          </button>
        </form>
      </section>
    </>
  );
}

export default RegisterPage;
