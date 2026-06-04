import { useTranslation } from "react-i18next";

const STORE_EMAIL = "lilymade.itt@gmail.com";

export default function Contact() {
  const { t } = useTranslation();
  return (
    <div className="container section prose">
      <h1 className="section__title">{t("contact.title")}</h1>
      <p>{t("contact.body")}</p>
      <p>
        {t("contact.email")}: <a href={`mailto:${STORE_EMAIL}`}>{STORE_EMAIL}</a>
      </p>
    </div>
  );
}
