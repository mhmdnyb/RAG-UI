import "./Notification.css";
function Notification({ text, setModal }) {
  //   setTimeout(() => {
  //     setModal(false);
  //   }, 2500);
  return (
    <div className="text-tenpercent absolute z-10 left-1/2 top-3 bg-thirtypercent-light rounded-sm animate-notification px-10 py-2 -translate-x-1/2">
      <p>{text}</p>
    </div>
  );
}
export default Notification;
