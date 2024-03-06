import logging


class L2Processor:
    """
    L2Processor is responsible for processing L2 data from a websocket client
    """
    def __init__(self):
        # Init instance variables
        self.__processors = None
        self.__logger = logging.getLogger('data_manager_processor')
        self.__orderbooks = {}

    @property
    def processors(self):
        return self.__processors

    @processors.setter
    def processors(self, processors):
        self.__processors = processors

    @property
    def orderbooks(self):
        """This method is called by a consumer"""
        return self.__orderbooks

    async def process_market_data(self, exchange: str, raw_data):
        """
        Process data using the processors defined in datamanager/utils.py for each exchange
        Its processor is unique in the sense that the data coming through wire probably
        won't be the same. After processing the raw data coming form the websocket connection
        it updates the order_books and deletes filled offers.
        """
        data = await self.__processors[exchange](raw_data, self.__logger)

        if not data:
            return

        bid, ask, bid_depletion, ask_depletion = data
        self.__logger.info(
            f"Market data update for {exchange}, updates: bid = {len(bid.values())}, ask = {len(ask.values())}"
            f"bid_depletions = {len(bid_depletion)}, ask_depletions = {len(ask_depletion)}"
        )

        # If orderbook for a given exchange is not present, create it
        if exchange not in self.__orderbooks:
            self.__orderbooks[exchange] = {"bid": bid, "ask": ask}
            # And return right away as initial state should not contain depletions
            return

        # Merge previous state with incoming updates
        self.__orderbooks[exchange] = {
            "bid": {**bid, **self.__orderbooks[exchange]["bid"]},
            "ask": {**bid, **self.__orderbooks[exchange]["ask"]}
        }

        # Manage depletions for ask and bid
        for depletion in ask_depletion:
            self.__orderbooks[exchange]["ask"].pop(depletion, None)

        for depletion in bid_depletion:
            self.__orderbooks[exchange]["bid"].pop(depletion, None)

        self.__logger.info(
            f"Orderbook depth for {exchange}: bid = {len(self.__orderbooks[exchange]['bid'])}"
            f" ask = {len(self.__orderbooks[exchange]['ask'])}"
        )





