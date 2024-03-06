import argparse
import logging
import logging.config
import yaml

from data_manager.data_mngr import DataMngr
from l2_manager import deplete_liquidity
from utils import run


def setup_logging(config_file):
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f.read())
    logging.config.dictConfig(config)


def init(to_deplete: float, side: str):
    """
    Main method that launches the current project
    :param to_deplete:
    :param side:
    :return:
    """
    with DataMngr(["BTC-USD"]) as mngr:
        mngr.subscribe_market_data()
        run(
            deplete_liquidity(to_deplete, side, mngr, logging.getLogger('l2_manager')),
            *mngr.run()
        )


if __name__ == '__main__':
    # Initialize curses and create a window

    def positive_float(value):
        try:
            fvalue = float(value)
            if fvalue <= 0:
                raise argparse.ArgumentTypeError("Liquidity must be a positive float")
            return fvalue
        except ValueError:
            raise argparse.ArgumentTypeError("Invalid float value")


    parser = argparse.ArgumentParser(description="Process orderbook data")
    parser.add_argument("action", choices=["buy", "sell"], help="Action: 'buy' or 'sell'")
    parser.add_argument("liquidity", type=positive_float, help="Liquidity amount (positive float)")
    args = parser.parse_args()

    setup_logging("logs/config.yml")

    init(args.liquidity, args.action)

