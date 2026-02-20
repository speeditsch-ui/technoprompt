"""Mikrofon-Device-Auflösung und Auflistung."""
import sounddevice as sd


def list_devices() -> list[dict]:
    """Gibt alle verfügbaren Audiogeräte zurück (sounddevice query_devices)."""
    try:
        devices = sd.query_devices()
        result = []
        for i, d in enumerate(devices):
            result.append({
                "index": i,
                "name": d.get("name", ""),
                "channels_in": d.get("max_input_channels", 0),
                "sample_rate": d.get("default_samplerate", 0),
            })
        return result
    except Exception as e:
        return [{"error": str(e)}]


def resolve_device(mic_device: str | int | None) -> int | None:
    """
    Löst mic_device (Index oder Substring) zu einem Geräte-Index auf.
    Returns None wenn Default-Gerät verwendet werden soll.
    """
    if mic_device is None:
        return None
    if isinstance(mic_device, int):
        return mic_device
    devices = sd.query_devices()
    s = str(mic_device).lower()
    for i, d in enumerate(devices):
        if str(i) == s:
            return i
        if s in (d.get("name") or "").lower():
            return i
    return None
