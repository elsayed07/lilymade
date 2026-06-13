import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link, useSearchParams } from "react-router-dom";

import { api } from "../api";
import Seo from "../components/Seo";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";

export default function OrderSuccess() {
  const { t } = useTranslation();
  const { clear } = useCart();
  const { user } = useAuth();
  const [params] = useSearchParams();
  const [order, setOrder] = useState(null);
  const sessionId = params.get("session_id");

  useEffect(() => {
    clear();
    if (sessionId) {
      api.getOrderBySession(sessionId).then(setOrder).catch(() => setOrder(null));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return (
    <div className="container section center">
      <Seo title={t("order.successTitle")} />
      <h1 className="section__title">{t("order.successTitle")}</h1>
      <p className="lead">{t("order.successMsg")}</p>

      {order && (
        <div
          className="order-card"
          style={{ maxWidth: 420, margin: "1.5rem auto", textAlign: "left" }}
        >
          <div className="order-card__head">
            <strong>{t("account.orderNumber", { id: order.id })}</strong>
            <span className={`badge badge--${order.status}`}>{order.status}</span>
          </div>
          <ul>
            {order.items.map((it, i) => (
              <li key={i}>
                {it.product_title} – {it.variant_title} ×{it.quantity}
              </li>
            ))}
          </ul>
          <div className="order-card__total">
            {order.currency} {order.total}
          </div>
        </div>
      )}

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
