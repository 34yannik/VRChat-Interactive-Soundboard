import pygame
from PySide6.QtCore import QUrl, QPropertyAnimation, QEasingCurve, QTimer
from PySide6.QtMultimedia import QMediaPlayer, QAudioOutput, QMediaDevices
from core.data_manager import get_data_manager

try:
    if not pygame.mixer.get_init():
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except Exception as e:
    print(f"pygame init failed: {e}")
    PYGAME_AVAILABLE = False


def get_audio_duration(file_path):
    try:
        if not PYGAME_AVAILABLE:
            return "0:00"
        sound = pygame.mixer.Sound(file_path)
        total_seconds = int(sound.get_length())
        return f"{total_seconds // 60}:{total_seconds % 60:02d}"
    except (pygame.error, FileNotFoundError, OSError):
        return "0:00"


def get_audio_outputs():
    devices = QMediaDevices.audioOutputs()
    return [d.description() for d in devices] or ["Default Output"]


class AudioPlayer:
    def __init__(self):
        self.data_manager = get_data_manager()
        self.player = QMediaPlayer()
        self.audio_output = QAudioOutput()
        self.player.setAudioOutput(self.audio_output)

        settings = self.data_manager.get_settings()
        self.master_volume = settings.get("volume", 75)
        self.audio_output.setVolume(self.master_volume / 100.0)
        self._apply_output_device()

        self._fade_animation = QPropertyAnimation(self.audio_output, b"volume")
        self._fade_animation.setEasingCurve(QEasingCurve.Type.Linear)
        self._fade_animation.finished.connect(self._on_fade_finished)
        self._pending_stop = False
        self._current_sound_volume = 100

        self.player.durationChanged.connect(self._on_duration_changed)
        self._current_duration = 0

        # Store timer references to prevent garbage collection
        self._pending_timers = []

    def _apply_output_device(self):
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

    def _combined_volume(self, sound_volume):
        return (self.master_volume / 100.0) * (sound_volume / 100.0)

    def _fade_out(self, duration_ms=30, then_stop=False):
        if self._fade_animation.state() == QPropertyAnimation.State.Running:
            self._fade_animation.stop()
        self._fade_animation.setDuration(duration_ms)
        self._fade_animation.setStartValue(self.audio_output.volume())
        self._fade_animation.setEndValue(0.0)
        self._pending_stop = then_stop
        self._fade_animation.start()

    def _fade_in(self, target_volume, duration_ms=30):
        if self._fade_animation.state() == QPropertyAnimation.State.Running:
            self._fade_animation.stop()
        self._fade_animation.setDuration(duration_ms)
        self._fade_animation.setStartValue(0.0)
        self._fade_animation.setEndValue(target_volume)
        self._fade_animation.start()

    def _on_fade_finished(self):
        if self._pending_stop:
            self.player.stop()
            self._pending_stop = False

    def _on_duration_changed(self, duration_ms):
        self._current_duration = duration_ms

    def _get_duration_ms(self, file_path):
        try:
            if PYGAME_AVAILABLE:
                sound = pygame.mixer.Sound(file_path)
                return int(sound.get_length() * 1000)
        except (pygame.error, FileNotFoundError, OSError):
            pass
        return 0

    def play_sound(self, file_path, sound_volume=100):
        settings = self.data_manager.get_settings()
        if not settings.get("enable_output", False):
            return

        duration_ms = self._get_duration_ms(file_path)

        if duration_ms < 500 and PYGAME_AVAILABLE:
            self._play_short_pygame(file_path, sound_volume)
        else:
            self._play_long_qt(file_path, sound_volume)

    def _play_short_pygame(self, file_path, sound_volume):
        try:
            volume_factor = self._combined_volume(sound_volume)
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(min(1.0, volume_factor))
            sound.play()
        except (pygame.error, FileNotFoundError, OSError) as e:
            print(f"pygame playback failed: {e}")
            self._play_long_qt(file_path, sound_volume)

    def _play_long_qt(self, file_path, sound_volume):
        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self._fade_out(duration_ms=30, then_stop=True)

            # Create and store timer reference
            timer = QTimer()
            timer.setSingleShot(True)
            timer.timeout.connect(
                lambda fp=file_path, sv=sound_volume: self._start_qt_sound(fp, sv)
            )
            self._pending_timers.append(timer)
            timer.start(40)
        else:
            self._start_qt_sound(file_path, sound_volume)

    def _start_qt_sound(self, file_path, sound_volume):
        try:
            self.player.stop()
            self.audio_output.setVolume(0.0)
            self.player.setSource(QUrl.fromLocalFile(file_path))
            self.player.play()
            target_vol = self._combined_volume(sound_volume)
            self._current_sound_volume = sound_volume

            # Create and store timer reference
            fade_timer = QTimer()
            fade_timer.setSingleShot(True)
            fade_timer.timeout.connect(lambda tv=target_vol: self._fade_in(tv, duration_ms=30))
            self._pending_timers.append(fade_timer)
            fade_timer.start(10)

            # Cleanup old timers
            self._pending_timers = [t for t in self._pending_timers if t.isActive()]
        except (FileNotFoundError, OSError) as e:
            print(f"Error starting Qt sound: {e}")

    def stop_all(self):
        # Stop all pending timers
        for timer in self._pending_timers:
            timer.stop()
        self._pending_timers.clear()

        if self.player.playbackState() != QMediaPlayer.PlaybackState.StoppedState:
            self._fade_out(duration_ms=30, then_stop=True)
        else:
            self.player.stop()

        if PYGAME_AVAILABLE:
            pygame.mixer.stop()

    def set_volume(self, volume_percent):
        self.master_volume = volume_percent
        target = self._combined_volume(self._current_sound_volume)
        self._fade_in(target, duration_ms=20)

    def set_output_device(self, device_name):
        settings = self.data_manager.get_settings()
        settings["output_device"] = device_name
        self.data_manager.update_settings("output_device", device_name)
        self._apply_output_device()