#!/bin/bash
# Normalisation du volume de tous les fichiers audio d'un dossier

# Si un argument est fourni, on l'utilise comme dossier source
# Sinon, on prend le répertoire courant
SRC_DIR="${1:-.}"
DEST_DIR="$SRC_DIR/normalised"

mkdir -p "$DEST_DIR"

# Boucle sur tous les fichiers MP3 du dossier source
for f in "$SRC_DIR"/*.mp3; do
    # Vérifie que le fichier existe (évite les erreurs si aucun .mp3 n'est trouvé)
    [ -e "$f" ] || { echo "Aucun fichier mp3 trouvé dans $SRC_DIR"; break; }

    base=$(basename "$f")
    echo "Normalisation de $base ..."
    ffmpeg -i "$f" -af loudnorm=I=-16:TP=-1.5:LRA=11 "$DEST_DIR/$base"
done

echo "Normalisation terminée. Fichiers disponibles dans : $DEST_DIR"
