import { useTranslation } from "react-i18next";

import Seo from "../components/Seo";

export default function Policies() {
  const { t } = useTranslation();
  return (
    <div className="container section prose">
      <Seo title={t("policies.title")} />
      <h1 className="section__title">{t("policies.title")}</h1>
      <h2>{t("policies.shippingTitle")}</h2>
      <p>{t("policies.shippingBody")}</p>
      <h2>{t("policies.returnsTitle")}</h2>
      <p>{t("policies.returnsBody")}</p>
      <h2>{t("policies.privacyTitle")}</h2>
      <p>{t("policies.privacyBody")}</p>
      <h2>{t("policies.cookiesTitle")}</h2>
      <p>{t("policies.cookiesBody")}</p>
    </div>
  );
}
