# choncotm.com

Source code for [choncotm.com](https://choncotm.com) — my personal site, portfolio and brand page.

## Stack

- Static HTML/CSS/vanilla JS
- Served by [Caddy](https://caddyserver.com/) (automatic HTTPS) inside Docker

## Structure

- `index.html`, `css/`, `js/` — the main site
- `amazon-price-tracker/policy/` — privacy policy page for the [Amazon Price Tracker](https://github.com/choncotm/amazon-price-tracker-bot) Telegram bot
- `Caddyfile`, `Dockerfile`, `docker-compose.yml` — deployment

## Running locally

```sh
docker compose up -d --build
```
