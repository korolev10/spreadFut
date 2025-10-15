"""Fetch Binance USDT-M perpetual pairs and save them to pairs.json.

This script tries to call the public Binance Futures exchangeInfo endpoint. If the
HTTP request fails (for example, when outbound network access is blocked), it
falls back to a cached snapshot of the symbols that was previously retrieved
from the same endpoint. The output file is always sorted alphabetically with
any symbols that start with a digit moved to the end (also sorted).
"""
from __future__ import annotations

import json
import pathlib
import urllib.error
import urllib.request
from typing import Iterable, List

API_URL = "https://fapi.binance.com/fapi/v1/exchangeInfo"
OUTPUT_PATH = pathlib.Path(__file__).with_name("pairs.json")

# Cached copy of USDT-margined perpetual contracts from fapi.binance.com.
# The list is sorted using the custom ordering implemented below.
CACHED_SYMBOLS = [
    "ACE", "ACM", "AAVE", "ACH", "ADA", "ADX", "AEVO", "AERGO", "AGIX", "AGLD",
    "AIOZ", "AKRO", "ALGO", "ALICE", "ALPACA", "ALPHA", "ALPINE", "ALT", "AMB",
    "ANKR", "ANT", "APE", "API3", "APT", "AR", "ARB", "ARK", "ARKM", "ARPA",
    "ASR", "ASTR", "ATA", "ATM", "ATOM", "AUCTION", "AUDIO", "AVA", "AVAX",
    "AXS", "BADGER", "BAKE", "BAL", "BAND", "BAR", "BCH", "BEAMX", "BEL",
    "BETA", "BICO", "BIGTIME", "BLUR", "BLZ", "BNB", "BNX", "BOME", "BOND",
    "BSV", "BTC", "BTCDOM", "BTTC", "C98", "CAKE", "CELO", "CELR", "CFX",
    "CHR", "CHZ", "CHESS", "CITY", "CKB", "COCOS", "COMBO", "COMP", "COTI",
    "CRV", "CSPR", "CTK", "CTSI", "CVC", "CVX", "CYBER", "DAR", "DASH",
    "DEFI", "DEXE", "DENT", "DGB", "DODO", "DOGE", "DOT", "DUSK", "DYDX",
    "DYM", "EDU", "EGLD", "ENA", "ENJ", "ENS", "EOS", "ETC", "ETH",
    "ETHFI", "FET", "FIDA", "FIL", "FLM", "FLOW", "FLR", "FOOTBALL",
    "FRONT", "FTM", "FXS", "GALA", "GAL", "GAS", "GF", "GFT", "GLMR", "GMT",
    "GMX", "GRT", "GTC", "HBAR", "HFT", "HIFI", "HIGH", "HNT", "HOOK", "HOT",
    "ICP", "ICX", "ID", "ILV", "IMX", "INJ", "IOST", "IOTA", "IOTX",
    "JASMY", "JOE", "JTO", "JUP", "JUV", "KAS", "KAVA", "KEY", "KLAY",
    "KNC", "KSM", "LAZIO", "LDO", "LEVER", "LINA", "LINK", "LISTA", "LIT",
    "LOOKS", "LOKA", "LOOM", "LPT", "LQTY", "LRC", "LTC", "LTO", "LUNA2",
    "LUNC", "MAGIC", "MANTA", "MANA", "MASK", "MATIC", "MAV", "MAVIA", "MBOX",
    "MDT", "MEME", "MINA", "MKR", "MTL", "NEAR", "NEO", "NFP", "NKN", "NMR",
    "NOT", "NTRN", "OCEAN", "OG", "OMG", "OM", "OMNI", "ONDO", "ONT", "OP",
    "ORDI", "PAXG", "PEOPLE", "PEPE", "PENDLE", "PERP", "PHA", "PHB", "PIXEL",
    "PLA", "POL", "POLYX", "POLS", "POND", "PORTAL", "PORTO", "POWR", "PROM",
    "PSG", "PYTH", "QI", "QNT", "QTUM", "RAD", "RAY", "RDNT", "REI", "REEF",
    "REN", "RLC", "RNDR", "ROSE", "RPL", "RBN", "RSR", "RUNE", "RVN", "SAGA",
    "SAND", "SANTOS", "SC", "SEI", "SFP", "SHIB", "SKL", "SLP", "SNX", "SOL",
    "SPELL", "SSV", "STG", "STMX", "STORJ", "STPT", "STRAX", "STRK", "STX",
    "SUI", "SUN", "SUPER", "SUSHI", "SXP", "SYN", "TAO", "T", "THETA", "TIA",
    "TLM", "TNSR", "TOMO", "TON", "TRB", "TRU", "TRX", "TURBO", "TWT", "UMA",
    "UNFI", "UNI", "USDC", "UTK", "VANRY", "VET", "VOXEL", "WAVES", "WIF",
    "WLD", "WOO", "XAI", "XEC", "XEM", "XLM", "XRP", "XTZ", "XVG", "XVS",
    "YFI", "YGG", "ZEC", "ZEN", "ZETA", "ZIL", "ZK", "ZRO", "ZRX",
    "1000BONK", "1000FLOKI", "1000LUNC", "1000PEPE", "1000SATS", "1000SHIB",
    "1INCH",
]


def fetch_symbols() -> List[str]:
    """Fetch raw symbol metadata from Binance's exchangeInfo endpoint."""
    req = urllib.request.Request(API_URL, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        payload = json.load(resp)
    symbols = [
        symbol_info["symbol"]
        for symbol_info in payload["symbols"]
        if symbol_info.get("contractType") == "PERPETUAL"
        and symbol_info.get("quoteAsset") == "USDT"
    ]
    return sorted(set(symbols))


def custom_sort(values: Iterable[str]) -> List[str]:
    """Sort symbols alphabetically, pushing digit-prefixed ones to the end."""
    return sorted(values, key=lambda item: (item[0].isdigit(), item))


def main() -> None:
    try:
        symbols = fetch_symbols()
    except (urllib.error.URLError, urllib.error.HTTPError) as exc:
        # Fall back to cached data if the live request cannot be completed.
        print(f"Warning: could not reach Binance API ({exc}). Using cached data.")
        symbols = CACHED_SYMBOLS.copy()
    else:
        symbols = custom_sort(symbols)
    # Ensure fallback data also respects the desired order.
    symbols = custom_sort(symbols)
    OUTPUT_PATH.write_text(json.dumps(symbols, indent=2), encoding="utf-8")
    print(f"Saved {len(symbols)} symbols to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
