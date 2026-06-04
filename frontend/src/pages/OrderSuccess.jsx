import { useEffect } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function OrderSuccess() {
  const { t } = useTranslation();
  const { clear } = useCart();
  const { user } = useAuth();

  useEffect(() => {
    clear();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="container section center">
      <h1 className="section__title">{t("order.successTitle")}</h1>
      <p className="lead">{t("order.successMsg")}</p>
      <div className="cta-row">
        {user && (
          <Link to="/account" className="btn">
            {t("order.viewOrders")}
          </Link>
        )}
        <Link to="/shop" className="btn btn--ghost">
          {t("order.backHome")}
        </Link>
      </div>
    </div>
  );
}
