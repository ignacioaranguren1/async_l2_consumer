import json
import logging

import websockets

from typing import Dict, List

from utils import run
from data_manager.l2_processor import L2Processor


class DataMngrClient:
    """
    DataMngrClient defines the basic interface of the client that initiates
    WebSocket stream
    """

    def __init__(self, tickers: List[str], exchange: str, config: Dict, processor: L2Processor, ):
        # Init instance variable from args
        self.__tickers = tickers
        self.__exchange = exchange
        self.__endpoint = config['URL']
        self.__subs_msg_format = config['SUBS_FORMAT']
        self.__processor = processor

        # Init additional instance variables
        self.__connection = None
        self.__logger = logging.getLogger("data_manager_client")

    def connect(self):
        """
        Establish connection with the websocket server
        :return:
        """
        self.__logger.info(f"Connecting client to {self.__endpoint}")
        run(self.__connect_async())

    async def __connect_async(self):
        self.__connection = await websockets.connect(self.__endpoint, max_size=2**22, ping_timeout=None, logger=self.__logger)
        self.__logger.info(f"Client connected -> {self.__endpoint}")

    def disconnect(self):
        """
        Terminate websocket connection with server
        :return:
        """
        self.__logger.info(f"Disconnecting client from {self.__endpoint}")
        run(self.__disconnect_async())

    async def __disconnect_async(self):
        if not self.__connection.open:
            self.__logger.info(f"Client {self.__exchange} not connected")
            return
        await self.__connection.close()

    async def receive(self):
        if not self.__connection.open:
            self.__logger.info(f"Client {self.__exchange}  not connected")
            return
        while True:
            msg = await self.__connection.recv()
            await self.__processor.process_market_data(self.__exchange, json.loads(msg))

    def subscribe_market_data(self):
        """
        Init market data subscription for a ticker
        :param tickers: List[str] list of tickers to init subscriptions
        :return:
        """
        run(self.__subscribe_market_data())

    async def __subscribe_market_data(self):
        if not self.__connection.open:
            self.__logger.info(f"Client {self.__exchange} not connected")
            return
        await self.__connection.send(str(json.dumps(self.__subs_msg_format(self.__tickers))))

