const BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";

function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem("token");
}

async function request<T>(
  path: string,
  options: RequestInit = {}
): Promise<T> {
  const token = getToken();
  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };
  if (token) headers["Authorization"] = `Bearer ${token}`;

  const res = await fetch(`${BASE}${path}`, { ...options, headers });

  if (res.status === 401) {
    if (typeof window !== "undefined") {
      localStorage.removeItem("token");
      window.location.href = "/login";
    }
    throw new Error("Unauthorized");
  }

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail ?? "Request failed");
  }

  return res.json();
}

function json<T>(path: string, body: unknown, method = "POST"): Promise<T> {
  return request<T>(path, {
    method,
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
}

function form<T>(path: string, data: FormData, method = "POST"): Promise<T> {
  return request<T>(path, { method, body: data });
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const api = {
  auth: {
    login: (username: string, password: string) => {
      const body = new URLSearchParams({ username, password });
      return request<{ access_token: string; token_type: string }>(
        "/auth/token",
        {
          method: "POST",
          headers: { "Content-Type": "application/x-www-form-urlencoded" },
          body: body.toString(),
        }
      );
    },
    register: (username: string, password: string) =>
      json<{ access_token: string; token_type: string }>("/auth/register", {
        username,
        password,
      }),
    me: () => request<{ id: number; username: string }>("/auth/me"),
  },

  // ── Research ───────────────────────────────────────────────────────────────
  research: {
    run: (idea: string, reference_url?: string) =>
      json("/research", { idea, reference_url }),
    runWithDoc: (idea: string, file?: File, reference_url?: string) => {
      const fd = new FormData();
      fd.append("idea", idea);
      if (reference_url) fd.append("reference_url", reference_url);
      if (file) fd.append("file", file);
      return form("/research/upload", fd);
    },
  },

  // ── Webpage ────────────────────────────────────────────────────────────────
  webpage: {
    designAndDeploy: (body: unknown) =>
      json("/webpage/design-and-deploy", body),
    designAndDeployWithRef: (
      idea: string,
      research: unknown,
      reference_url?: string,
      text_preferences?: string,
      file?: File
    ) => {
      const fd = new FormData();
      fd.append("idea", idea);
      fd.append("research", JSON.stringify(research));
      if (reference_url) fd.append("reference_url", reference_url);
      if (text_preferences) fd.append("text_preferences", text_preferences);
      if (file) fd.append("file", file);
      return form("/webpage/design-and-deploy-with-ref", fd);
    },
  },

  // ── Instagram ──────────────────────────────────────────────────────────────
  instagram: {
    trends: (body: unknown) => json("/instagram/trends", body),
    generate: (body: unknown) => json("/instagram/generate", body),
    publish: (body: unknown) => json("/instagram/publish", body),
  },

  // ── Analytics ──────────────────────────────────────────────────────────────
  analytics: {
    ideas: (page = 1, page_size = 20) =>
      request(`/analytics/ideas?page=${page}&page_size=${page_size}`),
    summary: () => request("/analytics/summary"),
  },
};
