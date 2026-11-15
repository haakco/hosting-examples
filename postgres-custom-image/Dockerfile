# A PostgreSQL 18 image for a Hosting database server, with one extra extension.
#
# It starts from the public CloudNativePG operand image, which already meets every
# requirement Hosting checks (binaries, user 26, PGDATA, locales), and adds HypoPG
# (hypothetical indexes, PostgreSQL licence) from the PostgreSQL apt repository.
# Change the package line to add the extension you need.
FROM ghcr.io/cloudnative-pg/postgresql:18-standard-trixie@sha256:23719505c7cc417b043ffd9998b44ab8d57fec1d92f0bf11b231a1754a5962f2

USER root
RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-18-hypopg \
 && rm -rf /var/lib/apt/lists/*
USER 26
