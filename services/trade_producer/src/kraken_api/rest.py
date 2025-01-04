from typing import List, Dict, Tuple
import requests
import json
from loguru import logger
class KrakenRestApi:
    #URL = "https://api.kraken.com/0/public/Trades"

    URL = "https://api.kraken.com/0/public/Trades?pair={product_id}&since={since_sec}"

    def __init__(
          self,
          product_ids: List[str],
          #from_ms: int,
          #to_ms: int,
         last_n_days: int 
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
        # self.from_ms = from_ms
        # self.to_ms = to_ms
        self.from_ms, self.to_ms = self._init_from_to_ms(last_n_days)
        self.last_trade_ms = self.from_ms
        # are we done fetching the historical data?
        # yes, if the last batch of trades has a data['result'][product_id]['last'] >= self.to_ms
        self._is_done = False

        
        # initializing kraken from_ms to the last trade timestamp
        logger.info(f'Initializing kraken : from_ms = {self.from_ms}, to_ms = {self.from_ms}')

    @staticmethod
    def _init_from_to_ms(last_n_days: int)->tuple[int, int]:
        """
        Returns the frrom_mos to_ms timestamps for the historical data
        These values are calculated using todays date at midnight and the lat_n_days
        Args:
            last_n_days (int): number of days of historical data to fetch
        Returns:
            Tuple[int, int]: from_ms and to_ms timestamps
        """
        import time
        # get current date at midnight using UTC
        from datetime import datetime
        from datetime import timezone
        today_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        # today_date to milliseconds
        to_ms = int(today_date.timestamp() * 1000)
        # from_ms is last_n_days ago from today, so we subtract the number of milliseconds in last_n_days days
        from_ms = to_ms - last_n_days * 24 * 60 * 60 * 1000
        return from_ms, to_ms

    def get_trades(
            self,
    ) -> List[dict]:
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
        since_sec =self.last_trade_ms // 1000
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
        # filter out the trades that are outside the time stamp range
        trades = [trade for trade in trades if trade['time'] <= self.to_ms//1000]
        # check if we are done fetching the historical data
        last_ts_in_ns = int(data['result']['last'])
        # convert the last timestamp from nanoseconds to milliseconds
        self.last_trade_ms = last_ts_in_ns // 1_000_000
        self._is_done = self.last_trade_ms >= self.to_ms
        logger.debug(f'fetching {len(trades)} trades')
        # log the last trade timestamp
        logger.debug(f'last trade timestamp: {self.last_trade_ms}')
        return trades
           
        
     


    def is_done(self)-> bool:

        return self._is_done
    
          
            
    