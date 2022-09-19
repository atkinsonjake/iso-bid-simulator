import pandas as pd

class PreprocessPjmData:

    def __init__(self):
        pass


    def _drop_redundant_attributes(self, df):
        # Check these columns if modifying data!
        df = df.drop(df.columns[[0, 4, 5, 7]], axis=1, inplace=True)
        return df


    def _transform_columns(self, df, column_name: str):
        # For PJM column = "datetime_beginning_ept"
        df[column_name] = df[column_name].astype(str)
        return df

    def _transform_date_columns(self, df):
        df = self._transform_columns(df, "datetime_beginning_ept")
        df[['date_beginning_ept', 'time_beginning_ept']] = df['datetime_beginning_ept'].str.split(" ", 1, expand=True)
        df = df.drop(['datetime_beginning_ept'], axis=1, inplace=True)
        return df


    def _convert_time(self, twelve_hr_time):
        # Reformats 12hr time to 24hr

        if len(twelve_hr_time) < 11:
            time = str(0) + str(twelve_hr_time)
        else:
            time = twelve_hr_time

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


    def _transform_time(self, df, twelve_hr_time_column):
        twenty_four_times = []

        for time_twelve in df[twelve_hr_time_column]:
            time_twenty_four = self._convert_time(time_twelve)
            twenty_four_times.append(time_twenty_four)

        time_beginning_ept = pd.DataFrame(twenty_four_times, columns=['time_beginning_ept'])
        df = pd.concat([df, time_beginning_ept], axis=1)

        return df
