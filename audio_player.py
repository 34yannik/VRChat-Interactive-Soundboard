import threading
import pygame

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices

from data_manager import get_data_manager

try:
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except Exception as e:
    print(f"pygame nicht verfuegbar: {e}")
    PYGAME_AVAILABLE = False


def get_audio_duration(file_path):
    try:
        if not PYGAME_AVAILABLE:
            return "0:00"
        sound = pygame.mixer.Sound(file_path)
        total_seconds = int(sound.get_length())
        return f"{total_seconds // 60}:{total_seconds % 60:02d}"
    except Exception:
        return "0:00"


def get_audio_inputs():
    devices = QMediaDevices.audioInputs()
    return [d.description() for d in devices] or ["Default Input"]


def get_audio_outputs():
    devices = QMediaDevices.audioOutputs()
    return [d.description() for d in devices] or ["Default Output"]


class AudioPlayer:

    def __init__(self):
        self.data_manager = get_data_manager()

        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()

        self.player.setAudioOutput(self.audio_output)

        self.audio_output.setVolume(
            self.data_manager.get_settings().get("volume", 75) / 100.0
        )

        self._apply_output_device()

    def _apply_output_device(self):
        settings = self.data_manager.get_settings()
        saved_name = settings.get("output_device", "")

        devices = QMediaDevices.audioOutputs()

        selected = None

        if saved_name:
            for d in devices:
                if d.description() == saved_name:
                    selected = d
                    break

        if selected is None and devices:
            selected = devices[0]

        if selected:
            self.audio_output.setDevice(selected)

    def play_sound(self, file_path):
        if not self.data_manager.get_settings().get("enable_output", False):
            return

        self._apply_output_device()

        self.player.setSource(QUrl.fromLocalFile(file_path))
        self.player.play()

    def stop_all(self):
        self.player.stop()

    def set_volume(self, volume_percent):
        self.audio_output.setVolume(volume_percent / 100.0)

    def set_output_device(self, device_name):
        settings = self.data_manager.get_settings()
        settings["output_device"] = device_name
        self.data_manager.save_data()
        self._apply_output_device()