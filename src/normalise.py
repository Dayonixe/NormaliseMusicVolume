import os
from ffmpeg_normalize import FFmpegNormalize

input_dir = "../musique"
output_dir = "../musique_normalisee"
os.makedirs(output_dir, exist_ok=True)

normalizer = FFmpegNormalize(
    target_level=-16.0,
    audio_codec="libmp3lame",   # important pour les MP3
    audio_bitrate="192k",       # optionnel, mais conseillé
    progress=True
)

for f in os.listdir(input_dir):
    if f.lower().endswith(('.mp3', '.wav', '.flac')):
        input_path = os.path.join(input_dir, f)
        output_path = os.path.join(output_dir, f)
        print(f"Normalisation de {f} ...")
        normalizer.add_media_file(input_path, output_path)

normalizer.run_normalization()
