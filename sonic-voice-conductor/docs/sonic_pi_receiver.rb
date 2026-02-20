# Sonic Pi OSC Receiver für Sonic Voice Conductor (Technoprompter)
# Füge diesen Code in Sonic Pi ein, um die OSC-Nachrichten zu empfangen.
#
# Setup:
# - Sonic Pi 4.x empfängt OSC auf Port 4560 (Standard)
# - Die App sendet an /ai mit [key, value]
# - Sonic Pi's OSC-Server muss aktiv sein (läuft standardmäßig)
#
# Hinweis: Sonic Pi empfängt OSC automatisch. Nutze die
# live_loop :osc_receive (siehe Sonic Pi Docs) oder diesen Workaround:
#
# In Sonic Pi: Run -> Enable Incoming OSC (falls vorhanden)
# Dann werden Nachrichten an /ai mit /ai/key/value gesendet.
#
# Alternativ: Nutze einen externen OSC-zu-Sonic-Pi Bridge oder
# Sonic Pi's live_loop mit cue/get für interne Steuerung.

# Globale Variablen für Voice-Steuerung
set :energy, 0.5
set :darkness, 0.5
set :hats, 0.5
set :bpm, 128
set :kick_on, 1
set :profile, "peak"
set :saved_state, nil

# Beispiel-Live-Loop der die gesetzten Werte nutzt
live_loop :voice_params do
  use_real_time
  e = get(:energy)
  d = get(:darkness)
  h = get(:hats)
  # Hier deine Synths an e, d, h anbinden
  # z.B. with_fx :lpf, cutoff: (60 + d * 100) do ...
  sleep 0.1
end

# OSC-Empfang: Sonic Pi 4 nutzt Port 4560
# Die App sendet: /ai ["energy", 0.8]
# Du musst ggf. den OSC-Input in Sonic Pi konfigurieren.
# Siehe: https://in-thread.sonic-pi.net/t/osc-input
