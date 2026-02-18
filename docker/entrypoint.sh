#!/usr/bin/env bash
VALID_COMMANDS=("speak" "download" "server")

DATA_DIR='/data'
COMMAND="$1"
shift

case "${COMMAND}" in
  speak)
    exec python3 -m piper --data-dir "${DATA_DIR}" "$@"
    ;;
  download)
    exec python3 -m piper.download_voices --data-dir "${DATA_DIR}" "$@"
    ;;
  server)
    # Télécharger le modèle français s'il n'existe pas
    echo "Checking French voice model..."
    python3 -m piper.download_voices --data-dir "${DATA_DIR}" fr_FR-siwis-medium
    
    # Lancer le serveur HTTP en production avec Gunicorn
    echo "Starting Piper HTTP server with Gunicorn..."
    exec gunicorn --bind 0.0.0.0:5000 --workers 2 --timeout 300 --access-logfile - "piper.http_server:app"
    ;;
  ""|help|-h|--help)
    echo "Usage: <command> [args...]"
    echo "Available commands:"
    echo "  speak        Synthesize audio from text"
    echo "  download     Download voices"
    echo "  server       Run HTTP server"
    exit 0
    ;;
  *)
    echo "Error: Unknown command '$COMMAND'"
    echo "Run with --help for usage."
    exit 1
    ;;
esac
