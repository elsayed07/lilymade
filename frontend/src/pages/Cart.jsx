import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { api } from "../api";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { useStore } from "../context/StoreContext";

export default function Cart() {
  const { t, i18n } = useTranslation();
  const { currency, symbol } = useStore();
  const { items, setQuantity, remove } = useCart();
  const { token } = useAuth();
  const [priced, setPriced] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const lang = i18n.language;

  useEffect(() => {
    let active = true;
    async function load() {
      if (items.length === 0) {
        setPriced([]);
        setLoading(false);
        return;
      }
      setLoading(true);
      const handles = [...new Set(items.map((i) => i.handle))];
      const map = {};
      await Promise.all(
        handles.map(async (h) => {
          try {
            map[h] = await api.getProduct(h, { lang, currency });
          } catch {
            /* ignore */
          }
        })
      );
      const result = items.map((it) => {
        const p = map[it.handle];
        const v = p?.variants.find((x) => x.id === it.variant_id);
        return { ...it, price: v ? v.price : null, in_stock: v ? v.in_stock : false };
      });
      if (active) {
        setPriced(result);
        setLoading(false);
      }
    }
    load();
    return () => {
      active = false;
    };
  }, [items, lang, currency]);

  const subtotal = priced.reduce(
    (s, it) => s + (it.price ? parseFloat(it.price) * it.quantity : 0),
    0
  );
  const blocked = priced.some((it) => !it.in_stock);

  const checkout = async () => {
    setError("");
    setSubmitting(true);
    try {
      const { url } = await api.checkout({
        items: items.map((i) => ({ variant_id: i.variant_id, quantity: i.quantity })),
        currency,
        token,
      });
      window.location.href = url;
    } catch (e) {
      setError(e.message);
      setSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="container section">
        <p className="muted">{t("common.loading")}</p>
      </div>
    );
  }

  if (items.length === 0) {
    return (
      <div className="container section">
        <h1 className="section__title">{t("cart.title")}</h1>
        <p className="muted">{t("cart.empty")}</p>
        <Link to="/shop" className="btn">
          {t("cart.emptyCta")}
        </Link>
      </div>
    );
  }

  return (
    <div className="container section cart">
      <h1 className="section__title">{t("cart.title")}</h1>
      <div className="cart__items">
        {priced.map((it) => (
          <div key={it.variant_id} className="cart__row">
            {it.image && <img src={it.image} alt={it.product_title} />}
            <div className="cart__meta">
              <Link to={`/products/${it.handle}`}>{it.product_title}</Link>
              <span className="muted">{it.variant_title}</span>
              {!it.in_stock && <span className="badge">{t("common.outOfStock")}</span>}
            </div>
            <input
              type="number"
              min="1"
              value={it.quantity}
              onChange={(e) =>
                setQuantity(it.variant_id, Math.max(1, parseInt(e.target.value, 10) || 1))
              }
            />
            <span className="price">
              {it.price ? `${symbol}${(parseFloat(it.price) * it.quantity).toFixed(2)}` : "—"}
            </span>
            <button className="text-link" onClick={() => remove(it.variant_id)}>
              {t("cart.remove")}
            </button>
          </div>
        ))}
      </div>

      <div className="cart__summary">
        <div className="cart__subtotal">
          <span>{t("cart.subtotal")}</span>
          <strong>
            {symbol}
            {subtotal.toFixed(2)}
          </strong>
        </div>
        <p className="muted small">{t("cart.shippingNote")}</p>
        {error && <p className="error">{error}</p>}
        <button className="btn btn--lg" onClick={checkout} disabled={blocked || submitting}>
          {t("cart.checkout")}
        </button>
      </div>
    </div>
  );
}
