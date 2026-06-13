const BASE = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api";

function qs(params) {
  const sp = new URLSearchParams();
  Object.entries(params).forEach(([k, v]) => {
    if (v !== undefined && v !== null && v !== "") sp.append(k, v);
  });
  const s = sp.toString();
  return s ? `?${s}` : "";
}

async function request(path, { method = "GET", body, token } = {}) {
  const headers = { "Content-Type": "application/json" };
  if (token) headers["Authorization"] = `Bearer ${token}`;
  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  });
  if (!res.ok) {
    let detail = `Request failed (${res.status})`;
    try {
      const data = await res.json();
      detail = data.detail || Object.values(data)[0] || detail;
      if (Array.isArray(detail)) detail = detail[0];
    } catch {
      /* ignore */
    }
    const err = new Error(detail);
    err.status = res.status;
    throw err;
  }
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  getProducts: ({ collection, search, lang, currency } = {}) =>
    request(`/products/${qs({ collection, search, lang, currency })}`),
  getProduct: (handle, { lang, currency } = {}) =>
    request(`/products/${handle}/${qs({ lang, currency })}`),
  getCollections: ({ lang } = {}) => request(`/collections/${qs({ lang })}`),
  getCollection: (handle, { lang, currency } = {}) =>
    request(`/collections/${handle}/${qs({ lang, currency })}`),
  checkout: ({ items, currency, token }) =>
    request(`/checkout/`, { method: "POST", body: { items, currency }, token }),
  register: (data) => request(`/auth/register/`, { method: "POST", body: data }),
  login: (data) => request(`/auth/login/`, { method: "POST", body: data }),
  refresh: (refresh) => request(`/auth/refresh/`, { method: "POST", body: { refresh } }),
  me: (token) => request(`/auth/me/`, { token }),
  getOrders: (token) => request(`/account/orders/`, { token }),
  getOrderBySession: (sessionId) => request(`/orders/session/${sessionId}/`),
  requestPasswordReset: (email) =>
    request(`/auth/password-reset/`, { method: "POST", body: { email } }),
  confirmPasswordReset: (data) =>
    request(`/auth/password-reset-confirm/`, { method: "POST", body: data }),
};
