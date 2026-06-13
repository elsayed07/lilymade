#!/bin/sh
# Nightly backup of the Postgres database and uploaded media.
# Run on the host via cron, e.g.:
#   0 3 * * *  /srv/lilymade/scripts/backup.sh >> /var/log/lilymade-backup.log 2>&1
#
# Keeps the last RETENTION_DAYS of dumps locally. For off-site safety, sync
# BACKUP_DIR to object storage (Backblaze B2 / S3) — see the commented rclone line.
set -eu

BACKUP_DIR="${BACKUP_DIR:-/srv/lilymade/backups}"
RETENTION_DAYS="${RETENTION_DAYS:-14}"
STAMP="$(date +%Y%m%d-%H%M%S)"
COMPOSE="${COMPOSE:-docker compose}"

mkdir -p "$BACKUP_DIR"

# Database: pg_dump from inside the db container (custom format = compressed).
$COMPOSE exec -T db sh -c 'pg_dump -U "$POSTGRES_USER" -d "$POSTGRES_DB" -Fc' \
  > "$BACKUP_DIR/db-$STAMP.dump"

# Media: tar the uploaded images out of the backend container.
$COMPOSE exec -T backend tar -czf - -C /app media \
  > "$BACKUP_DIR/media-$STAMP.tar.gz"

# Prune old local backups.
find "$BACKUP_DIR" -name 'db-*.dump' -mtime "+$RETENTION_DAYS" -delete
find "$BACKUP_DIR" -name 'media-*.tar.gz' -mtime "+$RETENTION_DAYS" -delete

# Off-site (recommended): configure rclone once, then uncomment:
# rclone copy "$BACKUP_DIR" "b2:lilymade-backups" --max-age 24h

echo "Backup complete: db-$STAMP.dump, media-$STAMP.tar.gz"
