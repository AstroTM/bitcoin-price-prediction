"""Script to gather market data from bitfinex Spot Price API."""
import requests
from pytz import utc
from datetime import datetime
import time
from apscheduler.schedulers.blocking import BlockingScheduler
import sqlite3

def tick():
    conn = sqlite3.connect('/home/mattyab/bitcoin-price-prediction/priceData.db')

    c = conn.cursor()

    """Gather market data from bitfinex Spot Price API and insert them into a
       MongoDB collection."""
    ticker = requests.get('https://api.bitfinex.com/v2/ticker/tETHBTC').json()
    depth = requests.get('https://api.bitfinex.com/v2/trades/tETHBTC/hist').json()
    date = time.time()
    price = float(ticker[6])

    asks = []
    bids = []

    for trade in depth:
        if trade[2] < 0:
            asks.append(-trade[2])
        else:
            bids.append(trade[2])

    v_bid = sum([bid for bid in bids])
    v_ask = sum([ask for ask in asks])

    command = 'INSERT INTO prices VALUES (' + str(date) + ', ' + str(price) + ', ' + str(v_bid) + ', ' + str(v_ask) + ');'
    #command = 'DELETE FROM prices;'
    c.execute(command)
    #print(date, price, v_bid, v_ask)

    print('Inserted price: ' + str(price) + ' at time: ' + str(date))

    # Save (commit) the changes
    conn.commit()

    # We can also close the connection if we are done with it.
    # Just be sure any changes have been committed or they will be lost.
    conn.close()

def main():
    """Run tick() at the interval of every ten seconds."""
    scheduler = BlockingScheduler(timezone=utc)
    scheduler.add_job(tick, 'interval', seconds=10)
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == '__main__':
    main()

