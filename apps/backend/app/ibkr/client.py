"""
IBKR connection manager.

A lazily-connected singleton wrapper around `ib_async.IB`. Holds one TCP
connection to IB Gateway; routes pull it via `get_client()` which connects
on first call and reuses the connection on subsequent calls.

The retry logic mirrors what `poc/connect_ibkr.py` does at the script level:
IB Gateway may take 30-60s to be ready after the container starts, so we
retry up to 12 times with a 5-second backoff before giving up.
"""
from __future__ import annotations

import asyncio
import logging

from ib_async import IB

logger = logging.getLogger(__name__)

_DEFAULT_MAX_RETRIES = 12
_DEFAULT_RETRY_BACKOFF = 5.0
_DEFAULT_CONNECT_TIMEOUT = 10


class IBKRClient:
    def __init__(
        self,
        host: str,
        port: int,
        client_id: int,
        *,
        max_retries: int = _DEFAULT_MAX_RETRIES,
        retry_backoff: float = _DEFAULT_RETRY_BACKOFF,
        connect_timeout: int = _DEFAULT_CONNECT_TIMEOUT,
    ) -> None:
        self.host = host
        self.port = port
        self.client_id = client_id
        self.max_retries = max_retries
        self.retry_backoff = retry_backoff
        self.connect_timeout = connect_timeout

        self._ib: IB | None = None
        self._lock = asyncio.Lock()

    async def get_client(self) -> IB:
        """Return a connected `ib_async.IB`. Connects lazily on first call."""
        async with self._lock:
            if self._ib is not None and self._ib.isConnected():
                return self._ib

            ib = IB()
            for attempt in range(1, self.max_retries + 1):
                try:
                    await ib.connectAsync(
                        host=self.host,
                        port=self.port,
                        clientId=self.client_id,
                        timeout=self.connect_timeout,
                    )
                    self._ib = ib
                    logger.info(
                        "IBKR connected on attempt %d (host=%s port=%d clientId=%d)",
                        attempt,
                        self.host,
                        self.port,
                        self.client_id,
                    )
                    return ib
                except Exception as exc:  # noqa: BLE001
                    if attempt >= self.max_retries:
                        logger.error(
                            "IBKR connect failed after %d attempts: %s",
                            attempt,
                            exc,
                        )
                        raise
                    logger.warning(
                        "IBKR connect attempt %d/%d failed: %s. Retrying in %ds...",
                        attempt,
                        self.max_retries,
                        exc,
                        self.retry_backoff,
                    )
                    await asyncio.sleep(self.retry_backoff)

            # Unreachable — either we returned above or we re-raised.
            raise RuntimeError("IBKR connect retry loop terminated without resolution")

    @property
    def is_connected(self) -> bool:
        return self._ib is not None and self._ib.isConnected()

    async def disconnect(self) -> None:
        async with self._lock:
            if self._ib is not None and self._ib.isConnected():
                self._ib.disconnect()
                logger.info("IBKR disconnected.")
            self._ib = None
