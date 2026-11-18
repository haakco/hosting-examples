# An API with its own database

Two of your own container images as one system: an HTTP `api` and the PostgreSQL `db` it talks to. The api
names the database by reference, and Hosting works out the rest: the reference is the address and the
network grant, a non-HTTP port stays private, and each disk is its own claim at the path you give.

**Want Hosting to run the database for you instead?** Use a managed PostgreSQL database
(`databases.<key>.engine: postgres`). Hosting then owns backups, credentials and failover.

## What is in it

| Path | What it is |
| --- | --- |
| `hosting.yaml` | Both applications, their two disks and the password secret |
| `api/` | A tiny Python API: `GET /up` answers 200 when the database answers and 503 when it does not; `bin/report` prints the database size and is run nightly by `cron` |
| `db` | The image [`postgres-custom-image`](../postgres-custom-image/) builds: official PostgreSQL 18 plus HypoPG |

What Hosting infers, so the document does not say it:

| You write | Hosting works out |
| --- | --- |
| `run: {port: 8080, healthPath: /up}` | `api` is public, ready when `/up` answers |
| `run: {port: 5432, protocol: postgres}` | `db` is private: no public route, ready when the port accepts a connection |
| `DATABASE_URL: {service: db, field: url}` | `postgres://<db host>:5432`, and only `api` may reach `db` |
| Two `storage` entries | Two disks, each mounted at its path, kept across redeploys |

`PGUSER` and `PGPASSWORD` complete the connection: PostgreSQL clients read them when the URL leaves them out.

## Build and push

Replace `haakco/hosting-examples` with your own registry namespace here and in `hosting.yaml`.

```bash
docker build --platform linux/amd64 -t ghcr.io/haakco/hosting-examples/api:1 api
docker build --platform linux/amd64 -t ghcr.io/haakco/hosting-examples/postgres-hypopg:18-1 ../postgres-custom-image
docker push ghcr.io/haakco/hosting-examples/api:1
docker push ghcr.io/haakco/hosting-examples/postgres-hypopg:18-1
```

## Try it locally

```bash
docker network create example
docker run -d --name db --network example -e POSTGRES_PASSWORD=local \
  ghcr.io/haakco/hosting-examples/postgres-hypopg:18-1
docker run -d --name api --network example -p 8080:8080 \
  -e DATABASE_URL=postgres://db:5432 -e PGUSER=postgres -e PGPASSWORD=local \
  ghcr.io/haakco/hosting-examples/api:1
until curl -fsS localhost:8080/up; do sleep 1; done
docker exec api bin/report
docker rm -f api db && docker network rm example
```

## Use it on Hosting

Before importing, check the [object storage prerequisite](../README.md#the-hostingctl-sequence).

`<env>` is the environment's uuid and `<api>`/`<db>` the applications'
uuids, as `hostingctl environments` and `hostingctl application list <env>` print them. Every write takes
`--dry-run` to describe the change and send nothing, then `--confirm` to make it.

```bash
# 1. Install and sign in
npm i -g @haakco/hostingctl
hostingctl login --company <your-company>

# 2. Pick an environment, or create one for this example
hostingctl environments
hostingctl environment create --name "Api and own database" --package empty_environment --dry-run
hostingctl environment create --name "Api and own database" --package empty_environment --confirm

# 3. Private images only: store a registry connection, check it, and add `connection: <uuid>` under each
#    `image:` (public images need no connection). The token is read from stdin and never printed.
hostingctl registry-connections add --name ghcr --provider ghcr --host ghcr.io --username <you> \
  --repository-scope <you>/hosting-examples --confirm-auth-relationship --credential-stdin --dry-run
hostingctl registry-connections add --name ghcr --provider ghcr --host ghcr.io --username <you> \
  --repository-scope <you>/hosting-examples --confirm-auth-relationship --credential-stdin --confirm
hostingctl registry-connections check <connection-uuid> --repository <you>/hosting-examples/api --reference 1

# 4. Review (the preview lists what Hosting inferred and the secret still to set), set the password, apply
hostingctl environment configuration preview <env> --file hosting.yaml
# Save the draft so Hosting knows which secret to accept.
hostingctl environment configuration save <env> --file hosting.yaml --confirm
openssl rand -base64 32 > db-password && chmod 600 db-password
hostingctl environment secret write <env> --key db_password --value-source file --value-file db-password --confirm
hostingctl environment configuration apply <env> --file hosting.yaml --dry-run
hostingctl environment configuration apply <env> --file hosting.yaml --wait --confirm

# 5. Import each image, then deploy the release it prepared: db first, then api
hostingctl application list <env>
hostingctl application prepare-image <env> <db> --dry-run
hostingctl application prepare-image <env> <db> --confirm
hostingctl application deployment <env> <db>               # wait for the prepared release to show ready
hostingctl application deploy <env> <db> <release> --confirm
hostingctl application prepare-image <env> <api> --dry-run
hostingctl application prepare-image <env> <api> --confirm
hostingctl application deployment <env> <api>              # wait for the prepared release to show ready
hostingctl application deploy <env> <api> <release> --confirm

# 6. Status and logs
hostingctl environment show <env>
hostingctl application show <env> <api>
hostingctl logs live <env> --application <api>
hostingctl logs environment <env> --application <db>

# 7. List the services the document can reference, including `db`
hostingctl environment references <env>
```

### Make one change

Push `api:2`, change the api's `reference: "1"` to `reference: "2"`, and repeat steps 4 (preview and apply)
and 5 for `<api>` only. The database and its disks are untouched.

### Remove everything

```bash
# An environment you picked: remove both applications. Their disks are retained, not deleted.
hostingctl application remove <env> <api> --confirm
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

Hosting keeps both disks, but does not back them up, and copying a running database's files is not a backup.
Run `pg_dump` on a schedule into the `db_dumps` disk (mounted at `/dumps`) or into your own bucket, copy the
dumps somewhere outside this environment, and test a restore.

## Your responsibility

You are responsible for the licences of every image you import, and for what they contain, their security
updates and the database's upgrades between PostgreSQL major versions.
