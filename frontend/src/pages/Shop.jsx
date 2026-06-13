import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";

import { api } from "../api";
import ProductCard from "../components/ProductCard";
import Seo from "../components/Seo";
import { useStore } from "../context/StoreContext";

export default function Shop() {
  const { t, i18n } = useTranslation();
  const { currency } = useStore();
  const [products, setProducts] = useState([]);
  const [search, setSearch] = useState("");
  const [loading, setLoading] = useState(true);
  const lang = i18n.language;

  useEffect(() => {
    setLoading(true);
    const handle = setTimeout(() => {
      api
        .getProducts({ search, lang, currency })
        .then((d) => {
          setProducts(d);
          setLoading(false);
        })
        .catch(() => setLoading(false));
    }, 250);
    return () => clearTimeout(handle);
  }, [search, lang, currency]);

  return (
    <div className="container section">
      <Seo title={t("shop.title")} description={t("home.heroSubtitle")} />
      <h1 className="section__title">{t("shop.title")}</h1>
      <input
        className="search"
        placeholder={t("shop.searchPlaceholder")}
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {loading ? (
        <p className="muted">{t("common.loading")}</p>
      ) : products.length === 0 ? (
        <p className="muted">{t("shop.empty")}</p>
      ) : (
        <div className="grid">
          {products.map((p) => (
            <ProductCard key={p.id} product={p} />
          ))}
        </div>
      )}
    </div>
  );
}
