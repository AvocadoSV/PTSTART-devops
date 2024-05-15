FROM postgres:13

ENV POSTGRES_USER=postgres
ENV POSTGRES_PASSWORD=1234
ENV POSTGRES_DB=replication

COPY init.sql /docker-entrypoint-initdb.d/
