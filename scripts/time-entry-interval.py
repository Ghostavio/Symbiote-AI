"""Validate timezone-aware ISO 8601 timestamps and print normalized interval JSON."""

from datetime import datetime, timezone
import json
import re
import sys


TIMESTAMP_PATTERN = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}"
    r"(?:Z|[+-](?:0[0-9]|1[0-4]):[0-5][0-9])$"
)


def parse_timestamp(value: str) -> datetime:
    if not TIMESTAMP_PATTERN.fullmatch(value):
        raise ValueError("use YYYY-MM-DDTHH:MM:SSZ or an explicit valid ±HH:MM offset")
    if value[-6:-3] in {"+14", "-14"} and value[-2:] != "00":
        raise ValueError("UTC offsets must be between -14:00 and +14:00")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> int:
    if len(sys.argv) != 3:
        print("Usage: time-entry-interval.py START END", file=sys.stderr)
        return 2

    try:
        start = parse_timestamp(sys.argv[1]).astimezone(timezone.utc)
        end = parse_timestamp(sys.argv[2]).astimezone(timezone.utc)
    except (ValueError, OverflowError) as error:
        print(f"ERRO: timestamp inválido: {error}.", file=sys.stderr)
        return 2

    duration = int((end - start).total_seconds())
    if duration <= 0:
        print("ERRO: --end deve representar um instante posterior a --start.", file=sys.stderr)
        return 1

    print(json.dumps({
        "duration_seconds": duration,
        "start_utc": start.isoformat(timespec="seconds").replace("+00:00", "Z"),
        "end_utc": end.isoformat(timespec="seconds").replace("+00:00", "Z"),
    }))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
