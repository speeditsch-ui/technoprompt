"""Konfiguration via YAML/TOML und CLI-Flags."""
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """Konfiguration der App."""

    model_config = SettingsConfigDict(
        env_prefix="SVC_",
        env_file=None,
        extra="ignore",
    )

    # OSC
    osc_host: str = Field(default="127.0.0.1", description="Sonic Pi OSC Host")
    osc_port: int = Field(default=4560, description="Sonic Pi OSC Port")

    # Ollama
    ollama_base_url: str = Field(default="http://127.0.0.1:11434", description="Ollama API URL")
    llm_model: str = Field(default="llama3.2", description="LLM Modell für Intent-Parsing")
    embed_model: str = Field(default="nomic-embed-text", description="Embedding Modell")

    # Whisper
    whisper_model_size: str = Field(default="base", description="faster-whisper Modellgröße")
    language: str = Field(default="de", description="Sprache für STT")

    # Audio
    record_seconds: float = Field(default=3.0, description="Aufnahmedauer für Voice-Input")
    sample_rate: int = Field(default=16000, description="Sample-Rate für Aufnahme")
    mic_device: str | int | None = Field(default=None, description="Mikrofon-Index oder Substring")

    # Thresholds
    knn_auto: float = Field(default=0.85, ge=0.0, le=1.0, description="Confidence >= : sofort anwenden")
    knn_suggest: float = Field(default=0.65, ge=0.0, le=1.0, description="Confidence zwischen suggest und auto")
    llm_auto_conf: float = Field(default=0.8, ge=0.0, le=1.0, description="LLM Confidence für Auto-Apply")

    # Safety
    max_big_changes_per_8_bars: int = Field(default=1, ge=1, le=10)
    bpm_max_delta_per_minute: float = Field(default=10.0, ge=1.0, le=50.0)

    # Paths
    config_path: Path | None = Field(default=None, description="Pfad zur config.yaml")
    data_dir: Path | None = Field(default=None, description="Datenverzeichnis für DB")

    @classmethod
    def load(cls, config_path: Path | None = None) -> "Config":
        """Lädt Config aus Datei falls vorhanden, mergt mit Env/CLI."""
        paths = []
        if config_path:
            paths.append(config_path)
        default_config = Path.home() / ".config" / "sonic-voice-conductor" / "config.yaml"
        if default_config.exists():
            paths.append(default_config)

        # YAML-Ladung, flacht thresholds/safety falls verschachtelt
        overrides: dict = {}
        for p in paths:
            if p and p.exists():
                import yaml
                with open(p) as f:
                    data = yaml.safe_load(f) or {}
                    if "thresholds" in data:
                        overrides.update(data["thresholds"])
                    if "safety" in data:
                        overrides.update(data["safety"])
                    overrides = {**overrides, **{k: v for k, v in data.items() if k not in ("thresholds", "safety")}}

        return cls(**{k: v for k, v in overrides.items() if k in cls.model_fields})


def get_data_dir(config: Config) -> Path:
    """Bestimmt das Datenverzeichnis."""
    if config.data_dir:
        return Path(config.data_dir)
    return Path.home() / ".local" / "share" / "sonic-voice-conductor"
