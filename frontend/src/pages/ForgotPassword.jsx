import { useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { api } from "../api";
import Seo from "../components/Seo";

export default function ForgotPassword() {
  const { t } = useTranslation();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  const submit = async (e) => {
    e.preventDefault();
    setError("");
    try {
      await api.requestPasswordReset(email);
      setSent(true);
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="container section auth">
      <Seo title={t("auth.forgotTitle")} />
      <h1 className="section__title">{t("auth.forgotTitle")}</h1>
      {sent ? (
        <p className="lead">{t("auth.forgotSent")}</p>
      ) : (
        <form onSubmit={submit} className="form">
          <label>
            {t("account.email")}
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />
          </label>
          {error && <p className="error">{error}</p>}
          <button className="btn btn--lg" type="submit">
            {t("auth.sendResetLink")}
          </button>
        </form>
      )}
      <Link className="text-link" to="/account">
        {t("auth.backToSignIn")}
      </Link>
    </div>
  );
}
