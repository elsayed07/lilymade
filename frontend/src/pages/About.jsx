import { useTranslation } from "react-i18next";

export default function About() {
  const { t } = useTranslation();
  return (
    <div className="container section prose">
      <h1 className="section__title">{t("about.title")}</h1>
      <p>{t("about.body")}</p>
    </div>
  );
}
