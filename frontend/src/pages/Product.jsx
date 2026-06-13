import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";

import { api } from "../api";
import Seo from "../components/Seo";
import { useCart } from "../context/CartContext";
import { useStore } from "../context/StoreContext";

export default function Product() {
  const { handle } = useParams();
  const { t, i18n } = useTranslation();
  const { currency, symbol } = useStore();
  const { add } = useCart();
  const [product, setProduct] = useState(null);
  const [selected, setSelected] = useState(null);
  const [activeImg, setActiveImg] = useState(0);
  const [added, setAdded] = useState(false);
  const lang = i18n.language;

  useEffect(() => {
    api
      .getProduct(handle, { lang, currency })
      .then((p) => {
        setProduct(p);
        const firstAvail = p.variants.find((v) => v.in_stock) || p.variants[0];
        setSelected(firstAvail || null);
        setActiveImg(0);
      })
      .catch(() => setProduct(null));
  }, [handle, lang, currency]);

  if (!product) {
    return (
      <div className="container section">
        <p className="muted">{t("common.loading")}</p>
      </div>
    );
  }

  const images = product.images || [];
  const hasOptions =
    product.variants.length > 1 ||
    (product.variants[0] && product.variants[0].title !== "Default");

  const jsonLd = {
    "@context": "https://schema.org",
    "@type": "Product",
    name: product.title,
    description: product.description || undefined,
    image: images.map((im) => im.url).filter(Boolean),
    brand: { "@type": "Brand", name: "Lilymade" },
    offers: selected
      ? {
          "@type": "Offer",
          price: selected.price,
          priceCurrency: currency,
          availability: selected.in_stock
            ? "https://schema.org/InStock"
            : "https://schema.org/OutOfStock",
        }
      : undefined,
  };

  const onAdd = () => {
    if (!selected || !selected.in_stock) return;
    add({
      variant_id: selected.id,
      quantity: 1,
      handle: product.handle,
      product_title: product.title,
      variant_title: selected.title,
      image: images[0]?.url || product.featured_image || "",
    });
    setAdded(true);
    setTimeout(() => setAdded(false), 1800);
  };

  return (
    <div className="container section product">
      <Seo
        title={product.title}
        description={product.description}
        image={images[0]?.url || product.featured_image}
        jsonLd={jsonLd}
      />
      <div className="product__gallery">
        <div className="product__main-img">
          {images[activeImg] ? (
            <img src={images[activeImg].url} alt={product.title} decoding="async" />
          ) : (
            <div className="card__placeholder" />
          )}
        </div>
        {images.length > 1 && (
          <div className="product__thumbs">
            {images.map((img, i) => (
              <button
                key={i}
                className={i === activeImg ? "active" : ""}
                onClick={() => setActiveImg(i)}
              >
                <img src={img.url} alt="" loading="lazy" decoding="async" />
              </button>
            ))}
          </div>
        )}
      </div>

      <div className="product__info">
        <h1>{product.title}</h1>
        <p className="price price--lg">
          {selected ? `${symbol}${selected.price}` : ""}
        </p>

        {hasOptions && (
          <div className="options">
            {product.variants.map((v) => (
              <button
                key={v.id}
                className={`option ${selected?.id === v.id ? "selected" : ""} ${
                  !v.in_stock ? "disabled" : ""
                }`}
                onClick={() => v.in_stock && setSelected(v)}
                disabled={!v.in_stock}
                title={!v.in_stock ? t("common.soldOut") : ""}
              >
                {v.title}
              </button>
            ))}
          </div>
        )}

        <button
          className="btn btn--lg"
          onClick={onAdd}
          disabled={!selected || !selected.in_stock}
        >
          {selected && selected.in_stock
            ? added
              ? t("product.added")
              : t("common.addToCart")
            : t("common.soldOut")}
        </button>

        {product.description && (
          <div className="product__desc">
            <h2>{t("product.description")}</h2>
            <p>{product.description}</p>
          </div>
        )}
      </div>
    </div>
  );
}
