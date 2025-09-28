#!/usr/bin/env bash
set -euo pipefail

# Script de limpieza TOTAL del entorno Docker local del proyecto LeyIA.
# ADVERTENCIA: Elimina contenedores, imágenes, redes y volúmenes asociados al proyecto.
# Úsalo sólo en entorno local de desarrollo.

PROJECT_NAME=${PROJECT_NAME:-alccia}
IMAGE_NAME=${IMAGE_NAME:-reflex-local}

echo "[clean] Deteniendo stack compose (si existe)..."
docker compose down -v --remove-orphans 2>/dev/null || true

echo "[clean] Eliminando contenedores manuales antiguos (si existen)..."
docker rm -f leyia-db reflex-app 2>/dev/null || true

echo "[clean] Eliminando red manual 'leyia-net' (si existe)..."
docker network rm leyia-net 2>/dev/null || true

# Borrar imágenes del proyecto (si no las usa otro contenedor)
if docker images | grep -q "$IMAGE_NAME"; then
  echo "[clean] Eliminando imagen $IMAGE_NAME"
  docker image rm -f "${IMAGE_NAME}" 2>/dev/null || true
fi

# Eliminar cualquier imagen dangling
echo "[clean] Eliminando imágenes dangling..."
docker image prune -f >/dev/null || true

# Volúmenes específicos del proyecto (si quedaran tras el down -v)
for vol in ${PROJECT_NAME}_pgdata ${PROJECT_NAME}_uploaded_files; do
  if docker volume ls -q | grep -qx "$vol"; then
    echo "[clean] Eliminando volumen $vol"
    docker volume rm "$vol" || true
  fi
done

# Limpia builder cache (opcional)
if [ "${PRUNE_BUILDER:-0}" = "1" ]; then
  echo "[clean] Limpiando builder cache (docker builder prune)..."
  docker builder prune -f || true
fi

# Limpieza general de recursos no usados
echo "[clean] docker system prune -f (recursos no usados)"
docker system prune -f >/dev/null || true

echo "[clean] Hecho. Estado actual mínimo listo para reconstruir."
echo "[clean] Para reconstruir desde cero:"
echo "    docker compose build --no-cache && docker compose up -d"
