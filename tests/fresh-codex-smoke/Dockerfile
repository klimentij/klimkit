FROM node:22-bookworm-slim

ARG CODEX_VERSION=0.134.0
ARG SKILLS_VERSION=1.5.9

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates git python3 ripgrep \
  && rm -rf /var/lib/apt/lists/*

RUN npm install -g "@openai/codex@${CODEX_VERSION}" "skills@${SKILLS_VERSION}" \
  && npm cache clean --force

WORKDIR /workspace

COPY smoke-entrypoint.sh /usr/local/bin/klimkit-fresh-codex-smoke
RUN chmod +x /usr/local/bin/klimkit-fresh-codex-smoke

ENTRYPOINT ["klimkit-fresh-codex-smoke"]
