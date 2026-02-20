# Sonic Voice Conductor (Technoprompter)

Lernfähige lokale Sprachsteuerung für Sonic Pi (Techno Live-Coding) über OSC.

## Features
- **Push-to-talk**: Enter drücken → Sprechen → Befehl ausführen
- **Lernfähig**: Korrekturen werden gespeichert und verbessern die Erkennung
- **Lokal**: Keine Cloud – Ollama, faster-whisper, alles auf deinem Rechner
- **OSC**: Steuerung von Sonic Pi über [key, value] auf `/ai`

## Installation

```bash
cd sonic-voice-conductor
python -m venv .venv
source .venv/bin/activate   # Linux/macOS
pip install -e .
```

**System-Abhängigkeiten (Linux):**
- PortAudio: `apt install portaudio19-dev python3-pyaudio` oder `pacman -S portaudio`
- Für Mikrofon: PipeWire oder PulseAudio

## Ollama Setup

```bash
# Ollama installieren (https://ollama.ai)
ollama pull llama3.2
ollama pull nomic-embed-text
```

## Sonic Pi Receiver

Kopiere `docs/sonic_pi_receiver.rb` in Sonic Pi oder passe dein Set an. Die App sendet OSC an `127.0.0.1:4560` auf Adresse `/ai` mit `[key, value]`.

Keys: `energy`, `darkness`, `hats`, `bpm`, `kick_on`, `save`, `undo`, `break`, `drop`, `reset`, `profile`, `macro`, `schedule`, `hold`.

## Konfiguration

```bash
mkdir -p ~/.config/sonic-voice-conductor
cp config.example.yaml ~/.config/sonic-voice-conductor/config.yaml
# Bearbeite config.yaml nach Bedarf
```

## Start

```bash
svc
# oder
sonic-voice-conductor
```

**Tasten**: Enter = Aufnahme | d = Geräte | m = Makros | p = Profile | q = Beenden

## Beispiel-Sprachbefehle

- "energie hoch", "bpm 128"
- "profil warmup", "macro hypnotischer zug"
- "break 8", "drop"

Siehe `docs/voice_commands.md` für die vollständige Liste.

## Troubleshooting

### PipeWire / Mikrofon
- Prüfe mit `d` die Geräteliste
- Setze `mic_device` in der Config (Index oder Namen-Substring)
- Bei Flatpak: Berechtigungen für Mikrofon prüfen

### OSC Port
- Sonic Pi nutzt standardmäßig Port 4560
- Stelle sicher, dass Sonic Pi läuft und OSC-Eingang akzeptiert

### Ollama
- `ollama serve` muss laufen (Startet meist automatisch)
- Test: `curl http://127.0.0.1:11434/api/tags`

### Whisper
- Erstes Laden des Modells kann dauern
- `base` ist am schnellsten, `small`/`medium` genauer

### PortAudio / sounddevice
- Fehler "PortAudio library not found": `apt install portaudio19-dev` (oder distro-spezifisch)
