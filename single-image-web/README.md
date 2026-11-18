# One web image

The smallest thing Hosting runs: one container image you publish, answering HTTP on one port. Hosting
imports the exact image, routes the environment's address to it and checks `/up` before it takes traffic.

```yaml
version: "1.24"
applications:
  web:
    runtime: client_image
    image: {registryHost: ghcr.io, repository: haakco/hosting-examples/single-image-web, reference: "1"}
    run: {port: 8080, healthPath: /up}
```

`runtime`, `image` and `run.port` are the minimum. `healthPath` defaults to `/`.

## Build and push

Replace `haakco/hosting-examples` with your own registry namespace here and in `hosting.yaml`.

```bash
docker build --platform linux/amd64 -t ghcr.io/haakco/hosting-examples/single-image-web:1 .
docker push ghcr.io/haakco/hosting-examples/single-image-web:1
```

## Try it locally

```bash
docker run -d --name web -p 8080:8080 ghcr.io/haakco/hosting-examples/single-image-web:1
curl -fsS localhost:8080/up
docker rm -f web
```

## Use it on Hosting

`<env>` is the environment's uuid and `<app>` an application's uuid, as `hostingctl environments` and
`hostingctl application list <env>` print them. Every write takes `--dry-run` to describe the change and send
nothing, then `--confirm` to make it.

```bash
# 1. Install and sign in
npm i -g @haakco/hostingctl
hostingctl login --company <your-company>

# 2. Pick an environment, or create one for this example
hostingctl environments
hostingctl environment create --name "Single image web" --dry-run
hostingctl environment create --name "Single image web" --confirm

# 3. Private image only: store a registry connection, check it, and add `connection: <uuid>` under `image:`
#    (a public image needs no connection). The token is read from stdin and never printed.
hostingctl registry-connections add --name ghcr --provider ghcr --host ghcr.io --username <you> \
  --repository-scope <you>/hosting-examples --confirm-auth-relationship --credential-stdin --dry-run
hostingctl registry-connections add --name ghcr --provider ghcr --host ghcr.io --username <you> \
  --repository-scope <you>/hosting-examples --confirm-auth-relationship --credential-stdin --confirm
hostingctl registry-connections check <connection-uuid> \
  --repository <you>/hosting-examples/single-image-web --reference 1

# 4. Review, then apply
hostingctl environment configuration preview <env> --file hosting.yaml
hostingctl environment configuration apply <env> --file hosting.yaml --dry-run
hostingctl environment configuration apply <env> --file hosting.yaml --wait --confirm

# 5. Import the image, then deploy the release it prepared
hostingctl application list <env>
hostingctl application prepare-image <env> <app> --dry-run
hostingctl application prepare-image <env> <app> --confirm
hostingctl application deployment <env> <app>            # shows the prepared release
hostingctl application deploy <env> <app> <release> --dry-run
hostingctl application deploy <env> <app> <release> --confirm

# 6. Status and logs
hostingctl environment show <env>
hostingctl application show <env> <app>
hostingctl logs live <env> --application <app>
hostingctl logs environment <env> --application <app>

# 7. What a document in this environment may reference
hostingctl environment references <env>
```

### Make one change

Push a new tag, change `reference: "1"` to `reference: "2"` in `hosting.yaml`, and repeat steps 4 and 5.
The running release keeps serving until you deploy the new one.

### Remove everything

```bash
# An environment you picked: remove the application (retained data is not deleted)
hostingctl application remove <env> <app> --dry-run
hostingctl application remove <env> <app> --confirm

# An environment you created for this example: cancel it now (--generation is in `environment show`)
hostingctl cancellation request <env> --reason "example finished" --timing now --generation <n> --dry-run
hostingctl cancellation request <env> --reason "example finished" --timing now --generation <n> --confirm

# The registry connection, if you made one: revoke it, then delete it
hostingctl registry-connections revoke <connection-uuid> --confirm
hostingctl registry-connections remove <connection-uuid> --confirm
```

## Your responsibility

You are responsible for the licences of every image you import, and for what it contains and its security
updates.
