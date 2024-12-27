from typing import List, Dict
from websocket import create_connection
import json
class KrakenWebsocketTradeAPI:
    URL = "wss://ws.kraken.com/v2"

    def __init__(
            self,
            product_id: str,
        ):
        
         self.product_id = product_id

         self._ws = create_connection(self.URL)
         print("Connected to Kraken Websocket")

         # subscribe to the trade for the given "product_id"
         self._subscribe(product_id)

    def _subscribe(self, product_id: str):
         """
            Subscribe to the trade for the given "product_id"
         """
         
         print(f"Subscribing to trade for {product_id}")
         # subscribe to the trade for the given "product_id"

         msg = {
             "method": "subscribe",
             "params":{
                  "channel": "trade",
                  "symbol":[
                      product_id,
                  ],
                'snapshot': False
             }
         }
         self._ws.send(json.dumps(msg)) # send the message to the websocket
                                            # json.dump encode the message  from the dictionary to a string
         print("subscription worked!")

        # dumping the first two messages because they are not trade messages
        # they are subscription confirmation messages
         _ = self._ws.recv()
         _ = self._ws.recv()
         

    def get_trades(self)->List[Dict]:
        #mock_trades = [
        #  {
        #     "price": 10000,
        #    "volume": 0.1,
        #   "timestamp": 1609459200,
        #  "product_id": "BTC-USD"
        #},
        #{
        #   "price": 30000,
        #  "volume": 0.1,
        # "timestamp": 1609459240,
        #"product_id": "BTC-USD"
        #}
        #]

     message = self._ws.recv() # receive the message from the websocket
     if 'heartbeat' in message:
         # if the message is a heartbeat message, return an empty list
         return []
     # parse the message to a dictionary
     message = json.loads(message)
    
     trades = []
     for trade in message['data']:
         trade.append({
            'product_id': self.product_id,
            'price': trade['price'],
            'volume': trade['qty'],
            'timestamp': trade['timestamp'],
          })
         
     return trades
     
     #print(f"Received message: {message}")

     #return message