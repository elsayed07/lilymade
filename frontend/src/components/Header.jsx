import { useTranslation } from "react-i18next";
import { Link, NavLink } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { CURRENCIES, useStore } from "../context/StoreContext";

export default function Header() {
  const { t, i18n } = useTranslation();
  const { count } = useCart();
  const { currency, setCurrency } = useStore();
  const { user } = useAuth();
  const lang = i18n.language || "en";

  return (
    <header className="header">
      <div className="header__inner container">
        <Link to="/" className="brand">
          {t("brand")}
        </Link>

        <nav className="nav">
          <NavLink to="/shop">{t("nav.shop")}</NavLink>
          <NavLink to="/about">{t("nav.about")}</NavLink>
          <NavLink to="/contact">{t("nav.contact")}</NavLink>
        </nav>

        <div className="header__actions">
          <div className="lang-switch">
            <button
              className={lang.startsWith("en") ? "active" : ""}
              onClick={() => i18n.changeLanguage("en")}
            >
              EN
            </button>
            <span aria-hidden>/</span>
            <button
              className={lang.startsWith("it") ? "active" : ""}
              onClick={() => i18n.changeLanguage("it")}
            >
              IT
            </button>
          </div>

          <select
            className="currency-select"
            value={currency}
            onChange={(e) => setCurrency(e.target.value)}
            aria-label={t("common.currency")}
          >
            {CURRENCIES.map((c) => (
              <option key={c.code} value={c.code}>
                {c.code}
              </option>
            ))}
          </select>

          <Link to="/account" className="text-link">
            {user ? user.full_name?.split(" ")[0] || t("nav.account") : t("nav.account")}
          </Link>
          <Link to="/cart" className="text-link cart-link">
            {t("nav.cart")} ({count})
          </Link>
        </div>
      </div>
    </header>
  );
}
