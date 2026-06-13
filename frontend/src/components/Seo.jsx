import { useEffect } from "react";

// Minimal, dependency-free document-head manager. Sets the title, meta description,
// OpenGraph tags, canonical link and optional JSON-LD for the current page, and
// restores the previous values on unmount. Googlebot executes JS, so this is indexed.

function upsertMeta(attr, key, content) {
  if (!content) return null;
  let el = document.head.querySelector(`meta[${attr}="${key}"]`);
  let created = false;
  if (!el) {
    el = document.createElement("meta");
    el.setAttribute(attr, key);
    document.head.appendChild(el);
    created = true;
  }
  const prev = el.getAttribute("content");
  el.setAttribute("content", content);
  return { el, prev, created };
}

export default function Seo({ title, description, image, jsonLd }) {
  const fullTitle = title ? `${title} · Lilymade` : null;
  useEffect(() => {
    const prevTitle = document.title;
    if (fullTitle) document.title = fullTitle;

    const changes = [
      description && upsertMeta("name", "description", description),
      fullTitle && upsertMeta("property", "og:title", fullTitle),
      description && upsertMeta("property", "og:description", description),
      image && upsertMeta("property", "og:image", image),
      upsertMeta("property", "og:type", "website"),
    ];

    let canonical = document.head.querySelector('link[rel="canonical"]');
    let canonicalCreated = false;
    let canonicalPrev = null;
    if (!canonical) {
      canonical = document.createElement("link");
      canonical.setAttribute("rel", "canonical");
      document.head.appendChild(canonical);
      canonicalCreated = true;
    } else {
      canonicalPrev = canonical.getAttribute("href");
    }
    canonical.setAttribute("href", window.location.href.split("?")[0]);

    let script = null;
    if (jsonLd) {
      script = document.createElement("script");
      script.type = "application/ld+json";
      script.text = JSON.stringify(jsonLd);
      document.head.appendChild(script);
    }

    return () => {
      document.title = prevTitle;
      changes.forEach((c) => {
        if (!c) return;
        if (c.created) c.el.remove();
        else if (c.prev !== null) c.el.setAttribute("content", c.prev);
      });
      if (canonicalCreated) canonical.remove();
      else if (canonicalPrev !== null) canonical.setAttribute("href", canonicalPrev);
      if (script) script.remove();
    };
  }, [fullTitle, description, image, jsonLd]);

  return null;
}
