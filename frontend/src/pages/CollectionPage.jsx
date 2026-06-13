import { useEffect, useState } from "react";
import { useTranslation } from "react-i18next";
import { useParams } from "react-router-dom";

import { api } from "../api";
import ProductCard from "../components/ProductCard";
import Seo from "../components/Seo";
import { useStore } from "../context/StoreContext";

export default function CollectionPage() {
  const { handle } = useParams();
  const { t, i18n } = useTranslation();
  const { currency } = useStore();
  const [collection, setCollection] = useState(null);
  const lang = i18n.language;

  useEffect(() => {
    setCollection(null);
    api
      .getCollection(handle, { lang, currency })
      .then(setCollection)
      .catch(() => setCollection(null));
  }, [handle, lang, currency]);

  if (!collection) {
    return (
      <div className="container section">
        <p className="muted">{t("common.loading")}</p>
      </div>
    );
  }

  return (
    <div className="container section">
      <Seo title={collection.title} description={collection.description} image={collection.image} />
      <h1 className="section__title">{collection.title}</h1>
      {collection.description && <p className="muted lead">{collection.description}</p>}
      <div className="grid">
        {collection.products.map((p) => (
          <ProductCard key={p.id} product={p} />
        ))}
      </div>
    </div>
  );
}
