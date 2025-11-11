import os
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

import sys
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.normalise import (
    normalize_directory,
    get_audio_files,
    get_codec_for_extension,
    CODEC_MAP,
)


@pytest.fixture
def sample_music_dir(tmp_path):
    """
    We recreate a small test directory that mimics tests/musics_files but in a tmp_path so as not to break anything.
    """
    d = tmp_path / "musics_files"
    d.mkdir(parents=True)

    # creates some fake audio files
    (d / "track1.mp3").write_bytes(b"fake mp3")
    (d / "track2.wav").write_bytes(b"fake wav")
    (d / "readme.txt").write_text("not audio")

    return d

def test_get_audio_files(sample_music_dir):
    """
    L'application doit détecter uniquement les fichiers audio valides dans un dossier et ignorer les autres fichiers.
    """
    files = get_audio_files(str(sample_music_dir))
    assert "track1.mp3" in files
    assert "track2.wav" in files
    assert "readme.txt" not in files
    # S'assure qu'il n'y a que 2 fichiers audio
    assert len(files) == 2

@pytest.mark.parametrize(
    "ext,expected",
    [
        (".mp3", "libmp3lame"),
        (".MP3", "libmp3lame"),
        (".flac", "flac"),
        (".wav", "pcm_s16le"),
        (".unknown", "libmp3lame"),  # fallback
    ],
)
def test_get_codec_for_extension(ext, expected):
    """
    L'application doit utiliser le codec libmp3lame pour les fichiers au format .mp3.
    L'application doit reconnaître les extensions de fichiers sans tenir compte de la casse (majuscules/minuscules).
    L'application doit choisir automatiquement le codec flac pour les fichiers au format .flac.
    L'application doit choisir le codec pcm_s16le pour les fichiers audio .wav.
    L'application doit utiliser par défaut le codec libmp3lame lorsqu'un format de fichier n'est pas reconnu.
    """
    assert get_codec_for_extension(ext) == expected

def test_normalize_directory_creates_output_dir(sample_music_dir, tmp_path):
    """
    L'application doit créer automatiquement le dossier de sortie et générer un fichier normalisé pour chaque fichier audio détecté.
    """
    out_dir = tmp_path / "out"

    with patch("src.normalise.FFmpegNormalize") as mock_norm_cls:
        mock_norm = MagicMock()
        mock_norm_cls.return_value = mock_norm

        # Simulate the creation of output files
        def fake_add_media_file(input_path, output_path):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            # Creates a small simulated empty file
            Path(output_path).write_text("normalized")
        mock_norm.add_media_file.side_effect = fake_add_media_file

        normalize_directory(str(sample_music_dir), str(out_dir))

    assert out_dir.exists()
    # There should be two output files (mp3 + wav)
    out_files = {p.name for p in out_dir.iterdir()}
    assert "track1.mp3" in out_files
    assert "track2.wav" in out_files

def test_normalize_directory_calls_ffmpeg_normalize(sample_music_dir, tmp_path):
    """
    L'application doit appeler la bibliothèque ffmpeg_normalize pour chaque fichier audio à traiter.
    """
    out_dir = tmp_path / "out"

    with patch("src.normalise.FFmpegNormalize") as mock_norm_cls:
        mock_norm = MagicMock()
        mock_norm_cls.return_value = mock_norm

        normalize_directory(str(sample_music_dir), str(out_dir))

    # A normaliser must have been created for each audio file
    # sample_music_dir contains 2 audio files → 2 calls
    assert mock_norm_cls.call_count == 2
    # For each instance, add_media_file then run_normalisation
    assert mock_norm.add_media_file.call_count == 2
    assert mock_norm.run_normalization.call_count == 2

def test_normalize_directory_progress_callback(sample_music_dir, tmp_path):
    """
    L'application doit appeler la fonction de suivi de progression après chaque fichier traité afin de permettre la mise à jour d'une barre de progression.
    """
    out_dir = tmp_path / "out"
    calls = []

    def cb(current, total):
        calls.append((current, total))

    with patch("src.normalise.FFmpegNormalize") as mock_norm_cls:
        mock_norm = MagicMock()
        mock_norm_cls.return_value = mock_norm

        normalize_directory(str(sample_music_dir), str(out_dir), progress_callback=cb)

    # There are as many calls as there are audio files.
    assert len(calls) == 2
    # Last call = all finished
    assert calls[-1] == (2, 2)


def test_normalize_directory_no_files(tmp_path):
    """
    L'application doit gérer correctement le cas d'un dossier vide sans provoquer d'erreur. 
    """
    empty_dir = tmp_path / "empty"
    empty_dir.mkdir()

    # Should not raise an error even if the folder is empty
    with patch("src.normalise.FFmpegNormalize") as mock_norm_cls:
        normalize_directory(str(empty_dir))
        mock_norm_cls.assert_not_called()