"""In-memory event store for MCP sessions."""

from __future__ import annotations

import asyncio
import time
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from mcp.types import JSONRPCMessage


class InMemoryEventStore:
    """Simple in-memory event store for MCP sessions.

    This store maintains event history for each session, allowing clients
    to resume connections and retrieve missed events.
    """

    def __init__(self) -> None:
        """Initialize the event store."""
        self._events: dict[str, list[tuple[int, JSONRPCMessage]]] = {}
        self._next_seq: dict[str, int] = {}
        self._lock = asyncio.Lock()

    async def store_event(self, session_id: str, event: JSONRPCMessage) -> int:
        """Store an event for a session.

        Args:
            session_id: The session identifier
            event: The JSON-RPC message to store

        Returns:
            The sequence number assigned to this event
        """
        async with self._lock:
            if session_id not in self._events:
                self._events[session_id] = []
                self._next_seq[session_id] = 0

            seq = self._next_seq[session_id]
            self._next_seq[session_id] += 1
            self._events[session_id].append((seq, event))
            return seq

    async def get_events(
        self, session_id: str, from_seq: int = 0
    ) -> AsyncIterator[tuple[int, JSONRPCMessage]]:
        """Get events for a session starting from a sequence number.

        Args:
            session_id: The session identifier
            from_seq: Starting sequence number (inclusive)

        Yields:
            Tuples of (sequence_number, event)
        """
        async with self._lock:
            if session_id not in self._events:
                return

            for seq, event in self._events[session_id]:
                if seq >= from_seq:
                    yield seq, event

    async def clear_session(self, session_id: str) -> None:
        """Clear all events for a session.

        Args:
            session_id: The session identifier
        """
        async with self._lock:
            self._events.pop(session_id, None)
            self._next_seq.pop(session_id, None)

    async def cleanup_old_sessions(self, max_age_seconds: int = 3600) -> None:
        """Remove sessions that haven't been accessed recently.

        Args:
            max_age_seconds: Maximum age in seconds before cleanup
        """
        # This is a simple implementation that doesn't track access times
        # In a production system, you'd want to track last access time per session
        pass
