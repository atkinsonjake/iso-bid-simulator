import pandas as pd

data = pd.read_csv('pjm_data_2017.csv')

# Check these columns if modifying data!
data = data.drop(data.columns[[0, 4, 5, 7]], axis=1, inplace=True)
data['datetime_beginning_ept'] = data['datetime_beginning_ept'].astype(str)
data[['date_beginning_ept', 'time_beginning_ept']] = data['datetime_beginning_ept'].str.split(" ", 1, expand=True)
data = data.drop(['datetime_beginning_ept'], axis=1, inplace=True)


# Reformat time to 24hr
def convert_time(twelve_hour):
    global time

    if len(twelve_hour) < 11:
        time = str(0) + str(twelve_hour)
    else:
        time = twelve_hour

    if time[-3:] == ' AM':
        if time[:2] == '12':
            newtime = str('00' + time[2:-3])
        else:
            newtime = time[:-3]
    else:
        if time[:2] == '12':
            newtime = time[:-2]
        else:
            newtime = str(int(time[:2]) + 12) + time[2:-3]

    return newtime


twenty_four_times = []
for time_twelve in data['time_beginning_ept']:
    time_twenty_four = convert_time(time_twelve)
    twenty_four_times.append(time_twenty_four)


data.drop(['time_beginning_ept'], axis=1, inplace=True)
time_beginning_ept = pd.DataFrame(twenty_four_times, columns=['time_beginning_ept'])
data = pd.concat([data, time_beginning_ept], axis=1)
