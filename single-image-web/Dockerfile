# The smallest web image Hosting can run: static files served by nginx as a non-root user on port 8080.
# /up is the readiness path hosting.yaml names.
FROM nginxinc/nginx-unprivileged:1.29-alpine@sha256:0c79d56aee561a1d81c63f00eee5fb5fe29279560cdc55e91425133104c7fbe6

COPY index.html /usr/share/nginx/html/index.html
COPY up /usr/share/nginx/html/up
