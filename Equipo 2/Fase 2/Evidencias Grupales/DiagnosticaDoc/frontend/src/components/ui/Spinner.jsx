// ✅ compatible: default y named
function Spinner({ className = "" }) {
  return (
    <div className={`flex items-center gap-2 ${className}`}>
      <svg className="animate-spin w-5 h-5" viewBox="0 0 24 24">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" opacity="0.25" />
        <path d="M4 12a8 8 0 0 1 8-8" stroke="currentColor" strokeWidth="4" fill="none" />
      </svg>
      <span className="text-sm">Procesando…</span>
    </div>
  );
}

export default Spinner;
export { Spinner };  // ← named export para imports { Spinner }
