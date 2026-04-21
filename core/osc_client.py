# OSC = Open Sound Control, damit kommunizieren wir mit VRChat
import fancify_text
import uwuify
from data_manager import DataManager

try:
    from pythonosc import udp_client
    OSC_AVAILABLE = True
except ImportError:
    print("python-osc nicht installiert. OSC-Funktionen sind deaktiviert.")
    OSC_AVAILABLE = False


class OscClient:
    def __init__(self, host="127.0.0.1", port=9000):
        self.host = host
        self.port = port
        self.client = None
        self._connect()

    def _connect(self):
        if OSC_AVAILABLE:
            try:
                self.client = udp_client.SimpleUDPClient(self.host, self.port)
                print(f"OSC Client verbunden: {self.host}:{self.port}")
            except Exception as e:
                print(f"OSC Verbindungsfehler: {e}")
                self.client = None

    def update_connection(self, host, port):
        """Verbindung mit neuen Einstellungen neu aufbauen"""
        self.host = host
        self.port = port
        self._connect()

    def send_chatbox_message(self, message):
        """Sendet eine Nachricht in die VRChat Chatbox mit Font/uwuify Support"""

        if not self.client:
            print(f"[OSC nicht verfuegbar] Chatbox: '{message}'")
            return

        try:

            data_manager = DataManager()
            settings = data_manager.get_settings()
            font = settings.get("font")

            if font == "UwU":
                if "?" not in message and "!" not in message:
                    message += "."
                message = uwuify.uwu(message, flags=uwuify.SMILEY | uwuify.STUTTER)

            elif font:
                try:
                    message = fancify_text.fancify(message, font)
                except Exception as e:
                    print(f"[FONT ERROR] {e} → fallback used")

            self.client.send_message("/chatbox/input", [message, True])
            print(f"[OSC Chatbox] -> '{message}'")

        except Exception as e:
            print(f"OSC Chatbox Fehler: {e}")

    def send_avatar_parameter(self, parameter_name, value):
        """Steuert einen Avatar-Parameter (z.B. Emotes, visuelle Effekte)"""
        if self.client:
            try:
                address = f"/avatar/parameters/{parameter_name}"
                self.client.send_message(address, value)
                print(f"[OSC Avatar] {address} = {value}")
            except Exception as e:
                print(f"OSC Parameter Fehler: {e}")
        else:
            print(f"[OSC nicht verfuegbar] Avatar: {parameter_name} = {value}")
