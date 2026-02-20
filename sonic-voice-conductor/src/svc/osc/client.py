"""OSC Sender zu Sonic Pi."""
from pythonosc import udp_client


class OSCClient:
    """Sendet OSC-Nachrichten an Sonic Pi (/ai [key, value])."""

    def __init__(self, host: str = "127.0.0.1", port: int = 4560):
        self.client = udp_client.SimpleUDPClient(host, port)
        self.address = "/ai"

    def send(self, key: str, value: float | int | str) -> None:
        """Sendet eine einzelne [key, value] Nachricht."""
        self.client.send_message(self.address, [key, value])

    def send_batch(self, items: list[tuple[str, float | int | str]]) -> None:
        """Sendet mehrere (key, value) Paare."""
        for k, v in items:
            self.send(k, v)
