import threading

# pygame wird fuer Audio genutzt
try:
    import pygame
    pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
    PYGAME_AVAILABLE = True
except Exception as e:
    print(f"pygame nicht verfuegbar: {e}")
    PYGAME_AVAILABLE = False


def get_audio_duration(file_path):
    """Gibt die Laenge einer Audio-Datei als String zurueck (z.B. '0:03')"""
    try:
        if not PYGAME_AVAILABLE:
            return "0:00"
        sound = pygame.mixer.Sound(file_path)
        total_seconds = int(sound.get_length())
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}:{seconds:02d}"
    except Exception:
        return "0:00"


class AudioPlayer:
    def __init__(self):
        self.volume = 0.75  # Lautstaerke von 0.0 bis 1.0
        self.currently_playing = []  # Liste aller aktiven Sound-Objekte

    def set_volume(self, volume_percent):
        """Setzt die Lautstaerke, volume_percent ist 0 bis 100"""
        self.volume = volume_percent / 100.0

    def play_sound(self, file_path):
        """Spielt einen Sound in einem separaten Thread ab"""
        if not PYGAME_AVAILABLE:
            print(f"[Simuliere Abspielen]: {file_path}")
            return
        play_thread = threading.Thread(target=self._play_in_thread, args=(file_path,), daemon=True)
        play_thread.start()

    def _play_in_thread(self, file_path):
        try:
            sound = pygame.mixer.Sound(file_path)
            sound.set_volume(self.volume)
            channel = sound.play()
            self.currently_playing.append(sound)
            # Warten bis der Sound fertig ist, dann aus Liste entfernen
            if channel:
                while channel.get_busy():
                    pygame.time.wait(100)
            if sound in self.currently_playing:
                self.currently_playing.remove(sound)
        except Exception as e:
            print(f"Fehler beim Abspielen von '{file_path}': {e}")

    def stop_all(self):
        """Stoppt alle laufenden Sounds"""
        if PYGAME_AVAILABLE:
            pygame.mixer.stop()
        self.currently_playing.clear()
