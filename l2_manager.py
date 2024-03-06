import asyncio
import logging

from typing import Dict
from data_manager.data_mngr import DataMngr
from utils import print_results


def merge_and_deplete(one_side: Dict[str, list], depletion: float, side: str):
    """
    Merge one side of the trade from different exchanges and deplete liquidity
    :param one_side: one side of the OB from different exchanges
    :param depletion: liquidity to withdraw
    :param side: bid or ask
    :return:
    """
    orders = []
    adjusted_orders = []
    for exchange, book in one_side.items():
        orders += book

    orders = sorted(orders, reverse=(side == "bid"))
    for price, volume in orders:
        if depletion <= 0:
            break
        adjusted_volume = min(volume, depletion)
        adjusted_orders.append((price, volume))
        depletion -= adjusted_volume
    return adjusted_orders


async def deplete_liquidity(depletion: float, action: str, data_manager: DataMngr, logger: logging.Logger):
    """
    Deplete liquidity in each exchange
    :param depletion: liquidity to withdraw from any side of the queue
    :param action: sell or buy. Sell depletes bid side and buy bid's
    :param data_manager: datamanager object. Only used to access the updates of the OB from websockets clients
    :param logger: logger object
    :return:
    """
    logger.info(f"Liquidity to deplete {depletion}, action: {action}")
    side = 'ask' if action == 'buy' else 'bid'
    while True:
        await asyncio.sleep(2)
        order_book_state = data_manager.get_orderbooks()
        tasks = [process_exchange(exchange, l2_data, side, depletion) for exchange, l2_data in order_book_state.items()]
        adjusted_order_books = {exchange: adjusted_orders for exchange, adjusted_orders in await asyncio.gather(*tasks)}
        print_results(
            depletion,
            action,
            side,
            merge_and_deplete(adjusted_order_books, depletion, side),
            adjusted_order_books
        )


async def process_exchange(exchange: str, l2_data: Dict[str, Dict], side: str, depletion: float):
    sorted_book = sorted(l2_data[side].items(), key=lambda x: x[0], reverse=(side == "bid"))
    adjusted_orders = []
    acum = 0
    for price, amount in sorted_book:
        if acum + float(amount) >= depletion:
            adjusted_orders.append((price, depletion - acum))
            break
        acum += float(amount)
        adjusted_orders.append((price, amount))
    return exchange, adjusted_orders
