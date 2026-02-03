const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

export async function apiGet<T>(path: string): Promise<T> {
  const user = localStorage.getItem("talaty.user");
  const response = await fetch(`${API_BASE_URL}${path}`, {
    headers: user ? { "X-User": user } : undefined,
  });
  if (!response.ok) {
    throw new Error(`API error ${response.status}`);
  }
  return response.json() as Promise<T>;
}
