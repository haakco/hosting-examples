# Your own PostgreSQL 18, run by you on Hosting as an ordinary container image, with one extra extension.
#
# It starts from the official PostgreSQL image, which creates the database on first start from
# POSTGRES_PASSWORD, and adds HypoPG (hypothetical indexes, PostgreSQL licence) from the PostgreSQL apt
# repository that image already uses. Change the package line to add the extension you need.
FROM postgres:18-trixie@sha256:2ea8630df176ad090ec92136dee850397c5af8781e4bcf2e4162593691c61bbc

RUN apt-get update \
 && apt-get install -y --no-install-recommends postgresql-18-hypopg \
 && rm -rf /var/lib/apt/lists/*
