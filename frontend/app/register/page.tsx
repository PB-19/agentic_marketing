"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { api } from "@/lib/api";
import { useAuth } from "@/lib/auth";

export default function RegisterPage() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    if (password !== confirm) { setError("Passwords do not match"); return; }
    if (password.length < 6) { setError("Password must be at least 6 characters"); return; }
    setLoading(true);
    try {
      const { access_token } = await api.auth.register(username, password);
      await login(access_token);
      router.replace("/dashboard");
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Registration failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", padding: 24 }}>
      <div className="card" style={{ width: "100%", maxWidth: 400, padding: 32 }}>
        <h1 style={{ fontSize: 24, fontWeight: 400, marginBottom: 8 }}>Create account</h1>
        <p style={{ fontSize: 14, color: "var(--md-sys-color-on-surface-variant)", marginBottom: 24 }}>
          Join Agentic Marketing
        </p>

        <form onSubmit={submit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          <div>
            <label className="field-label">Username</label>
            <input className="field-input" value={username} onChange={e => setUsername(e.target.value)} required autoFocus />
          </div>
          <div>
            <label className="field-label">Password</label>
            <input className="field-input" type="password" value={password} onChange={e => setPassword(e.target.value)} required />
          </div>
          <div>
            <label className="field-label">Confirm password</label>
            <input className="field-input" type="password" value={confirm} onChange={e => setConfirm(e.target.value)} required />
          </div>

          {error && (
            <div style={{ padding: "12px 16px", background: "var(--md-sys-color-error-container)", color: "var(--md-sys-color-on-error-container)", borderRadius: "var(--md-shape-xs)", fontSize: 14 }}>
              {error}
            </div>
          )}

          <button className="btn-filled" type="submit" disabled={loading} style={{ marginTop: 8 }}>
            {loading ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p style={{ marginTop: 24, textAlign: "center", fontSize: 14, color: "var(--md-sys-color-on-surface-variant)" }}>
          Already have an account?{" "}
          <Link href="/login" style={{ color: "var(--md-sys-color-primary)", textDecoration: "none", fontWeight: 500 }}>
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}
