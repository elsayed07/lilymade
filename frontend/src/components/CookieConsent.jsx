import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { loadAnalytics } from "../lib/analytics";

const KEY = "cookie-consent"; // "accepted" | "rejected"

export default function CookieConsent() {
  const { t } = useTranslation();
  const [choice, setChoice] = useState(() => localStorage.getItem(KEY));

  useEffect(() => {
    if (choice === "accepted") loadAnalytics();
  }, [choice]);

  if (choice) return null;

  const decide = (value) => {
    localStorage.setItem(KEY, value);
    setChoice(value);
  };

  return (
    <div className="cookie-consent" role="dialog" aria-label={t("cookies.title")}>
      <p className="cookie-consent__text">
        {t("cookies.message")}{" "}
        <Link to="/policies">{t("cookies.learnMore")}</Link>
      </p>
      <div className="cookie-consent__actions">
        <button className="btn btn--ghost" onClick={() => decide("rejected")}>
          {t("cookies.reject")}
        </button>
        <button className="btn" onClick={() => decide("accepted")}>
          {t("cookies.accept")}
        </button>
      </div>
    </div>
  );
}
