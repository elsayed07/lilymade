// Consent-gated Google Analytics 4 loader. Nothing is loaded until the visitor
// accepts analytics cookies (GDPR), and only when VITE_GA_ID is configured.

const GA_ID = import.meta.env.VITE_GA_ID;
let loaded = false;

export function loadAnalytics() {
  if (loaded || !GA_ID || typeof window === "undefined") return;
  loaded = true;

  const s = document.createElement("script");
  s.async = true;
  s.src = `https://www.googletagmanager.com/gtag/js?id=${GA_ID}`;
  document.head.appendChild(s);

  window.dataLayer = window.dataLayer || [];
  function gtag() {
    window.dataLayer.push(arguments);
  }
  window.gtag = gtag;
  gtag("js", new Date());
  gtag("config", GA_ID, { anonymize_ip: true });
}
