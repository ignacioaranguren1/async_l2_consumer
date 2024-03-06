import logging

from typing import List, Dict

from data_manager.config import CraConfig
from data_manager.client import DataMngrClient
from data_manager.l2_processor import L2Processor


class DataMngr:
    """
    DataMngr class launching the websocket clients an
    d L2Processor
    """
    def __init__(self, tickers: List[str]):
        # Init instance variables
        self.__logger = logging.getLogger('data_manager')
        self.__processor = L2Processor()

        # Initialize websocket clients for all exchanges
        self.__clients: Dict[str, DataMngrClient] = {}
        exchange_l2_processors = {}
        for exchange, config in CraConfig.EXCHANGE_PARAMS.items():
            self.__clients[exchange] = DataMngrClient(
                tickers, exchange, config, self.__processor
            )
            exchange_l2_processors[exchange] = config['L2_PROCESSOR']

        # Init processors property in processor object
        self.__processor.processors = exchange_l2_processors

    def run(self):
        """
        return awaitables to be run by the event loop
        :return:
        """
        return list(map(lambda x: x.receive(), self.__clients.values()))

    def get_orderbooks(self):
        return self.__processor.orderbooks

    def connect(self):
        """
        Method connecting the websocket client to the endpoint
        :return:
        """
        for client in self.__clients.values():
            client.connect()

    def disconnect(self):
        """
        Disconnect client from websocket connection
        :return:
        """
        for client in self.__clients.values():
            client.disconnect()

    def subscribe_market_data(self):
        """
        Make client start a websocket connection for l2 data for the specified symbols
        :return:
        """
        for client in self.__clients.values():
            client.subscribe_market_data()

    def __enter__(self):
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()
