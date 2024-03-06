

The project is implemented in two logical modules: the data manager and the l2_manager.


The data manager is responsible for establishing the websocket connections to the endpoints 
for the configurations defined in [config.py](data_manager%2Fconfig.py). The idea of the data 
manager is to be as generic as possible. Different sources can be included in [config.py](data_manager%2Fconfig.py)
as long as a websocket endpoint, subscription message and a data processor function object are included.

The [l2_manager](l2_manager.py) core entrypoint is deplete_liquidity which takes the parameters: depletion (liquidity to be depleted at one side of the book),
 action (sell or buy) and data_manager object (used to access the realtime orderbook updated by the websocket connection).

The core of the program is in line 27 of [main.py](main.py) which initiates the eventloop with the tasks:
deplete_liquidity and run method of [data_mngr.py](data_manager%2Fdata_mngr.py), which returns awaitables coroutines 
to the receive methods of the [clients](data_manager%2Fclient.py). Asyncio is the selected concurrency library. 
The implementation could be carried out by other concurrency libraries such as threading. However, due to the GIL
limitations, which makes that only a thread can be run at a moment by the interpreter, as new websocket connections are
included, the scheduling of threads runtime can become a bit chaotic. So the main reason for using asyncio library is 
scalability. By creating a task per receive method of a client and one additional for deplete_liquidity the synchronization
can be done effortlessly by the event loop. 

The selected library to connect to the exchanges is the websockets library, which follows a conventional send/recv architecture.
I first tried to use socketio, which I like more than websockets because the first is event driven. In any case, it seems
that the websocket server of Gemini, Kraken and Coinbase is not a socketio sever so the option was then discarded. 


## Logging interface

There is a logging interface writing to text output on /tmp directory (I assume your system is UNIX-like). There are 
separate handlers for the data_manager, data_manager_client, data_manager_processor and l2_manager. 
To find out more bout how the loggers are configured you can take a look to [config.yml](logs%2Fconfig.yml)



## Prerequistes 
1. Your system is UNIX-lie.
2. Create a venv for the project and dependencies:

```shell
cd cra
python3 -m venv .
source venv/bin/activate
pip3 install -r requirements.txt
```

## Run 
The program runs on CLI and uses the argsparse library. 
```shell
python3 main.py [action] [liquidity] 
```
-action arg is one of sell or buy
-liquidity arg is the liquidity be depleted

As an example: the command ```python3 main.py sell 15``` show the following output:

![cra_cli.png](images%2Fcra_cli.png)

The magenta colored line gives a summary of the input parameters. In this example, the liquidity to be depleted is 15 and 
the action is sell, then we would take out liquidity from the bid side of the order book. 

The purple colored tree structures display how our order would impact the  limits of the order book: How many
limits we would need to fill and a which price (the price is weighted by the volume of each order). 
The displayed information is for Kraken, Gemini and Coinbase exchanges. 

Then a merged order book displays the same information. This orderbook takes the limits that would be needed to fill
on every individual exchanges, aggregates them, sorts them, and finally it depletes liquidity of a made-up merged exchange.

The last part shows the raw information of the orders filled for each exchange. The way in which the limits are displayed
is a list of tuples (price, volume).

It is also helpful to display the content of the logs in /tmp. You can use the command ```less``` to display the logs input.
```shell
less +FG /tmp/processor.log
```

**Note:** Kraken l2 data feed provides a limited snapshot of the order book, therefore it may take some time to reach the desired
volume as new limit updates need to come.