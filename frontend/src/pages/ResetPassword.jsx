import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useNavigate, useSearchParams } from "react-router-dom";

import { api } from "../api";
import Seo from "../components/Seo";

export default function ResetPassword() {
  const { t } = useTranslation();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [password, setPassword] = useState("");
  const [done, setDone] = useState(false);
  const [error, setError] = useState("");

  const uid = params.get("uid");
  const token = params.get("token");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.confirmPasswordReset({ uid, token, password });
      setDone(true);
      setTimeout(() => navigate("/account"), 1800);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container section auth">
      <Seo title={t("auth.resetTitle")} />
      <h1 className="section__title">{t("auth.resetTitle")}</h1>
      {!uid || !token ? (
        <p className="error">{t("auth.resetInvalid")}</p>
      ) : done ? (
        <p className="lead">{t("auth.resetDone")}</p>
      ) : (
        <form onSubmit={submit} className="form">
          <label>
            {t("auth.newPassword")}
            <input
              type="password"
              required
              minLength={8}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="btn btn--lg" type="submit">
            {t("auth.resetTitle")}
          </button>
        </form>
      )}
      <Link className="text-link" to="/account">
        {t("auth.backToSignIn")}
      </Link>
    </div>
  );
}
