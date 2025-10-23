import { useState } from "react";
import api, { getApiBase, setApiBase } from "../api/client";
import { normalizeBase } from "../lib/storage";

export default function ConfigPage() {
  const [base, setBase] = useState(getApiBase());
  const [msg, setMsg] = useState("");

  async function testPing(url) {
    try {
      const clean = normalizeBase(url);
      const r = await api.get("/_ping", { baseURL: clean });
      return r?.data?.ok === true;
    } catch {
      return false;
    }
  }

  async function onSave(e) {
    e.preventDefault();
    setMsg("");
    const clean = normalizeBase(base);
    const saved = setApiBase(clean);   // <-- actualiza axios + persiste
    const ok = await testPing(saved);
    setMsg(ok ? "Conexión OK ✅" : "No responde /_ping ❌");
  }

  return (
    <div className="section">
      <h2 className="title-page">Configuración</h2>
      <form onSubmit={onSave} className="space-y-4">
        <label className="label">API Base URL</label>
        <input
          className="input"
          value={base}
          onChange={(e) => setBase(e.target.value)}
          placeholder="http://127.0.0.1:8000"
        />
        <button className="btn-primary">Guardar</button>
      </form>
      {msg && <div className="mt-3 text-sm">{msg}</div>}
    </div>
  );
}
