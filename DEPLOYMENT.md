# Deployment & Shopify cutover runbook

Step-by-step guide to take Lilymade live on your own server and retire Shopify.
The whole stack runs with `docker compose`; Caddy handles HTTPS automatically.

> **Fresh-start plan:** new Stripe account, only **products + collections** are migrated
> (no Shopify order/customer history). Shopify stays untouched as a read-only reference
> until the final step.

---

## 0. What you need first

- A **VPS** — recommended **Hetzner CX22** (~€4–5/mo, 2 vCPU / 4 GB, German DC: low
  latency for Italy + EU data residency). DigitalOcean / OVH / Contabo also fine.
- A **domain** (e.g. `lilymade.it` or `.com`). You can register a new one now and move
  the existing domain off Shopify later.
- A **Stripe** account (start in test mode).
- A **transactional email** account — **Brevo**, **Resend**, **Postmark**, or **Mailgun**
  (you'll need SMTP host/port/user/password).

---

## 1. Provision the server

```sh
# On a fresh Ubuntu 24.04 VPS, as root:
apt update && apt -y upgrade
curl -fsSL https://get.docker.com | sh           # installs Docker + compose plugin
adduser deploy && usermod -aG docker deploy       # non-root user
# (optional) ufw allow OpenSSH; ufw allow 80; ufw allow 443; ufw enable
```

Log back in as `deploy` for the rest.

## 2. Point DNS at the server

In your domain registrar, create records pointing at the VPS public IP:

| Type | Name | Value         |
| ---- | ---- | ------------- |
| A    | @    | `<VPS IPv4>`  |
| A    | www  | `<VPS IPv4>`  |

Wait for it to resolve (`ping yourdomain.com`). Caddy needs ports **80 + 443** reachable
to issue the Let's Encrypt certificate.

## 3. Get the code and configure

```sh
git clone https://github.com/elsayed07/lilymade.git
cd lilymade
cp .env.prod.example .env
nano .env
```

Fill in `.env` (see `.env.prod.example` for the full annotated list):

- `DOMAIN`, `DJANGO_ALLOWED_HOSTS`, `CSRF_TRUSTED_ORIGINS`, `CORS_ALLOWED_ORIGINS`,
  `FRONTEND_URL` — all your domain.
- `DJANGO_SECRET_KEY` — a long random string: `python -c "import secrets;print(secrets.token_urlsafe(50))"`.
- `DJANGO_DEBUG=False`, `SECURE_SSL_REDIRECT=True`.
- `POSTGRES_*` — a strong DB password.
- `STRIPE_*` — start with **test** keys (live keys in step 7).
- `EMAIL_*`, `DEFAULT_FROM_EMAIL`, `ORDER_NOTIFICATION_EMAIL` — your email provider.
- (optional) `SENTRY_DSN`, `VITE_GA_ID`, `STRIPE_AUTOMATIC_TAX`.

## 4. Launch

```sh
docker compose up -d --build
docker compose exec backend python manage.py createsuperuser
```

Visit `https://yourdomain.com` (storefront) and `https://yourdomain.com/admin/` (dashboard).

## 5. Import the catalog (products, collections, images)

```sh
docker compose exec backend python manage.py seed_catalog
```

This pulls products/collections from Shopify's public JSON and **downloads every image
into your own media volume** (no runtime dependency on Shopify afterwards).

Then in the admin (`/admin/`):

- **Set real inventory** — the seed marks available variants as stock `1`; correct the
  quantities for each variant.
- Review titles/descriptions and the Italian translations.
- Check **currency rates** under Catalog → Currency rates (seeded with approximate values).

## 6. Configure the Stripe webhook

In the Stripe Dashboard → **Developers → Webhooks → Add endpoint**:

- URL: `https://yourdomain.com/api/webhooks/stripe/`
- Events: `checkout.session.completed`, `checkout.session.expired`,
  `charge.refunded`, `charge.dispute.created`
- Copy the **Signing secret** into `.env` as `STRIPE_WEBHOOK_SECRET`, then
  `docker compose up -d` to reload.

## 7. Test, then go live

1. **Test mode:** place a full order using Stripe test card `4242 4242 4242 4242`.
   Confirm: stock decremented, order appears in admin as *paid*, confirmation email
   received, success page shows the order.
2. Test a **refund** from the Stripe dashboard → order should flip to *refunded* and
   stock should return.
3. Swap `.env` to **live** Stripe keys + the live webhook secret; `docker compose up -d`.
4. Place one small **real** order to confirm end-to-end.

## 8. Backups & maintenance

```sh
# Nightly backups (DB + media). Add to the deploy user's crontab:
crontab -e
0 3 * * *  cd /home/deploy/lilymade && ./scripts/backup.sh >> /var/log/lilymade-backup.log 2>&1

# Safety net: release stock from abandoned checkouts hourly.
15 * * * * cd /home/deploy/lilymade && docker compose exec -T backend python manage.py release_stale_orders
```

Configure off-site copies by editing the `rclone` line in `scripts/backup.sh`.

## 9. Cut over from Shopify

1. Run the new store in parallel for a few days; confirm orders + emails work.
2. Move the **domain** to the new server (update DNS / transfer the domain off Shopify).
3. Once traffic is flowing to the new site and you've confirmed live orders, **cancel
   the Shopify subscription.** Images and data are fully self-hosted, so nothing breaks.

## Updating later

```sh
cd lilymade && git pull
docker compose up -d --build
docker compose exec backend python manage.py migrate
```

---

## Troubleshooting

| Symptom | Check |
| ------- | ----- |
| TLS cert fails | DNS A record points to the VPS; ports 80/443 open; `docker compose logs caddy` |
| Admin login "CSRF" error | `CSRF_TRUSTED_ORIGINS` includes `https://yourdomain.com` |
| Images 404 | media volume mounted in `web` (it is by default); re-run `seed_catalog` |
| No confirmation emails | `EMAIL_*` set; SPF/DKIM configured at your email provider; `docker compose logs backend` |
| Orders stay *pending* | Stripe webhook endpoint + signing secret correct; check Stripe webhook delivery log |
