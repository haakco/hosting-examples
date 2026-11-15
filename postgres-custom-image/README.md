# Your own PostgreSQL image

Run a Hosting database server from a PostgreSQL image you build, with an extension the standard offering
does not include. Hosting still manages credentials, backups and upgrades within the major version.

> **Status:** needs schema `1.25` (`databases.<key>.image`), which is not released yet. The image builds
> and runs today; the `hosting.yaml` is refused until the schema ships.

## Requirements

- `linux/amd64`, the same PostgreSQL major as your server (today 18).
- PostgreSQL server binaries on `PATH`, `du`, user ID 26 and a writable `/var/lib/postgresql/data`.
- No backup tools: Hosting runs backups beside the database, not in your image.
- Your image's entrypoint and command are ignored. Hosting starts PostgreSQL itself.

Starting `FROM` the CloudNativePG image, as this example does, meets all of these.

## Build and push

```bash
docker build --platform linux/amd64 -t ghcr.io/acme/postgres-hypopg:18-1 .
docker push ghcr.io/acme/postgres-hypopg:18-1
```

## Try it locally

```bash
docker run --rm --entrypoint bash ghcr.io/acme/postgres-hypopg:18-1 -c \
  'initdb -D /tmp/d -U postgres >/dev/null && pg_ctl -D /tmp/d -o "-k /tmp" -w start >/dev/null && psql -h /tmp -U postgres -v ON_ERROR_STOP=1 -c "CREATE EXTENSION hypopg;" && test "$(id -u)" = 26'
```

## Use it on Hosting

```bash
npm i -g @haakco/hostingctl
hostingctl login
hostingctl environment configuration preview --file hosting.yaml acme-prod
hostingctl environment configuration apply --file hosting.yaml --wait --confirm acme-prod
```

Changing the image restarts the database server; the preview says so.

## Switch back

Remove the `image:` line and apply again. The server returns to the platform image.

## Your responsibility

The image is yours, like your application code: what it contains, its licences and its updates. Hosting
checks that it is compatible and reports why if it fails to start.
