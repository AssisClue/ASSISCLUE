from __future__ import annotations

from abc import ABC, abstractmethod


class BaseSTTProvider(ABC):
    @abstractmethod
    def run_forever(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def stop(self) -> None:
        raise NotImplementedError