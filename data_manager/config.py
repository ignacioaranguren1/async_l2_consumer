import time

from data_manager.utils import (build_jwt, process_l2_gemini,
                                process_l2_kraken, process_l2_coinbase)


class CraConfig:
    FEEDS = ("coinbase", 'gemini', 'kraken')

    coinbase_key_name = ""
    coinbase_key_secret = ""
    coinbase_service_name = "public_websocket_api"

    EXCHANGE_PARAMS = {
        "gemini": {
            "URL": 'wss://api.gemini.com/v2/marketdata',
            "SUBS_FORMAT": lambda tickers: {
                "type": "subscribe",
                "subscriptions": [{"name": "l2", "symbols": list(map(lambda x: x.replace("-", ""), tickers))}]
            },
            "L2_PROCESSOR": process_l2_gemini
        },
        "coinbase": {
            "URL": "wss://advanced-trade-ws.coinbase.com",
            "SUBS_FORMAT": lambda tickers: {
                "type": "subscribe",
                "product_ids": tickers,
                "channel": "level2",
                "jwt": f"{build_jwt(CraConfig.coinbase_service_name, CraConfig.coinbase_key_secret, CraConfig.coinbase_key_name)}",
                "timestamp": f"{int(time.time())}"
            },
            "L2_PROCESSOR": process_l2_coinbase
        },
        "kraken": {
            "URL": 'wss://beta-ws.kraken.com/',
            "SUBS_FORMAT": lambda tickers: {"event": "subscribe", "pair": list(map(lambda x: x.replace("-", "/"), tickers)), "subscription": {"name": "book"}},
            "L2_PROCESSOR": process_l2_kraken
        }

    }
