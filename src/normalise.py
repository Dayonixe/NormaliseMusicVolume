import os
from ffmpeg_normalize import FFmpegNormalize

# Dictionary for choosing the right codec according to the extension
CODEC_MAP = {
    ".mp3": "libmp3lame",
    ".flac": "flac",
    ".wav": "pcm_s16le",
    ".m4a": "aac",
    ".aac": "aac",
    ".ogg": "libvorbis"
}

def get_audio_files(input_dir):
    """
    Returns the list of supported audio files in the folder.
    :param input_dir: Folder containing the files to be standardised
    """
    return [
        f for f in os.listdir(input_dir)
        if f.lower().endswith(tuple(CODEC_MAP.keys()))
    ]

def get_codec_for_extension(ext: str) -> str:
    """
    Returns the codec suitable for an extension (with fallback).
    :param ext: File extension
    """
    ext = ext.lower()
    return CODEC_MAP.get(ext, "libmp3lame")

def normalize_directory(input_dir, output_dir=None, target_level=-16.0, progress_callback=None):
    """
    Normalises the volume of all audio files in a directory.
    :param input_dir: Folder containing the files to be standardised
    :param output_dir: Output folder (created if it does not exist)
    :param target_level: Normalisation level in LUFS (default -16)
    :param progress_callback: Function called after each file processed (e.g. to update a progress bar)
    """

    # Check that the directory exists
    if not os.path.isdir(input_dir):
        raise FileNotFoundError(f"The folder '{input_dir}' does not exist.")

    # If no output folder is specified, a folder named ‘_normalised’ is created
    if output_dir is None:
        output_dir = os.path.join(input_dir, "_normalised")
    os.makedirs(output_dir, exist_ok=True)

    # List of audio files to be processed
    files = get_audio_files(input_dir)

    total_files = len(files)
    if total_files == 0:
        print("No audio files found.")
        return

    # File normalisation
    print(f"Normalising {total_files} files...\n")

    for index, filename in enumerate(files, start=1):
        input_path = os.path.join(input_dir, filename)
        output_path = os.path.join(output_dir, filename)

        _, ext = os.path.splitext(filename)
        audio_codec = get_codec_for_extension(ext)

        print(f"[{index}/{total_files}] {filename} ...")

        normalizer = FFmpegNormalize(
            target_level=target_level,
            audio_codec=audio_codec,
            audio_bitrate="192k",
            progress=False
        )

        normalizer.add_media_file(input_path, output_path)
        normalizer.run_normalization()

        # Progress callback (for the graphical interface)
        if progress_callback:
            progress_callback(index, total_files)

    print("\nNormalisation completed !")