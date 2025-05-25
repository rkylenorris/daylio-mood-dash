import pandas as pd
from datetime import datetime


def is_weekend(day: int):
    if day == 6 or day == 0:
        return True
    else:
        return False


def is_weekday(day: int):
    if 0 < day < 6:
        return True
    else:
        return False


def create_rolling_calendar(start='2018-01-01', end=datetime.today().strftime('%Y-%m-%d')):
    df = pd.DataFrame({"TimeStamp": pd.date_range(start, end)})
    df['Date'] = pd.to_datetime(df['TimeStamp'])
    df["Day"] = df.TimeStamp.apply(lambda x: x.to_pydatetime().date().strftime('%w'))
    df["DayName"] = df.TimeStamp.apply(lambda x: x.to_pydatetime().date().strftime('%A'))
    df["Week"] = df.Date.apply(lambda x: x.isocalendar()[1])
    df["Month"] = df.TimeStamp.apply(lambda x: x.to_pydatetime().date().month)
    df["MonthName"] = df.TimeStamp.apply(lambda x: x.to_pydatetime().date().strftime('%B'))
    df["Quarter"] = df.TimeStamp.apply(lambda x: x.quarter)
    df["Year"] = df.TimeStamp.apply(lambda x: x.year)
    df['MonthYear'] = df['MonthName'] + "-" + df['Year'].astype(str)
    df['QuarterYear'] = df.TimeStamp.apply(lambda x: f"Q{x.quarter}-{x.year}")
    df['IsWeekend'] = df.Date.apply(lambda x: is_weekend(x.weekday()))
    df['IsWeekday'] = df.Date.apply(lambda x: is_weekday(x.weekday()))
    return df
