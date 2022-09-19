import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

import random
import os

## Determine historical average per node RT (N.B. dependent only on date and not time!)
mean_total_lmp_rt = data[['pnode_id', 'time_beginning_ept', 'total_lmp_rt']].groupby(
    ['pnode_id', 'time_beginning_ept']).mean()
mean_total_lmp_rt = mean_total_lmp_rt.rename(columns={'total_lmp_rt': 'mean_total_lmp_rt'})
mean_total_lmp_rt = mean_total_lmp_rt.reset_index()

data['Key'] = data['pnode_id'].astype(str) + data['time_beginning_ept'].astype(str)
mean_total_lmp_rt['Key'] = mean_total_lmp_rt['pnode_id'].astype(str) + mean_total_lmp_rt['time_beginning_ept'].astype(
    str)

mean_total_lmp_rt = mean_total_lmp_rt.drop(['pnode_id', 'time_beginning_ept'], axis=1)
data = pd.merge(data, mean_total_lmp_rt, how='left', on='Key')

# # Determine historical average per node DA (N.B. dependent only on date and not time!)
mean_total_lmp_da = data[['pnode_id', 'time_beginning_ept', 'total_lmp_da']].groupby(
    ['pnode_id', 'time_beginning_ept']).mean()
mean_total_lmp_da = mean_total_lmp_da.rename(columns={'total_lmp_da': 'mean_total_lmp_da'})
mean_total_lmp_da = mean_total_lmp_da.reset_index()

data['Key'] = data['pnode_id'].astype(str) + data['time_beginning_ept'].astype(str)
mean_total_lmp_da['Key'] = mean_total_lmp_da['pnode_id'].astype(str) + mean_total_lmp_da['time_beginning_ept'].astype(
    str)

mean_total_lmp_da = mean_total_lmp_da.drop(['pnode_id', 'time_beginning_ept'], axis=1)
data = pd.merge(data, mean_total_lmp_da, how='left', on='Key')

# Retain index as key
data['index_key'] = data.index


def forecast(data, criterion_str, average_data, average_column, output_name_str='forecast'):
    # Creates arbitrary forecasts
    forecasts = []
    mean_av = average_data[f'{average_column}'].mean()
    mean_stdev = 3 * (average_data[f'{average_column}'].std())

    count = 0
    mean_applied = 0

    for price in data[criterion_str]:
        # random_k = random.randrange(-5, 5)
        # forecast = price * (1 + random_k / 100)
        # forecasts.append(forecast)

        count += 1
        if (mean_av + mean_stdev) < price or price < (mean_av - mean_stdev):
            forecast = mean_av
            forecasts.append(forecast)
            mean_applied += 1
        else:
            random_k = random.randrange(-5, 5)
            forecast = price * (1 + random_k / 100)
            forecasts.append(forecast)

    forecasts_df = pd.DataFrame(forecasts, columns=[f'{output_name_str}'])
    data = data.reset_index(drop=True)
    data_with_forecasts = data.join(forecasts_df)

    return data_with_forecasts


# Create a forecast within 10% of bid/sell price for 70% of nodes
accurate_forecast2017 = data.sample(frac=0.7)

node_id = 51205
peak_start = '07:00:00'
peak_end = '23:00:00'
accurate_forecast2017 = accurate_forecast2017.loc[(accurate_forecast2017['pnode_id'] == node_id) & (accurate_forecast2017['time_beginning_ept'] > peak_start) & (accurate_forecast2017['time_beginning_ept'] <= peak_end)]


accurate_forecast2017_rt = forecast(accurate_forecast2017, 'total_lmp_rt', mean_total_lmp_rt, 'mean_total_lmp_rt',
                                    'forecast_total_lmp_rt')
accurate_forecast2017_da = forecast(accurate_forecast2017, 'total_lmp_da', mean_total_lmp_da, 'mean_total_lmp_da',
                                    'forecast_total_lmp_da')

# Create a forecast within 10% of historical average bid/sell price for 30% of nodes
av_forecast2017 = data.drop(accurate_forecast2017.index)

av_forecast2017 = av_forecast2017.loc[(av_forecast2017['pnode_id'] == node_id) & (accurate_forecast2017['time_beginning_ept'] > peak_start) & (accurate_forecast2017['time_beginning_ept'] <= peak_end)]

av_forecast2017_rt = forecast(av_forecast2017, 'mean_total_lmp_rt', mean_total_lmp_rt, 'mean_total_lmp_rt',
                              'forecast_total_lmp_rt')
av_forecast2017_da = forecast(av_forecast2017, 'mean_total_lmp_da', mean_total_lmp_da, 'mean_total_lmp_da',
                              'forecast_total_lmp_da')

# Complete dataframe
pjm2017_forecasts_rt = pd.concat([accurate_forecast2017_rt, av_forecast2017_rt])
pjm2017_forecasts_rt.drop(pjm2017_forecasts_rt.columns[:-2], axis=1, inplace=True)
pjm2017_forecasts_rt.sort_values(by=['index_key'])

pjm2017_forecasts_da = pd.concat([accurate_forecast2017_da, av_forecast2017_da])
pjm2017_forecasts_da.drop(pjm2017_forecasts_da.columns[:-2], axis=1, inplace=True)
pjm2017_forecasts_da.sort_values(by=['index_key'])

data = pd.merge(data, pjm2017_forecasts_rt, how='inner', on='index_key')
data = pd.merge(data, pjm2017_forecasts_da, how='inner', on='index_key')

data.drop(['Key', 'index_key'], axis=1, inplace=True)

data_name = 'pjm2017_forecasts'
root = 'data'
data.to_csv(f'{root}/{data_name}.csv', index=False)
