import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

export default function Footer() {
  const { t } = useTranslation();
  return (
    <footer className="footer">
      <div className="container footer__inner">
        <div>
          <div className="brand">{t("brand")}</div>
          <p className="muted">{t("tagline")}</p>
        </div>
        <nav className="footer__links">
          <Link to="/shop">{t("nav.shop")}</Link>
          <Link to="/about">{t("nav.about")}</Link>
          <Link to="/contact">{t("nav.contact")}</Link>
          <Link to="/policies">{t("policies.title")}</Link>
        </nav>
        <p className="muted small">
          © {new Date().getFullYear()} {t("brand")}. {t("footer.rights")} · {t("footer.madeBy")}
        </p>
      </div>
    </footer>
  );
}
