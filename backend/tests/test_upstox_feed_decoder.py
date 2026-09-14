from decimal import Decimal

from advance_system.adapters.upstox.feed_decoder import decode_quotes


def test_decode_ltpc_quote() -> None:
    message = {
        "currentTs": "1760000000000",
        "feeds": {
            "NSE_EQ|INE123456789": {
                "ltpc": {"ltp": 123.45, "ltt": "1760000000123", "ltq": "10", "cp": 120}
            }
        },
    }

    quotes = decode_quotes(message)

    assert len(quotes) == 1
    assert quotes[0].instrument_key == "NSE_EQ|INE123456789"
    assert quotes[0].ltp == Decimal("123.45")
    assert quotes[0].ltq == 10
    assert quotes[0].source == "upstox_v3"


def test_decode_full_feed_depth_and_oi() -> None:
    message = {
        "currentTs": "1760000000000",
        "feeds": {
            "NSE_FO|12345": {
                "fullFeed": {
                    "ltpc": {"ltp": 101.25, "ltt": "1760000000123", "ltq": 25},
                    "vtt": "90000",
                    "oi": "120000",
                    "marketLevel": {
                        "bidAskQuote": [
                            {"bidP": 101.20, "bidQ": "400", "askP": 101.30, "askQ": "600"}
                        ]
                    },
                }
            }
        },
    }

    quotes = decode_quotes(message)

    assert len(quotes) == 1
    quote = quotes[0]
    assert quote.volume == 90000
    assert quote.oi == 120000
    assert quote.bid_price == Decimal("101.2")
    assert quote.bid_qty == 400
    assert quote.ask_price == Decimal("101.3")
    assert quote.ask_qty == 600


def test_unknown_or_status_message_does_not_create_quotes() -> None:
    assert decode_quotes({"type": "market_info", "feeds": {}}) == []
    assert decode_quotes({"feeds": {"NSE_EQ|X": {"unexpected": {}}}}) == []
