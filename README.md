# choncotm.com

Source code for [choncotm.com](https://choncotm.com) — my personal site, portfolio and brand page.

## Problem

I needed a real, professional home online: a place that presents who I am and what I do, links out to my other projects, and can host small extras (like a privacy policy page for another project) without depending on a third-party platform. I also wanted basic, privacy-friendly visit/click stats without handing that data to a third party.

## Solution

A minimal static site (no build step, no framework) with a small client-side i18n layer, deployed behind [Caddy](https://caddyserver.com/) in Docker for automatic HTTPS. Easy to edit, fast to load, cheap to run.

A small self-hosted FastAPI service (`admin/`) handles a password-protected `/admin` stats dashboard and records pageviews/outbound-link clicks reported by the site's own tracking script — no third-party analytics.

Hosted on an OVH VPS, running as one of several Docker containers on that server alongside my other projects (each isolated in its own container).

## Stack

- Static HTML/CSS/vanilla JS
- [Caddy](https://caddyserver.com/) for automatic HTTPS and reverse-proxying `/admin` and `/api` to the stats service
- FastAPI + SQLAlchemy + PostgreSQL for the stats/admin backend
- Docker, deployed on an OVH VPS

## Structure

```
.
├── index.html                        # main page
├── css/
│   ├── base.css                      # shared base styles
│   ├── home.css                      # homepage styles
│   └── policy.css                    # privacy policy page styles
├── js/
│   ├── i18n.js                       # language switcher (FR/EN/PT/ES/RU/DE)
│   ├── main.js                       # scroll-reveal animation, mobile nav toggle
│   └── track.js                      # sends pageview/click events to /api/track
├── amazon-price-tracker/
│   └── policy/index.html             # privacy policy for the Amazon Price Tracker bot
├── admin/                            # stats/admin backend (FastAPI)
│   ├── app/
│   │   ├── main.py                   # routes: /admin (login), /admin/stats, /api/track
│   │   └── templates/                # server-rendered login + stats dashboard
│   ├── requirements.txt
│   └── Dockerfile
├── Caddyfile                         # reverse proxy / HTTPS config
├── Dockerfile                        # static site image
├── .env.example                      # template for the server-side .env (never commit the real one)
└── docker-compose.yml
```

## Stats / admin

`/admin` is a login-protected dashboard (bcrypt-hashed password, signed session cookie, basic login rate-limiting) showing pageviews, unique visitors, top pages, and top outbound link clicks over the last 30 days. Events are posted by `js/track.js` to `POST /api/track` and stored in a dedicated PostgreSQL database — no cookies are set for visitors, and no raw IP is stored (a daily-rotating hash is used to estimate unique visitors).

## Running locally

```sh
docker compose up -d --build
```

Requires a `.env` file (see `.env.example`) with the stats database credentials, admin username/bcrypt password hash, and session secret.
