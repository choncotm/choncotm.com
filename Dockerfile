FROM caddy:alpine

COPY Caddyfile /etc/caddy/Caddyfile
COPY index.html /usr/share/caddy/index.html
COPY css/ /usr/share/caddy/css/
COPY js/ /usr/share/caddy/js/
COPY amazon-price-tracker/ /usr/share/caddy/amazon-price-tracker/
