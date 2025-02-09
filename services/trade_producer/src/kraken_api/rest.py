import json
from typing import Dict, List, Tuple

import requests
from loguru import logger
from time import sleep
from karaken_api.trade import Trade
from datetime import datetime, timezone

class KrakenRestApiMultipleProducts:
    def __init__(
            self,
            product_ids :List[str],
            last_n_days: int,
    )->None:
        
        self.product_ids = product_ids

        self.kraken_apis = [
            KrakenRestApi(product_ids=[product_id], last_n_days=last_n_days)
            for product_id in product_ids
        ]
    def get_trades(self)->List[Dict]:
        """
        Get trade data from each Kraken_Api in  self.kraken_apis
        Retruns list with all trades from all kraken_apis.
        Args:
            None
        Retrun:
            List(Dict): list of dictionaries, where each dictionary contain the trade data for 
            all product_ids in self.product_ids
         
        """
        trades : List[Dict]= []

        for kraken_api in self.kraken_apis:
            if kraken_api.is_done():
                # if we are done fetching historical data for this product_id, we skip it.
                continue

            else:
                trades += kraken_api.get_trades()

        return trades
    def is_done(self)->bool:
        """
        Return true if all kraken_api in self.kraken_apis are done fetching historical data
        It returns False, otherwise!

        """
        for kraken_api in self.kraken_apis:
            if not kraken_api.is_done():
                return False
            
        return True


        

class KrakenRestApi:
    #URL = "https://api.kraken.com/0/public/Trades"

    URL = 'https://api.kraken.com/0/public/Trades?pair={product_id}&since={since_sec}'

    def __init__(
          self,
          product_id: str,
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
        self.product_id = product_id
        
    
        self.from_ms, self.to_ms = self._init_from_to_ms(last_n_days)
        logger.debug(f'Initializing KrakenRestApi: from_ms = {self.from_ms}, to_ms = {self.to_ms}')
        self.last_trade_ms = self.from_ms
        # are we done fetching the historical data?
        # yes, if the last batch of trades has a data['result'][product_id]['last'] >= self.to_ms
        self._is_done = False

    @staticmethod
    def _init_from_to_ms(last_n_days: int)->Tuple[int, int]:
        """
        Returns the frrom_mos to_ms timestamps for the historical data
        These values are calculated using todays date at midnight and the lat_n_days
        Args:
            last_n_days (int): number of days of historical data to fetch
        Returns:
            Tuple[int, int]: from_ms and to_ms timestamps
        """
        # get current date at midnight using UTC
        from datetime import datetime, timezone
        today_date = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        # today_date to milliseconds
        to_ms = int(today_date.timestamp() * 1000)
        # from_ms is last_n_days ago from today, so we subtract the number of milliseconds in last_n_days days
        from_ms = to_ms - last_n_days * 24 * 60 * 60 * 1000
        return from_ms, to_ms

    def get_trades(self) -> List[Trade]:
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
        url = self.URL.format(product_id = self.product_id, since_sec = since_sec)
        response = requests.request("GET", url, headers=headers, data=payload)
    # parse string into dictionary
        data = json.loads(response.text)
    #TODO    check for errors, right now we are not doing any error handling
        if ('error' in data)and('EGeneral:Too many requests'in data['error']):
        # slow down the rate at which we are making requests to KrakenRestApi
            logger.info('too many requests. Sleeping for 30 seconds')
            sleep(30)
         
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
        trades = [
            Trade(
                price =float(trade[0]),
                volume = float(trade[1]),
                timestamp_ms = int(trade[2])*1000,
                product_id = self.product_id,
            ) 
            for trade in data['result'][self.product_id]
        ]
        # filter out the trades that are outside the time stamp range
        trades = [trade for trade in trades if trade.timestamp_ms <= self.to_ms]
        # check if we are done fetching the historical data
        last_ts_in_ns = int(data['result']['last'])
        # convert the last timestamp from nanoseconds to milliseconds
        self.last_trade_ms = last_ts_in_ns // 1_000_000
        self._is_done = self.last_trade_ms >= self.to_ms
        logger.debug(f'fetching {len(trades)} trades')
        # log the last trade timestamp
        logger.debug(f'last trade timestamp: {self.last_trade_ms}')
        logger.debug(f'Last trade timestamp: {ts_to_date(self.last_trade_ms)}')
        sleep(1)
        return trades
           
        
     


    def is_done(self)-> bool:

        return self._is_done
    
          
    def ts_to_date(ts: int) -> str:
         """
         Transform a timestamp in Unix milliseconds to a human-readable date
          Args:
        ts (int): A timestamp in Unix milliseconds
    Returns:
        str: A human-readable date in the format '%Y-%m-%d %H:%M:%S'
    """
    
         return datetime.fromtimestamp(ts / 1000, tz=timezone.utc).strftime(
        '%Y-%m-%d %H:%M:%S'
    )