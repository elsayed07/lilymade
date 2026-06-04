import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { useStore } from "../context/StoreContext";

export default function ProductCard({ product }) {
  const { t } = useTranslation();
  const { symbol } = useStore();

  return (
    <Link to={`/products/${product.handle}`} className="card">
      <div className="card__img">
        {product.featured_image ? (
          <img src={product.featured_image} alt={product.title} loading="lazy" />
        ) : (
          <div className="card__placeholder" />
        )}
        {!product.in_stock && <span className="badge">{t("common.soldOut")}</span>}
      </div>
      <div className="card__body">
        <h3>{product.title}</h3>
        {product.price_from && (
          <p className="price">
            {symbol}
            {product.price_from}
          </p>
        )}
      </div>
    </Link>
  );
}
