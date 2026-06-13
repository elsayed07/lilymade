# Lilymade

A self-hosted e-commerce platform for **Lilymade** — an Italian artisan brand of
handcrafted crochet bags. Built to own the full stack and move the storefront off a
hosted SaaS, eliminating subscription and per-transaction fees.

The Django admin doubles as the seller dashboard, and the React storefront ships with
multi-language and multi-currency support out of the box.

---

## Features

- **Catalog & collections** — products grouped into collections, with per-product
  image galleries. Product images are **self-hosted** (downloaded from Shopify at seed
  time), so the store has no runtime dependency on Shopify's CDN.
- **Variants** — color/size variants with independent pricing and inventory.
- **Cart & checkout** — client-side cart with **Stripe hosted Checkout**; the server
  re-prices every line item and never trusts client-supplied amounts. Supports
  **promotion codes** and optional **Stripe Tax**.
- **Oversell protection** — stock is **reserved inside a row-locked transaction at
  checkout**, so two buyers can never pay for the same one-of-a-kind item. Unpaid
  reservations are released when Stripe expires the session (plus a `release_stale_orders`
  safety-net command).
- **Transactional email** — order confirmation to the customer, new-order/dispute alerts
  to the seller, and password-reset emails.
- **Customer accounts** — registration, login, password reset, and order history via JWT.
- **Webhooks** — `checkout.session.completed/expired`, `charge.refunded` (auto-restock),
  and `charge.dispute.created` are all handled idempotently.
- **Internationalization** — English and Italian storefront UI and product content.
- **Multi-currency** — prices stored in EUR and converted to USD / GBP / CAD using
  admin-editable exchange rates.
- **SEO** — per-page meta/OpenGraph tags, product JSON-LD, a generated `sitemap.xml`
  and `robots.txt`.
- **Privacy** — GDPR cookie-consent banner; analytics (GA4) load only after consent.
- **Hardening & ops** — DRF rate limiting on auth/checkout, optional Sentry error
  monitoring, a backup script, and GitHub Actions CI.
- **Seller dashboard** — the Django admin manages products, variants, inventory,
  translations, currency rates, and orders.

## Tech stack

| Layer    | Technology                                                        |
| -------- | ----------------------------------------------------------------- |
| Backend  | Django 6 · Django REST Framework · SimpleJWT · modeltranslation   |
| Frontend | React 19 · Vite · React Router · react-i18next                    |
| Database | PostgreSQL (SQLite for local dev)                                 |
| Payments | Stripe Checkout                                                   |
| Infra    | Docker · Docker Compose · nginx · Caddy (automatic HTTPS)         |

## Architecture

```
browser ──HTTPS──> Caddy ──HTTP──> nginx ──────> gunicorn (Django) ──> PostgreSQL
                   (TLS)           (SPA +              (REST API,
                                    reverse proxy)      admin, Stripe)
```

In production everything is served same-origin: Caddy terminates TLS, nginx serves the
built React SPA and proxies `/api`, `/admin`, `/static`, and `/media` to the Django
backend.

## Project structure

```
lilymade/
├── backend/              # Django project + REST API
│   ├── accounts/         # custom email-login user + JWT auth
│   ├── catalog/          # products, collections, variants, currency rates
│   ├── orders/           # orders, Stripe checkout, webhook fulfillment
│   └── core/             # settings, URLs, WSGI
├── frontend/             # React + Vite storefront
│   ├── src/              # pages, contexts, API client, i18n locales
│   └── nginx.conf        # SPA serving + API reverse proxy
├── Caddyfile             # TLS edge / reverse proxy
├── docker-compose.yml    # db + backend + web + caddy
└── .env.prod.example     # configuration template
```

## Local development

### Backend

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate            # Windows  (source .venv/bin/activate on macOS/Linux)
pip install -r requirements.txt

python manage.py migrate
python manage.py seed_catalog     # load the catalog
python manage.py createsuperuser  # access the admin dashboard
python manage.py runserver        # http://127.0.0.1:8000
```

By default the backend uses SQLite locally. Set `DATABASE_URL` to point at PostgreSQL.

### Frontend

```bash
cd frontend
npm install
npm run dev                       # http://127.0.0.1:5173
```

## Configuration

Copy `.env.prod.example` to `.env` and fill in the values:

| Variable                | Description                                              |
| ----------------------- | -------------------------------------------------------- |
| `DOMAIN`                | Public hostname Caddy obtains a TLS certificate for      |
| `DJANGO_SECRET_KEY`     | Django secret key                                        |
| `DJANGO_DEBUG`          | `False` in production                                    |
| `DJANGO_ALLOWED_HOSTS`  | Comma-separated allowed hosts                            |
| `CSRF_TRUSTED_ORIGINS`  | Full origins for admin/CSRF (must include scheme)        |
| `SECURE_SSL_REDIRECT`   | `True` once TLS is terminated at the proxy               |
| `FRONTEND_URL`          | Public site URL for Stripe success/cancel redirects      |
| `POSTGRES_DB/USER/PASSWORD` | PostgreSQL credentials                              |
| `STRIPE_SECRET_KEY` / `STRIPE_WEBHOOK_SECRET` | Stripe API + webhook secrets       |

## Deployment

The whole stack runs with Docker Compose:

```bash
cp .env.prod.example .env         # then edit values
docker compose up -d --build
```

For a full server-setup → DNS → Stripe → catalog import → Shopify cutover walkthrough,
see **[DEPLOYMENT.md](DEPLOYMENT.md)**.


