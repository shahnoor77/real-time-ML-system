from typing import List, Dict
import requests
import json
from loguru import logger
class KrakenRestApi:
    #URL = "https://api.kraken.com/0/public/Trades"

    URL = "https://api.kraken.com/0/public/Trades?pair={product_id}&since={since_sec}"

    def __init__(
          self,
          product_ids: List[str],
          from_ms: int,
          to_ms: int,
    )-> None:
        """
        basic initialization of the kraken rest api 
        Args:
            product_ids (List[str]): list of product ids
            from_ms (int): start time in milliseconds
            to_ms (int): end time in milliseconds
        Returns:   
            None
        """
        self.product_ids = product_ids
        self.from_ms = from_ms
        self.to_ms = to_ms

        # are we done fetching the historical data?
        # yes, if the last batch of trades has a data['result'][product_id]['last'] >= self.to_ms
        self._is_done = False

    def get_trades(self) -> List[Dict]:
        """
            fetches the trades from the rest api of kraken and return
            as the list of dictionaries.
        Args:
            None
        Returns:
            List[Dict]: list of dictionaries containing trades
     
        """
    

        payload = {}
        headers = {'Accept': 'application/json'}
    # replace the product_id and since_ms with the actual values
        since_sec = self.from_ms // 1000
        url = self.URL.format(product_id = self.product_ids[0], since_sec = since_sec)
        response = requests.request("GET", url, headers=headers, data=payload)
    # parse string into dictionary
        data = json.loads(response.text)
    #TODO    check for errors, right now we are not doing any error handling
    #if data['error'] is not None:
    #   raise Exception(data['error'])
         
        #print(response.text)
        
     
     
        
    #for trade in data['result'][self.product_ids[0]]:
    #       trades.append(
    #           {
    #               'trade_id': trade[2],
    #               'price': trade[0],
    #               'size': trade[1],
    #               'time': trade[2]
    #          }
    #     )
    # little trick 
    # using list comprehension
        trades = []
        trades = [
            {
               
                'price': float(trade[0]),
                'volume': float(trade[1]),
                'time': int(trade[2]),
                'product_id': self.product_ids[0],
            } for trade in data['result'][self.product_ids[0]]
        ]
        
        # check if we are done fetching the historical data
        last_ts_in_ns = int(data['result']['last'])
        # convert the last timestamp from nanoseconds to milliseconds
        last_ts = last_ts_in_ns // 1_000_000
        if last_ts >= self.to_ms:
            #yes, we are done
            self._is_done = True
        logger.debug(f'fetching {len(trades)} trades')
        # log the last trade timestamp
        logger.debug(f'last trade timestamp: {last_ts}')
           
        
     


    def is_done(self)-> bool:

        return self._is_done
        
            
    