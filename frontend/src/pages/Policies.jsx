import { useTranslation } from "react-i18next";

export default function Policies() {
  const { t } = useTranslation();
  return (
    <div className="container section prose">
      <h1 className="section__title">{t("policies.title")}</h1>
      <h2>{t("policies.shippingTitle")}</h2>
      <p>{t("policies.shippingBody")}</p>
      <h2>{t("policies.returnsTitle")}</h2>
      <p>{t("policies.returnsBody")}</p>
    </div>
  );
}
