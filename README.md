# choncotm.com

Source code for [choncotm.com](https://choncotm.com) — my personal site, portfolio and brand page.

## Problem

I needed a real, professional home online: a place that presents who I am and what I do, links out to my other projects, and can host small extras (like a privacy policy page for another project) without depending on a third-party platform.

## Solution

A minimal static site (no build step, no framework) with a small client-side i18n layer, deployed behind [Caddy](https://caddyserver.com/) in Docker for automatic HTTPS. Easy to edit, fast to load, cheap to run.

Hosted on an OVH VPS, running as one of several Docker containers on that server alongside my other projects (each isolated in its own container).

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
│   └── main.js                       # scroll-reveal animation
├── amazon-price-tracker/
│   └── policy/index.html             # privacy policy for the Amazon Price Tracker bot
├── Caddyfile                         # reverse proxy / HTTPS config
├── Dockerfile
└── docker-compose.yml
```

## Running locally

```sh
docker compose up -d --build
```
