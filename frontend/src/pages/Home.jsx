import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { Link } from "react-router-dom";

import { api } from "../api";
import ProductCard from "../components/ProductCard";
import { useStore } from "../context/StoreContext";

export default function Home() {
  const { t, i18n } = useTranslation();
  const { currency } = useStore();
  const [collections, setCollections] = useState([]);
  const [featured, setFeatured] = useState([]);
  const lang = i18n.language;

  useEffect(() => {
    api.getCollections({ lang }).then(setCollections).catch(() => {});
    api
      .getProducts({ collection: "frontpage", lang, currency })
      .then(setFeatured)
      .catch(() => {});
  }, [lang, currency]);

  return (
    <>
      <section className="hero">
        <div className="container hero__inner">
          <p className="hero__eyebrow">{t("tagline")}</p>
          <h1>{t("home.heroTitle")}</h1>
          <p className="hero__sub">{t("home.heroSubtitle")}</p>
          <Link to="/shop" className="btn">
            {t("home.shopNow")}
          </Link>
        </div>
      </section>

      {featured.length > 0 && (
        <section className="container section">
          <h2 className="section__title">{t("home.featured")}</h2>
          <div className="grid">
            {featured.map((p) => (
              <ProductCard key={p.id} product={p} />
            ))}
          </div>
        </section>
      )}

      <section className="container section">
        <h2 className="section__title">{t("home.shopByCollection")}</h2>
        <div className="collections-grid">
          {collections.map((c) => (
            <Link key={c.handle} to={`/collections/${c.handle}`} className="collection-tile">
              {c.image ? (
                <img src={c.image} alt={c.title} loading="lazy" />
              ) : (
                <div className="card__placeholder" />
              )}
              <span>{c.title}</span>
            </Link>
          ))}
        </div>
      </section>

      <section className="story">
        <div className="container">
          <p>{t("home.story")}</p>
        </div>
      </section>
    </>
  );
}
