import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { api } from "../api";
import { useAuth } from "../context/AuthContext";

export default function Account() {
  const { t } = useTranslation();
  const { user, token, loading, login, register, logout } = useAuth();
  const [mode, setMode] = useState("login");
  const [form, setForm] = useState({ email: "", password: "", full_name: "" });
  const [error, setError] = useState("");
  const [orders, setOrders] = useState([]);

  useEffect(() => {
    if (token) api.getOrders(token).then(setOrders).catch(() => {});
  }, [token, user]);

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      if (mode === "login") await login(form.email, form.password);
      else await register(form);
    } catch (err) {
      setError(err.message);
    }
  };

  if (loading) {
    return (
      <div className="container section">
        <p className="muted">{t("common.loading")}</p>
      </div>
    );
  }

  if (user) {
    return (
      <div className="container section account">
        <div className="account__head">
          <h1>{t("account.welcome", { name: user.full_name || user.email })}</h1>
          <button className="text-link" onClick={logout}>
            {t("account.logout")}
          </button>
        </div>
        <h2 className="section__title">{t("account.myOrders")}</h2>
        {orders.length === 0 ? (
          <p className="muted">{t("account.noOrders")}</p>
        ) : (
          <div className="orders">
            {orders.map((o) => (
              <div key={o.id} className="order-card">
                <div className="order-card__head">
                  <strong>{t("account.orderNumber", { id: o.id })}</strong>
                  <span className={`badge badge--${o.status}`}>{o.status}</span>
                </div>
                <ul>
                  {o.items.map((it, i) => (
                    <li key={i}>
                      {it.product_title} – {it.variant_title} ×{it.quantity}
                    </li>
                  ))}
                </ul>
                <div className="order-card__total">
                  {o.currency} {o.total}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    );
  }

  return (
    <div className="container section auth">
      <h1 className="section__title">
        {mode === "login" ? t("account.signIn") : t("account.createAccount")}
      </h1>
      <form onSubmit={submit} className="form">
        {mode === "register" && (
          <label>
            {t("account.fullName")}
            <input
              value={form.full_name}
              onChange={(e) => setForm({ ...form, full_name: e.target.value })}
            />
          </label>
        )}
        <label>
          {t("account.email")}
          <input
            type="email"
            required
            value={form.email}
            onChange={(e) => setForm({ ...form, email: e.target.value })}
          />
        </label>
        <label>
          {t("account.password")}
          <input
            type="password"
            required
            value={form.password}
            onChange={(e) => setForm({ ...form, password: e.target.value })}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="btn btn--lg" type="submit">
          {mode === "login" ? t("account.signIn") : t("account.createAccount")}
        </button>
      </form>
      <button
        className="text-link"
        onClick={() => {
          setMode(mode === "login" ? "register" : "login");
          setError("");
        }}
      >
        {mode === "login" ? t("account.needAccount") : t("account.haveAccount")}
      </button>
    </div>
  );
}
