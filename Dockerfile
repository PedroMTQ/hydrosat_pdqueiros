FROM python:3.11.3-bullseye AS build

# RUN pip install \
#     dagster \
#     dagster-postgres \
#     dagster-docker

# installs uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

RUN ls
WORKDIR /opt/dagster/app
RUN ls
COPY ./uv.lock /opt/dagster/app/uv.lock
COPY ./pyproject.toml /opt/dagster/app/pyproject.toml
COPY ./README.md /opt/dagster/app/README.md

# Extract version and add to a __version__ file which will be read by the service later
RUN echo $(grep -m 1 'version' /opt/dagster/app/pyproject.toml | sed -E 's/version = "(.*)"/\1/') > /opt/dagster/app/__version__

# copying source code
COPY ./src/ /opt/dagster/app/src/

# installs package
RUN uv sync --frozen
ENV PATH="/opt/dagster/app/.venv/bin:$PATH"


# Final
FROM build
RUN apt autoremove -y && apt clean -y






