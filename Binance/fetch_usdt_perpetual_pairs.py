"""Fetch and display USDT-margined perpetual futures trading pairs from Binance.

This script calls the public Binance Futures API, filters the symbols so that
only USDT-quoted perpetual contracts remain, and prints them sorted in
alphabetical order with the contracts that start with digits placed at the end.
"""

from __future__ import annotations

import json
import sys
import urllib.error
import urllib.request
from typing import Iterable, List

API_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"


def fetch_exchange_info() -> dict:
    """Return the JSON payload from the Binance exchangeInfo endpoint."""

    request = urllib.request.Request(API_URL, headers={"User-Agent": "spreadFut-script"})
    with urllib.request.urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise RuntimeError(f"Unexpected status code: {response.status}")
        return json.load(response)


def extract_usdt_perpetual_symbols(payload: dict) -> List[str]:
    """Extract all USDT-quoted perpetual futures symbols from the payload."""

    symbols = []
    for symbol_info in payload.get("symbols", []):
        if symbol_info.get("contractType") != "PERPETUAL":
            continue
        if symbol_info.get("quoteAsset") != "USDT":
            continue
        symbol = symbol_info.get("symbol")
        if symbol:
            symbols.append(symbol)
    return symbols


def sort_symbols(symbols: Iterable[str]) -> List[str]:
    """Sort symbols alphabetically with those starting with digits at the end."""

    return sorted(symbols, key=lambda s: (s[0].isdigit(), s))


def main() -> None:
    try:
        payload = fetch_exchange_info()
        symbols = extract_usdt_perpetual_symbols(payload)
    except (urllib.error.URLError, RuntimeError, json.JSONDecodeError) as exc:
        print(f"Failed to retrieve symbols: {exc}", file=sys.stderr)
        sys.exit(1)

    for symbol in sort_symbols(symbols):
        print(symbol)


if __name__ == "__main__":
    main()
