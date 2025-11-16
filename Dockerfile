FROM lightdash/lightdash:latest

ARG RENDER_EXTERNAL_URL

ENV SITE_URL $RENDER_EXTERNAL_URL

COPY ./entrypoint.sh /usr/bin/entrypoint.sh
COPY lightdash.yaml /app/lightdash.yaml
COPY metadata.yaml /app/metadata.yaml

ENTRYPOINT ["/usr/bin/entrypoint.sh"]
CMD ["pnpm", "-F", "backend", "start"]
