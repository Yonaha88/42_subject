#!/usr/bin/env python3

from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.total = 0
        self._items: list[tuple[int, str]] = []

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    @abstractmethod
    def ingest(self, data: Any) -> None:
        pass

    def output(self) -> tuple[int, str]:
        if not self._items:
            raise IndexError(f"{self.name} has no data to output")
        return self._items.pop(0)

    def remaining(self) -> int:
        return len(self._items)

    def _store(self, value: str) -> None:
        self._items.append((self.total, value))
        self.total += 1


class NumericProcessor(DataProcessor):
    def __init__(self) -> None:
        super().__init__("Numeric Processor")

    def validate(self, data: Any) -> bool:
        if isinstance(data, (int, float)) and not isinstance(data, bool):
            return True
        if isinstance(data, list) and data:
            return all(
                isinstance(item, (int, float)) and not isinstance(item, bool)
                for item in data
            )
        return False

    def ingest(self, data: int | float | list[int | float]) -> None:
        if not self.validate(data):
            raise ValueError("Improper numeric data")
        if isinstance(data, list):
            for item in data:
                self._store(str(item))
        else:
            self._store(str(data))


class TextProcessor(DataProcessor):
    def __init__(self) -> None:
        super().__init__("Text Processor")

    def validate(self, data: Any) -> bool:
        if isinstance(data, str):
            return True
        if isinstance(data, list) and data:
            return all(isinstance(item, str) for item in data)
        return False

    def ingest(self, data: str | list[str]) -> None:
        if not self.validate(data):
            raise ValueError("Improper text data")
        if isinstance(data, list):
            for item in data:
                self._store(item)
        else:
            self._store(data)


class LogProcessor(DataProcessor):
    def __init__(self) -> None:
        super().__init__("Log Processor")

    def validate(self, data: Any) -> bool:
        if isinstance(data, dict):
            return self._is_log_entry(data)
        if isinstance(data, list) and data:
            return all(
                isinstance(item, dict) and self._is_log_entry(item)
                for item in data
            )
        return False

    def ingest(self, data: dict[str, str] | list[dict[str, str]]) -> None:
        if not self.validate(data):
            raise ValueError("Improper log data")
        if isinstance(data, list):
            for item in data:
                self._store(self._format(item))
        else:
            self._store(self._format(data))

    def _is_log_entry(self, entry: dict[Any, Any]) -> bool:
        if not entry:
            return False
        return all(
            isinstance(key, str) and isinstance(value, str)
            for key, value in entry.items()
        )

    def _format(self, entry: dict[str, str]) -> str:
        return ": ".join(entry.values())


def main() -> None:
    print("=== Code Nexus - Data Processor ===")
    print("Testing Numeric Processor...")
    numeric = NumericProcessor()
    print(f"Trying to validate input '42': {numeric.validate(42)}")
    print(f"Trying to validate input 'Hello': {numeric.validate('Hello')}")
    print("Test invalid ingestion of string 'foo' without prior validation:")
    bad_data = "foo"
    try:
        numeric.ingest(bad_data)
    except ValueError as exc:
        print(f"Got exception: {exc}")
    numbers: list[int | float] = [1, 2, 3, 4, 5]
    print(f"Processing data: {numbers}")
    numeric.ingest(numbers)
    print("Extracting 3 values...")
    for _ in range(3):
        rank, value = numeric.output()
        print(f"Numeric value {rank}: {value}")
    print()
    print("Testing Text Processor...")
    text = TextProcessor()
    print(f"Trying to validate input '42': {text.validate(42)}")
    words = ['Hello', 'Nexus', 'World']
    print(f"Processing data: {words}")
    text.ingest(words)
    print("Extracting 1 value...")
    rank, value = text.output()
    print(f"Text value {rank}: {value}")
    print()
    print("Testing Log Processor...")
    log = LogProcessor()
    print(f"Trying to validate input 'Hello': {log.validate('Hello')}")
    logs = [
        {'log_level': 'NOTICE', 'log_message': 'Connection to server'},
        {'log_level': 'ERROR', 'log_message': 'Unauthorized access!!'},
    ]
    print(f"Processing data: {logs}")
    log.ingest(logs)
    print("Extracting 2 values...")
    for _ in range(2):
        rank, value = log.output()
        print(f"Log entry {rank}: {value}")


if __name__ == "__main__":
    main()
