import jwt
import secrets
import time

from cryptography.hazmat.primitives import serialization


def build_jwt(service, key_secret, key_name):
    """Build JWT token to authenticate on lvl2 websocket api"""
    private_key_bytes = key_secret.encode('utf-8')
    private_key = serialization.load_pem_private_key(private_key_bytes, password=None)

    jwt_payload = {
        'sub': key_name,
        'iss': "coinbase-cloud",
        'nbf': int(time.time()),
        'exp': int(time.time()) + 120,
        'aud': [service],
    }

    jwt_token = jwt.encode(
        jwt_payload,
        private_key,
        algorithm='ES256',
        headers={'kid': key_name, 'nonce': secrets.token_hex()},
    )
    return jwt_token


async def process_l2_gemini(raw_l2_data, logger):
    """Process gemini orderbook data to unified format to be understood by processor"""
    l2_data = raw_l2_data.get("changes", [])
    bid = {}
    ask = {}
    bid_depletion = []
    ask_depletion = []
    for order_type, price, volume in l2_data:
        price, volume = float(price), float(volume)
        if order_type == "buy":
            if volume == 0:
                bid_depletion.append(price)
            else:
                bid[price] = volume
        elif order_type == "sell":
            if volume == 0:
                ask_depletion.append(price)
            else:
                ask[price] = volume
        else:
            logger.error(f"Unknown order received on gemini order book: {order_type}")
    return bid, ask, bid_depletion, ask_depletion


async def process_l2_coinbase(raw_l2_data, logger):
    """Process coinbase orderbook data to unified format to be understood by processor"""
    l2_data = raw_l2_data.get("events")[0].get('updates', [])
    bid = {}
    ask = {}
    bid_depletion = []
    ask_depletion = []
    for order in l2_data:
        order_type, _, price, volume = order.values()
        price, volume = float(price), float(volume)
        if order_type in ["bid", "buy"]:
            if volume == 0:
                bid_depletion.append(price)
            else:
                bid[price] = volume
        elif order_type in ["ask", "sell", "offer"]:
            if volume == 0:
                ask_depletion.append(price)
            else:
                ask[price] = volume
        else:
            logger.error(f"Unknown order received on coinbase order book: {order_type}")
    return bid, ask, bid_depletion, ask_depletion


async def process_l2_kraken(raw_l2_data, logger):
    """Process kraken orderbook data to unified format to be understood by processor"""
    if not isinstance(raw_l2_data, list):
        return

    bid_raw = raw_l2_data[1].get('bs', raw_l2_data[1].get('b', []))
    ask_raw = raw_l2_data[1].get('as', raw_l2_data[1].get('a', []))

    bid = {}
    ask = {}
    bid_depletion = []
    ask_depletion = []

    for order in bid_raw:
        price, volume = float(order[0]), float(order[1])
        if volume == 0:
            bid_depletion.append(price)
        else:
            bid[price] = volume

    for order in ask_raw:
        price, volume = float(order[0]), float(order[1])
        if volume == 0:
            ask_depletion.append(price)
        else:
            ask[price] = volume

    return bid, ask, bid_depletion, ask_depletion


