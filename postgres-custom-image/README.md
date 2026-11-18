# Your own PostgreSQL image

Run PostgreSQL from an image you build, as one of your own applications on Hosting, with an extension the
managed PostgreSQL server does not offer. You run it: Hosting starts it, keeps its disk and keeps it
private, but does not manage its credentials, backups, upgrades or exports.

**Want Hosting to run the database for you instead?** Use a managed PostgreSQL database
(`databases.<key>.engine: postgres`). Hosting then owns backups, credentials and failover, and you choose
from its extension catalogue.

To see an application using this database, follow [`api-and-own-database`](../api-and-own-database/).

## Build and push

Replace `haakco/hosting-examples` with your own registry namespace here and in `hosting.yaml`.

```bash
docker build --platform linux/amd64 -t ghcr.io/haakco/hosting-examples/postgres-hypopg:18-1 .
docker push ghcr.io/haakco/hosting-examples/postgres-hypopg:18-1
```

## Try it locally

```bash
docker run -d --name pg -e POSTGRES_PASSWORD=local ghcr.io/haakco/hosting-examples/postgres-hypopg:18-1
until docker exec pg pg_isready -U postgres; do sleep 1; done
docker exec pg psql -U postgres -v ON_ERROR_STOP=1 -c "CREATE EXTENSION hypopg;"
docker rm -f pg
```

## Use it on Hosting

Before importing, check the [object storage prerequisite](../README.md#the-hostingctl-sequence).

`<env>` is the environment's uuid and `<db>` the application's uuid, as
`hostingctl environments` and `hostingctl application list <env>` print them. Every write takes `--dry-run`
to describe the change and send nothing, then `--confirm` to make it.

```bash
# 1. Install and sign in
npm i -g @haakco/hostingctl
hostingctl login --company <your-company>

# 2. Pick an environment, or create one for this example
hostingctl environments
hostingctl environment create --name "Own PostgreSQL" --package empty_environment --dry-run
hostingctl environment create --name "Own PostgreSQL" --package empty_environment --confirm

# 3. Private image only: store a registry connection, check it, and add `connection: <uuid>` under `image:`
#    (a public image needs no connection). The token is read from stdin and never printed.
hostingctl registry-connections add --name ghcr --provider ghcr --host ghcr.io --username <you> \
  --repository-scope <you>/hosting-examples --confirm-auth-relationship --credential-stdin --dry-run
hostingctl registry-connections add --name ghcr --provider ghcr --host ghcr.io --username <you> \
  --repository-scope <you>/hosting-examples --confirm-auth-relationship --credential-stdin --confirm
hostingctl registry-connections check <connection-uuid> \
  --repository <you>/hosting-examples/postgres-hypopg --reference 18-1

# 4. Review, set the password, then apply
hostingctl environment configuration preview <env> --file hosting.yaml
# Save the draft so Hosting knows which secret to accept.
hostingctl environment configuration save <env> --file hosting.yaml --confirm
openssl rand -base64 32 > db-password && chmod 600 db-password
hostingctl environment secret write <env> --key db_password --value-source file --value-file db-password --confirm
hostingctl environment configuration apply <env> --file hosting.yaml --dry-run
hostingctl environment configuration apply <env> --file hosting.yaml --wait --confirm

# 5. Import the image, then deploy the release it prepared
hostingctl application list <env>
hostingctl application prepare-image <env> <db> --dry-run
hostingctl application prepare-image <env> <db> --confirm
hostingctl application deployment <env> <db>               # wait for the prepared release to show ready
hostingctl application deploy <env> <db> <release> --confirm

# 6. Status and logs
hostingctl environment show <env>
hostingctl application show <env> <db>
hostingctl logs live <env> --application <db>

# 7. List the services the document can reference, including `db`
hostingctl environment references <env>
```

Your other applications reach the database with a reference, which also grants the network access:

```yaml
env:
  DATABASE_URL: {service: db, field: url}
```

### Make one change

Add an extension to the `Dockerfile`, push it as `18-2`, change `reference: "18-1"` to `reference: "18-2"`,
and repeat steps 4 (preview and apply) and 5. The data disk is kept across the redeploy.

### Remove everything

```bash
# An environment you picked: remove the application. Its disk is retained, not deleted.
hostingctl application remove <env> <db> --confirm

# An environment you created for this example: cancel it now (--generation is in `environment show`)
hostingctl cancellation request <env> --reason "example finished" --timing now --generation <n> --dry-run
hostingctl cancellation request <env> --reason "example finished" --timing now --generation <n> --confirm

# The registry connection, if you made one: revoke it, then delete it
hostingctl registry-connections revoke <connection-uuid> --confirm
hostingctl registry-connections remove <connection-uuid> --confirm
rm db-password
```

## Backups are yours

Hosting keeps the disk, but does not back it up, and copying a running database's files is not a backup.
Run `pg_dump` on a schedule into a dumps disk (as [`api-and-own-database`](../api-and-own-database/) does) or
into your own bucket, copy the dumps somewhere outside this environment, and test a restore.

## Your responsibility

You are responsible for the licences of every image you import, and for what it contains, its security
updates and its upgrades between PostgreSQL major versions.
