# VRC Interact Soundboard

Ein Soundboard speziell fuer VRChat - steuert Sound, Chatbox und Avatar-Parameter ueber eine einzige Oberflaeche.

## Features

- **Collections** - Sounds in Sammlungen (Gaming Memes, Roleplay FX, etc.) organisieren
- **Pages** - Mehrere Seiten pro Collection (Page 1, Page 2, Voice Mods...)
- **Sound abspielen** - MP3, WAV, OGG, FLAC per Klick oder Hotkey
- **Wellenform-Animation** - Visuelle Rueckmeldung beim Abspielen
- **OSC Chatbox** - Automatisch eine Nachricht in VRChat senden wenn ein Sound spielt
- **VRChat Status** - Zeigt ob VRChat verbunden ist
- **Suche** - Sounds nach Name suchen
- **Einstellungen** - OSC Host und Port konfigurieren

## Installation

```bash
# 1. Python 3.11 vorausgesetzt

# 2. Abhaengigkeiten installieren
pip install -r requirements.txt

# 3. Starten
python main.py
```

## Projektstruktur

```
vrc_soundboard/
├── main.py              # Einstiegspunkt
├── main_window.py       # Hauptfenster - verbindet alles
├── sidebar_widget.py    # Linke Leiste mit Collections
├── topbar_widget.py     # Obere Leiste (Suche, Lautstaerke, Status)
├── pages_tabbar.py      # Tab-Leiste (Page 1, Page 2...)
├── sound_grid.py        # Das Grid mit allen Sound-Karten
├── sound_card.py        # Einzelne Sound-Karte
├── waveform_widget.py   # Animierte Wellenform-Anzeige
├── data_manager.py      # Daten laden und speichern (JSON)
├── audio_player.py      # Sound-Wiedergabe mit pygame
├── osc_client.py        # OSC-Kommunikation mit VRChat
├── dialogs.py           # Dialoge (Sound hinzufuegen, Einstellungen)
└── requirements.txt     # Python-Pakete
```

## VRChat OSC einrichten

1. In VRChat: Settings -> OSC -> Enable
2. Standard-Port: 9000 (Host: 127.0.0.1)
3. Im Soundboard: Settings -> OSC-Einstellungen pruefen

## Sound hinzufuegen

1. Eine Collection links auswaehlen
2. Auf das "+" / "Add Sound" Feld klicken
3. Name, Icon, Hotkey und Datei auswaehlen
4. Optional: OSC Chatbox-Nachricht eingeben

## Daten

Alle Daten werden in `soundboard_data.json` im Programmordner gespeichert.
