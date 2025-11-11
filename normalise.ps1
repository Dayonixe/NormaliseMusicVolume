# Normalisation du volume de tous les fichiers MP3 d'un dossier
# Utilise ffmpeg avec le filtre loudnorm (EBU R128)

param(
    [string]$SourceDir = "."
)

# Crée le dossier de sortie "normalised" dans le même répertoire
$DestDir = Join-Path $SourceDir "normalised"

if (!(Test-Path $DestDir)) {
    New-Item -ItemType Directory -Path $DestDir | Out-Null
}

# Récupère tous les fichiers MP3 du dossier
$files = Get-ChildItem -Path $SourceDir -Filter *.mp3 -File

if ($files.Count -eq 0) {
    Write-Host "Aucun fichier MP3 trouvé dans $SourceDir"
    exit
}

foreach ($f in $files) {
    Write-Host "Normalisation de $($f.Name)..."
    $output = Join-Path $DestDir $f.Name
    ffmpeg -hide_banner -loglevel error -i $f.FullName -af "loudnorm=I=-16:TP=-1.5:LRA=11" "$output"
}

Write-Host "Normalisation terminée. Fichiers disponibles dans : $DestDir"
