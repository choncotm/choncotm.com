# choncotm.com

[English](#english) | [Français](#français)

## English

Source code for [choncotm.com](https://choncotm.com) — my personal site, portfolio and brand page.

### Problem

I needed a real, professional home online: a place that presents who I am and what I do, links out to my other projects, and can host small extras (like a privacy policy page for another project) without depending on a third-party platform. I also wanted basic, privacy-friendly visit/click stats without handing that data to a third party.

### Solution

A minimal static site (no build step, no framework) with a small client-side i18n layer, deployed behind [Caddy](https://caddyserver.com/) in Docker for automatic HTTPS. Easy to edit, fast to load, cheap to run.

A small self-hosted FastAPI service (`admin/`) handles a password-protected `/admin` stats dashboard and records pageviews/link clicks reported by the site's own tracking script — no third-party analytics.

Hosted on an OVH VPS, running as one of several Docker containers on that server alongside my other projects (each isolated in its own container).

### Stack

- Static HTML/CSS/vanilla JS
- [Caddy](https://caddyserver.com/) for automatic HTTPS and reverse-proxying `/admin` and `/api` to the stats service
- FastAPI + SQLAlchemy + PostgreSQL for the stats/admin backend
- Docker, deployed on an OVH VPS

### Structure

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
│   │   ├── main.py                   # routes, scheduled monthly/yearly reports
│   │   └── templates/                # server-rendered login, stats, history, reports
│   ├── requirements.txt
│   └── Dockerfile
├── Caddyfile                         # reverse proxy / HTTPS config
├── Dockerfile                        # static site image
├── .env.example                      # template for the server-side .env (never commit the real one)
└── docker-compose.yml
```

### Stats / admin

`/admin` is a login-protected dashboard (bcrypt-hashed passwords, signed session cookie, basic login rate-limiting) showing pageviews, unique visitors, top pages, and top link clicks (internal and external) over the last 30 days. Events are posted by `js/track.js` to `POST /api/track` and stored in a dedicated PostgreSQL database — no cookies are set for visitors, and no raw IP is stored (a daily-rotating hash is used to estimate unique visitors).

The admin session expires after 1 hour server-side regardless of activity, and is a browser-session cookie (no persistent max-age), so closing the browser also logs you out.

`/admin/history` paginates through every recorded event (50 per page) instead of loading it all at once. `/admin/reports` shows monthly and yearly summaries, generated automatically by an in-process scheduler on the 1st of each month and on January 1st.

#### Accounts and permissions

Accounts live in the `users` table (username, bcrypt password hash, `is_owner` flag, list of granted `resources`). The owner account is seeded once from `ADMIN_USERNAME`/`ADMIN_PASSWORD_HASH` on first run; after that, all accounts (including the owner's own password) are managed from `/admin/users`, which is itself owner-only.

- The **owner** (`is_owner=True`) can see everything: site stats/history/reports, `/admin/users`, and every per-resource dashboard.
- **Collaborators** have no `is_owner` flag and only see the dashboards for the resources granted to them (e.g. `amazon_price_tracker` for the Amazon Price Tracker bot, shared with visualbynoah) via `/admin/home`. They cannot see the site's own analytics.
- `/admin/bots/amazon-price-tracker` shows real stats (users, tracked products, price drops/rises, recent changes, monthly/yearly reports) fetched over HTTP from a small internal stats API running in the `amazon-price-tracker-bot` project — see that project's README for how it's wired up (shared Docker network, `BOT_STATS_API_URL`/`BOT_STATS_TOKEN` env vars here). If that service is unreachable, the page shows a "service indisponible" message instead of erroring.

### Running locally

```sh
docker compose up -d --build
```

Requires a `.env` file (see `.env.example`) with the stats database credentials, admin username/bcrypt password hash, and session secret.

---

## Français

Code source de [choncotm.com](https://choncotm.com) — mon site personnel, portfolio et page de marque.

### Problème

J'avais besoin d'une vraie vitrine professionnelle en ligne : un endroit qui présente qui je suis et ce que je fais, qui renvoie vers mes autres projets, et qui peut héberger de petits extras (comme une page de politique de confidentialité pour un autre projet) sans dépendre d'une plateforme tierce. Je voulais aussi des statistiques de visites/clics simples et respectueuses de la vie privée, sans confier ces données à un tiers.

### Solution

Un site statique minimal (pas de build, pas de framework) avec une petite couche d'i18n côté client, déployé derrière [Caddy](https://caddyserver.com/) dans Docker pour l'HTTPS automatique. Facile à modifier, rapide à charger, peu coûteux à faire tourner.

Un petit service FastAPI auto-hébergé (`admin/`) gère un tableau de bord `/admin` protégé par mot de passe et enregistre les pages vues/clics rapportés par le script de suivi du site — aucune analytique tierce.

Hébergé sur un VPS OVH, tournant comme l'un des multiples conteneurs Docker sur ce serveur aux côtés de mes autres projets (chacun isolé dans son propre conteneur).

### Stack technique

- HTML/CSS/JS vanilla statique
- [Caddy](https://caddyserver.com/) pour l'HTTPS automatique et le reverse-proxy de `/admin` et `/api` vers le service de stats
- FastAPI + SQLAlchemy + PostgreSQL pour le backend stats/admin
- Docker, déployé sur un VPS OVH

### Structure

```
.
├── index.html                        # page principale
├── css/
│   ├── base.css                      # styles de base partagés
│   ├── home.css                      # styles de la page d'accueil
│   └── policy.css                    # styles de la page de politique de confidentialité
├── js/
│   ├── i18n.js                       # sélecteur de langue (FR/EN/PT/ES/RU/DE)
│   ├── main.js                       # animation d'apparition au scroll, menu mobile
│   └── track.js                      # envoie les événements pages vues/clics à /api/track
├── amazon-price-tracker/
│   └── policy/index.html             # politique de confidentialité du bot Amazon Price Tracker
├── admin/                            # backend stats/admin (FastAPI)
│   ├── app/
│   │   ├── main.py                   # routes, rapports mensuels/annuels planifiés
│   │   └── templates/                # login, stats, historique, rapports rendus côté serveur
│   ├── requirements.txt
│   └── Dockerfile
├── Caddyfile                         # config reverse proxy / HTTPS
├── Dockerfile                        # image du site statique
├── .env.example                      # modèle pour le .env côté serveur (ne jamais commit le vrai)
└── docker-compose.yml
```

### Stats / admin

`/admin` est un tableau de bord protégé par connexion (mots de passe hashés en bcrypt, cookie de session signé, limitation basique des tentatives de connexion) affichant les pages vues, visiteurs uniques, pages les plus vues et liens les plus cliqués (internes et externes) sur les 30 derniers jours. Les événements sont envoyés par `js/track.js` vers `POST /api/track` et stockés dans une base PostgreSQL dédiée — aucun cookie n'est posé pour les visiteurs, et aucune IP brute n'est stockée (un hash à rotation quotidienne est utilisé pour estimer les visiteurs uniques).

La session admin expire après 1 heure côté serveur quelle que soit l'activité, et c'est un cookie de session navigateur (pas de durée de vie persistante), donc fermer le navigateur déconnecte aussi.

`/admin/history` paginate à travers tous les événements enregistrés (50 par page) plutôt que de tout charger d'un coup. `/admin/reports` affiche des résumés mensuels et annuels, générés automatiquement par un planificateur interne le 1er de chaque mois et le 1er janvier.

#### Comptes et permissions

Les comptes vivent dans la table `users` (nom d'utilisateur, hash bcrypt du mot de passe, indicateur `is_owner`, liste des `resources` accordées). Le compte propriétaire est initialisé une fois à partir de `ADMIN_USERNAME`/`ADMIN_PASSWORD_HASH` au premier démarrage ; ensuite, tous les comptes (y compris le mot de passe du propriétaire) se gèrent depuis `/admin/users`, elle-même réservée au propriétaire.

- Le **propriétaire** (`is_owner=True`) voit tout : stats/historique/rapports du site, `/admin/users`, et chaque dashboard par ressource.
- Les **collaborateurs** n'ont pas l'indicateur `is_owner` et ne voient que les dashboards des ressources qui leur sont accordées (ex : `amazon_price_tracker` pour le bot Amazon Price Tracker, partagé avec visualbynoah) via `/admin/home`. Ils ne peuvent pas voir les analytics du site lui-même.
- `/admin/bots/amazon-price-tracker` affiche de vraies stats (utilisateurs, produits suivis, baisses/hausses de prix, changements récents, rapports mensuels/annuels) récupérées en HTTP depuis une petite API de stats interne tournant dans le projet `amazon-price-tracker-bot` — voir le README de ce projet pour le câblage (réseau Docker partagé, variables d'environnement `BOT_STATS_API_URL`/`BOT_STATS_TOKEN` ici). Si ce service est injoignable, la page affiche un message « service indisponible » plutôt que de planter.

### Lancer en local

```sh
docker compose up -d --build
```

Nécessite un fichier `.env` (voir `.env.example`) avec les identifiants de la base de stats, le nom d'utilisateur/hash bcrypt admin, et le secret de session.
