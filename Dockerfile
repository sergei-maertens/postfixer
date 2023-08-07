# This is a multi-stage build file, which means a stage is used to build
# the backend (dependencies), the frontend stack and a final production
# stage re-using assets from the build stages. This keeps the final production
# image minimal in size.

# Stage 1 - Backend build environment
# includes compilers and build tooling to create the environment

FROM python:3.10-slim-bookworm AS backend-build

RUN apt-get update && apt-get install -y --no-install-recommends \
        pkg-config \
        build-essential \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir /app/src

# Ensure we use the latest version of pip
RUN pip install pip setuptools -U
COPY ./requirements /app/requirements
RUN pip install -r requirements/production.txt


# Stage 3 - Build docker image suitable for production
FROM python:3.10-slim-bookworm

# Stage 3.1 - Set up the needed production dependencies
# install all the dependencies for GeoDjango
RUN apt-get update && apt-get install -y --no-install-recommends \
        procps \
        vim \
        mime-support \
        postgresql-client \
        gettext \
        # lxml deps
        # libxslt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./bin/docker_start.sh /start.sh

# Uncomment if you use celery
# COPY ./bin/celery_worker.sh /celery_worker.sh
# COPY ./bin/celery_beat.sh /celery_beat.sh
# COPY ./bin/celery_flower.sh /celery_flower.sh
RUN mkdir /app/log
RUN mkdir /app/media

VOLUME ["/app/log", "/app/media"]

# copy backend build deps
COPY --from=backend-build /usr/local/lib/python3.10 /usr/local/lib/python3.10
COPY --from=backend-build /usr/local/bin/uwsgi /usr/local/bin/uwsgi
# Uncomment if you use celery
# COPY --from=backend-build /usr/local/bin/celery /usr/local/bin/celery

# copy source code
COPY ./src /app/src

RUN useradd -M -u 1000 regex
RUN chown -R regex:regex /app

# drop privileges
USER regex

ARG COMMIT_HASH
ARG RELEASE=latest

ENV RELEASE=${RELEASE} \
    GIT_SHA=${COMMIT_HASH} \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=postfixer.conf.docker

ARG SECRET_KEY=dummy

# Run collectstatic and compilemessages, so the result is already included in
# the image
RUN python src/manage.py collectstatic --noinput \
    && python src/manage.py compilemessages

EXPOSE 8000
CMD ["/start.sh"]
