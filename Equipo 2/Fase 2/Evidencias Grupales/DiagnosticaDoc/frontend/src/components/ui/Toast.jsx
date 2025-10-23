// ✅ compatible: export default y export nombrado
import { useEffect } from "react";

function Toast({ type = "info", children, onClose }) {
  useEffect(() => {
    const t = setTimeout(() => onClose?.(), 3500);
    return () => clearTimeout(t);
  }, [onClose]);

  const base =
    "fixed bottom-4 right-4 px-4 py-3 rounded-lg shadow-lg text-white z-[1000]";
  const color =
    type === "error"
      ? "bg-red-600"
      : type === "success"
      ? "bg-emerald-600"
      : "bg-slate-700";

  return (
    <div className={`${base} ${color}`}>
      <div className="text-sm">{children}</div>
    </div>
  );
}

export default Toast;
export { Toast };   // ← named export para imports { Toast }
