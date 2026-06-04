import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

export default function OrderCancel() {
  const { t } = useTranslation();
  return (
    <div className="container section center">
      <h1 className="section__title">{t("order.cancelTitle")}</h1>
      <p className="lead">{t("order.cancelMsg")}</p>
      <Link to="/cart" className="btn">
        {t("order.backToCart")}
      </Link>
    </div>
  );
}
