# Your own PostgreSQL image

Run PostgreSQL from an image you build, as one of your own applications on Hosting, with an extension the
managed PostgreSQL server does not offer. You run it: Hosting starts it, keeps its disk and keeps it
private, but does not manage its credentials, backups, upgrades or exports.

> **Status:** needs schema `1.25` (a client image's own disk at any path, and a private non-HTTP port), which
> is not released yet. The image builds and runs today; the `hosting.yaml` is refused until the schema ships.

**Want Hosting to run the database for you instead?** Use a managed PostgreSQL database
(`databases.<key>.engine: postgres`). Hosting then owns backups, credentials and failover, and you choose
from its extension catalogue.

## Build and push

```bash
docker build --platform linux/amd64 -t ghcr.io/acme/postgres-hypopg:18-1 .
docker push ghcr.io/acme/postgres-hypopg:18-1
```

## Try it locally

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=local ghcr.io/acme/postgres-hypopg:18-1
until docker exec pg pg_isready -U postgres; do sleep 1; done
docker exec pg psql -U postgres -v ON_ERROR_STOP=1 -c "CREATE EXTENSION hypopg;"
docker rm -f pg
```

## Use it on Hosting

```bash
npm i -g @haakco/hostingctl
hostingctl login
hostingctl environment configuration preview --file hosting.yaml acme-prod
hostingctl environment configuration apply --file hosting.yaml --wait --confirm acme-prod
```

Set the `db_password` secret when the preview asks for it. Your other applications reach the database
with a reference, which also grants the network access:

```yaml
env:
  DATABASE_URL: {service: db, field: url}
```

## Backups are yours

Hosting keeps the disk, but does not back it up, and copying a running database's files is not a backup.
Run `pg_dump` on a schedule into your own storage, and test a restore.

## Your responsibility

The image is yours, like your application code: what it contains, its licences, its security updates and
its upgrades between PostgreSQL major versions.
