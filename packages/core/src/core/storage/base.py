from typing import Protocol


class ObjectStore(Protocol):
    def put_bytes(self, key: str, data: bytes, content_type: str | None = None) -> None:
        ...

    def get_bytes(self, key: str) -> bytes:
        ...

    def list(self, prefix: str) -> list[str]:
        ...

    def exists(self, key: str) -> bool:
        ...

    def signed_url(self, key: str, expires_in: int = 3600) -> str:
        ...

