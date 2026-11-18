# Hosting examples

Worked examples for [HaakCo Hosting](https://github.com/haakco). Each directory is one example with a
README, a `hosting.yaml` and any `Dockerfile`, plus the full `hostingctl` commands from setup to removal.

| Example | Shows | Deployable |
| --- | --- | --- |
| [`single-image-web`](single-image-web/) | The smallest web application: one image, one port, a readiness path | Yes, schema `1.24` |
| [`postgres-custom-image`](postgres-custom-image/) | Your own PostgreSQL image, run as one of your applications, with one extra extension | Yes, schema `1.25` |
| [`api-and-own-database`](api-and-own-database/) | An API and its own PostgreSQL: a reference, a private port, two disks and a nightly task | Yes, schema `1.25` |

## The `hostingctl` sequence

Every example follows the same steps; its README has the exact commands.

1. Install and sign in: `npm i -g @haakco/hostingctl`, then `hostingctl login --company <your-company>`.
2. Pick an environment (`hostingctl environments`) or create one (`hostingctl environment create --name …`).
3. For a private image, add a registry connection (`hostingctl registry-connections add …`) and `check` it.
4. Review and apply: `hostingctl environment configuration preview <env> --file hosting.yaml`, then
   `apply` with `--dry-run` before `--confirm`.
5. Import and deploy each image: `hostingctl application prepare-image --confirm`, then `application deploy --confirm`.
6. Status and logs: `hostingctl environment show <env>`, `hostingctl logs live <env> --application <app>`.
7. What the environment may reference: `hostingctl environment references <env>`.
8. Make one change, preview and apply it again.
9. Remove everything: `hostingctl application remove`, or `hostingctl cancellation request` for an environment
   made for the example, and revoke then remove the registry connection.

Every write takes `--dry-run` to describe the change and send nothing, then `--confirm` to make it.

## Your images, your licences, your backups

You are responsible for the licences of every image you import. A database you run in your own image is
yours to back up: Hosting keeps its disk but does not back it up, and copying a running database's files is
not a backup. Use `pg_dump` into a dumps disk or your own bucket, or use a managed database, where Hosting
owns backups.

## Checks

CI builds every `Dockerfile`, starts each example's images, and validates every `hosting.yaml` against the
schema Hosting publishes for its `version` (`https://hosting.haak.co/api/v1/hosting/schemas/<version>`). Run the
schema check locally with `scripts/validate-hosting-yaml.sh`.
