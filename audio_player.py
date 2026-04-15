import pygame
from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from data_manager import get_data_manager

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except Exception as e:
    print(f"Metadaten-Engine (pygame) konnte nicht gestartet werden: {e}")
    PYGAME_AVAILABLE = False


def get_audio_duration(file_path):
    """Berechnet die Länge eines Sounds in M:SS"""
    try:
        if not PYGAME_AVAILABLE:
            return "0:00"
        sound = pygame.mixer.Sound(file_path)
        total_seconds = int(sound.get_length())
        return f"{total_seconds // 60}:{total_seconds % 60:02d}"
    except Exception:
        return "0:00"


def get_audio_outputs():
    """Gibt alle verfügbaren Ausgabegeräte als Liste von Strings zurück"""
    devices = QMediaDevices.audioOutputs()
    return [d.description() for d in devices] or ["Default Output"]


class AudioPlayer:
    def __init__(self):
        self.data_manager = get_data_manager()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        settings = self.data_manager.get_settings()

        initial_vol = settings.get("volume", 75) / 100.0
        self.audio_output.setVolume(initial_vol)

        self._apply_output_device()

    def _apply_output_device(self):
        """Sucht das gespeicherte Gerät und weist es dem Output zu"""
        settings = self.data_manager.get_settings()
        saved_name = settings.get("output_device", "")
        devices = QMediaDevices.audioOutputs()

        selected_device = None

        if saved_name:
            for d in devices:
                if d.description() == saved_name:
                    selected_device = d
                    break

        if selected_device is None and devices:
            selected_device = devices[0]

        if selected_device:
            if self.audio_output.device() != selected_device:
                self.audio_output.setDevice(selected_device)

    def play_sound(self, file_path):
        """Spielt einen Sound über das gewählte Gerät ab"""
        settings = self.data_manager.get_settings()

        if not settings.get("enable_output", False):
            return

        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self.player.stop()

        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.play()

    def stop_all(self):
        """Stoppt die aktuelle Wiedergabe sofort"""
        self.player.stop()

    def set_volume(self, volume_percent):
        """Passt die Lautstärke während der Laufzeit an"""
        self.audio_output.setVolume(volume_percent / 100.0)

    def set_output_device(self, device_name):
        """
        Ändert das Ausgabegerät global.
        Sollte nur aufgerufen werden, wenn der User die Settings ändert.
        """
        settings = self.data_manager.get_settings()
        settings["output_device"] = device_name
        self.data_manager.update_settings("output_device", device_name)

        self._apply_output_device()