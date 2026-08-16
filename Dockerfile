FROM caddy:alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY index.html /usr/share/caddy/index.html
