import asyncio
import os

from typing import Awaitable, Optional, List, Dict


class Color:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    RESET = '\033[0m'


def print_colored(text, color):
    print(f"{color}{text}{Color.RESET}")


def print_results(liquidity: float, action: str, side: str, merged_order_book: List, adjusted_order_book: Dict):
    """Print results of the l2_manager to stdout"""
    if len(adjusted_order_book) == 0:
        return
    os.system('cls' if os.name == 'nt' else 'clear')  # Clear the terminal screen
    print_colored("\n\n*************** ORDERBOOKS *********************", Color.CYAN)
    print_colored(f"ORDER SIZE: {liquidity}, ACTION: {action}, SIDE: {side}", Color.MAGENTA)

    for exchange, orders in adjusted_order_book.items():
        if len(orders) == 0:
            continue
        print_colored(f"├──{exchange.upper()}", Color.BLUE)
        print(f"├── Num Orders: {len(orders)}")
        print(f"├── Total volume: {sum([volume for price, volume in orders])}")
        print(f"└── Price: {weighted_price_by_volume(orders)}")

    print_colored('\nMERGED ORDERBOOK', Color.BLUE)
    print(f"Num Orders: {len(merged_order_book)}")
    print(f"Total volume: {sum([volume for price, volume in merged_order_book])}")
    print(f"Price: {weighted_price_by_volume(merged_order_book)}")

    print_colored("\n\n*************** ORDERS *********************", Color.CYAN)
    print(f"Merged: {merged_order_book}\n")
    for exchange, orders in adjusted_order_book.items():
        print(f"{exchange.upper()}: {orders}\n")


def weighted_price_by_volume(orders: List):
    """Calculate the average of prices weighted on volume"""
    total_vol = sum([volume for price, volume in orders])

    numerator = 0
    for price, volume in orders:
        numerator += (price * volume)

    return numerator/total_vol


def get_loop():
    """Get the asyncio event loop for the current thread."""
    return asyncio.get_event_loop_policy().get_event_loop()


def run(*awaitables: Awaitable, timeout: Optional[float] = None):
    """
    When awaitables (like Tasks, Futures or coroutines) are given then
    run the event loop until each has completed and return their results.

    An optional timeout (in seconds) can be given that will raise
    asyncio.TimeoutError if the awaitables are not ready within the
    timeout period.
    """
    loop = get_loop()

    if len(awaitables) == 1:
        future = awaitables[0]
    else:
        future = asyncio.gather(*awaitables)
    if timeout:
        future = asyncio.wait_for(future, timeout)
    task = asyncio.ensure_future(future)

    try:
        result = loop.run_until_complete(task)
    except asyncio.CancelledError as e:
        raise e
    return result