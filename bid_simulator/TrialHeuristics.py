# v1 July 2021

# Modules
import pandas as pd
from numpy.core.defchararray import lower


# Calculate Delta for various heuristics
def bid_clearance(sord, bid, price):
    clearance = False

    if sord == 'inc':
        if bid <= price:
            clearance = True
    if sord == 'dec':
        if bid >= price:
            clearance = True

    return clearance


def delta(charge, credit):
    """
    Function takes a demand or supply instruction,
    day-ahead market price and real-time market price.

    Outputs delta.

    """

    return credit - charge


def delta_on_data(demand_supply_str, data, rt_market_price_str, da_market_price_str, bid_str, adjustment=0):
    """
    Function takes a demand or supply instruction, dataset containing bid information,
    attribute detailing real-time market prices, attribute detailing day-ahead market
    prices to compute delta and attribute detailing bid prices.

    Output contains the percentage of bids cleared and delta on the input.
    """

    total_bids = 0
    bids_cleared = 0
    total_delta = 0
    charges = 0

    adjusted_bid = data[f'{bid_str}'] + adjustment
    bids = adjusted_bid.tolist()
    
    rt_price = data[f'{rt_market_price_str}'].tolist()
    da_price = data[f'{da_market_price_str}'].tolist()

    demand_supply = lower(demand_supply_str)

    if demand_supply == 'supply':
        for (bid, price_rt, price_da) in zip(bids, rt_price, da_price):
            total_bids += 1
            if bid < price_da:
                bids_cleared += 1
                charges += price_rt
                delta = price_da - price_rt
                total_delta += delta

    elif demand_supply == 'demand':
        for (bid, price_rt, price_da) in zip(bids, rt_price, da_price):
            total_bids += 1

            if bid > price_da:
                bids_cleared += 1
                charges += price_da
                delta = price_rt - price_da
                total_delta += delta

    pc_bids_cleared = round((bids_cleared / total_bids) * 100, 2)

    return pc_bids_cleared, total_delta


def InitiateBids(name, data, forecasted_da_lmp, forecasted_rt_lmp, rt_market_price_str, da_market_price_str, dates,
                 times,
                 bid_adjustment=0):
    """
    """

    total_bids = 0
    bids_cleared = 0
    total_delta = 0
    charges = 0
    bid_count = 0

    # Track prices of successful bids and delta
    node_ids = []
    da_prices = []
    rt_prices = []
    cleared_delta = []
    date = []
    time = []
    bid_type = []

    # Convert dataframe columns to lists
    node_id = data['pnode_id'].tolist()
    da_price = data[f'{da_market_price_str}'].tolist()
    rt_price = data[f'{rt_market_price_str}'].tolist()
    da_forecast = data[f'{forecasted_da_lmp}'].tolist()
    rt_forecast = data[f'{forecasted_rt_lmp}'].tolist()
    dates = data[f'{dates}'].tolist()
    times = data[f'{times}'].tolist()

    for (node_id, da_price, rt_price, da_forecast, rt_forecast, datex, timex) in zip(node_id, da_price, rt_price,
                                                                                     da_forecast,
                                                                                     rt_forecast, dates, times):
        bid_count += 1
        print(bid_count)
        if da_forecast > rt_forecast:
        # if da_price > rt_price:
            print('INC bid executed.')
            bid = da_forecast * (1 - (bid_adjustment))

            if bid_clearance('inc', bid, da_price):
                print('INC bid cleared.')
                total_bids += 1
                bids_cleared += 1
                charges += rt_price
                node_ids.append(node_id)
                da_prices.append(da_price)
                rt_prices.append(rt_price)
                date.append(datex)
                time.append(timex)
                total_delta += delta(rt_price, da_price)
                cleared_delta.append(delta(rt_price, da_price))
                bid_type.append("INC")
            else:
                print('INC bid rejected.')

        else:
            print('DEC bid executed.')
            total_bids += 1
            bid = da_forecast * (1 + (bid_adjustment))

            if bid_clearance('dec', bid, da_price):
                print('DEC bid cleared.')
                bids_cleared += 1
                charges += da_price
                node_ids.append(node_id)
                da_prices.append(da_price)
                rt_prices.append(rt_price)
                date.append(datex)
                time.append(timex)
                total_delta += delta(da_price, rt_price)
                cleared_delta.append(delta(da_price, rt_price))
                bid_type.append("DEC")
            else:
                print('DEC bid rejected.')


    node_ids = pd.DataFrame(node_ids, columns=['node_id'])
    da_prices = pd.DataFrame(da_prices, columns=['da-lmp'])
    rt_prices = pd.DataFrame(rt_prices, columns=['rt-lmp'])
    cleared_delta = pd.DataFrame(cleared_delta, columns=['delta'])
    date = pd.DataFrame(date, columns=['date_ept'])
    time = pd.DataFrame(time, columns=['time_ept'])
    bid_type = pd.DataFrame(bid_type, columns=['type'])

    prices = pd.concat([node_ids, da_prices, rt_prices, cleared_delta, date, time, bid_type], axis=1)
    prices['strategy'] = name

    return prices, total_delta, (bids_cleared / total_bids)
