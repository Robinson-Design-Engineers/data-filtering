import numpy as np

from datetime import datetime
import matplotlib.pyplot as plt


def threshold_filter(df, value_clm, datetime_clm, min_threshold=None, max_threshold=None, nofilter_date_time_range=None):
    """
    Function Info:

    Values:
    df:                     filter dataframe, pandas dataframe
    value_clm:              name of value column, str
    datetime_clm:           name of datetime column, str
    min_threshold:          minimum allowable value
    max_threshold:          maximum allowable value
    date_time_range:        list of 2 values: [start date, end date]
    """

    # keep only rows that meet threshold conditions
    # max threshold
    if nofilter_date_time_range==None:
        if min_threshold==None:
            df = df[(df[value_clm] <= max_threshold)]
        elif max_threshold==None:
            df = df[(df[value_clm] >= min_threshold)]
    else:
        if min_threshold==None:
            df = df[(df[value_clm] <= max_threshold) | 
                    (df[datetime_clm] >= np.datetime64(nofilter_date_time_range[0])) & 
                    (df[datetime_clm] <= np.datetime64(nofilter_date_time_range[1]))]
        elif max_threshold==None:
            df = df[(df[value_clm] >= min_threshold) | 
                    (df[datetime_clm] >= np.datetime64(nofilter_date_time_range[0])) & 
                    (df[datetime_clm] <= np.datetime64(nofilter_date_time_range[1]))]
        else:
             df = df[(df[value_clm] >= min_threshold) &
                     (df[value_clm] <= max_threshold) | 
                     (df[datetime_clm] >= np.datetime64(nofilter_date_time_range[0])) & 
                     (df[datetime_clm] <= np.datetime64(nofilter_date_time_range[1]))]

    return df


def despike_simple_2_neighbors(df, value_clm, spike_threshold):
    """
    Function Info:

    Values:
    df:                             filter dataframe
    value_clm:                      name of value column, str
    spike_threshold:                first iteration's threshold for spike - max allowable difference between average and actual data point
    """

    # simple spike check
    val_i = np.array(df[value_clm][2:])
    val_i_1 = np.array(df[value_clm][1:-1])
    val_i_2 = np.array(df[value_clm][:-2])

    spike_ref = (val_i_2+val_i)/2
    df['spike_check'] = [np.nan, np.nan] + list(np.abs(val_i_1-spike_ref))

    # keep anything that is not a spike
    df = df[(df['spike_check'] < spike_threshold) | (np.isnan(df['spike_check']))]

    # drop unneccesary columns
    df = df.drop('spike_check', axis=1)

    return df


def despike_simple_12_neighbors(df, value_clm, moving_avg_spike_threshold):
    """
    Function Info:

    Values:
    df:                             filter dataframe
    value_clm:                      name of value column, str
    moving_avg_spike_threshold:     moving average threshold -  max allowable difference between average and actual data point
    """

    # moving average spike removal - 13 points, 6 points on each side of point i, so point i-6 to point i+6
    val_i_6 = np.array(df[value_clm][:-12])
    val_i_5 = np.array(df[value_clm][1:-11])
    val_i_4 = np.array(df[value_clm][2:-10])
    val_i_3 = np.array(df[value_clm][3:-9])
    val_i_2 = np.array(df[value_clm][4:-8])
    val_i_1 = np.array(df[value_clm][5:-7])
    val_i = np.array(df[value_clm][6:-6])
    val_ip1 = np.array(df[value_clm][7:-5])
    val_ip2 = np.array(df[value_clm][8:-4])
    val_ip3 = np.array(df[value_clm][9:-3])
    val_ip4 = np.array(df[value_clm][10:-2])
    val_ip5 = np.array(df[value_clm][11:-1])
    val_ip6 = np.array(df[value_clm][12:])

    spike_ref_avg = (val_i_6+val_i_5+val_i_4+val_i_3+val_i_2+val_i_1+val_ip1+val_ip2+val_ip3+val_ip4+val_ip5+val_ip6)/12
    df['moving_avg'] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan] + list(spike_ref_avg) + [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]
    df['moving_avg_check'] = [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan] + list(np.abs(val_i-spike_ref_avg)) + [np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]

    # keep anything that is not a spike
    df = df[(df['moving_avg_check'] < moving_avg_spike_threshold) | (np.isnan(df['moving_avg_check']))]

    # drop unneccesary columns
    df = df.drop(['moving_avg', 'moving_avg_check'], axis=1)

    return df


# rate of rise filter
def rateofrise_filter(df, value_clm, datetime_clm, rateofrise_threshold):
    """
    Function Info:

    Values:
    df:                             filter dataframe
    value_clm:                      name of value column, str
    rateofrise_threshold:           rate-of-rise threshold - max allowable rate of rise
    """

    # calc new rate of rise variables
    df['change_val'] = df[value_clm].diff().abs()
    df['change_time'] = df[datetime_clm].diff().dt.total_seconds()
    df['change_per_time'] = df['change_val']/df['change_time']

    df['change_val'][0] = 0.0
    df['change_time'][0] = 0.0
    df['change_per_time'][0] = 0.0
    df.head()

    condition_rate_of_rise = df['change_per_time'] < rateofrise_threshold # condition that if True, you keep this datapoint

    # keep only rows that meet rate of rise condition
    df = df[condition_rate_of_rise]

    # drop unneccesary columns
    df = df.drop(['change_val', 'change_time', 'change_per_time'], axis=1)

    return df


# flat line test
def remove_consecutive_duplicates(df, value_clm, n=10): # ChatGPT function
    """
    Function Info:

    Values:
    df:                 filter dataframe
    value_clm:          name of value column, str
    n:                  number of allowable flat line points, default 10
    """

    # Create a boolean mask that is True where there are n consecutive duplicates
    mask = (df[value_clm] == df[value_clm].shift())  # Compare current value with previous value
    count = mask.cumsum() - mask.cumsum().where(~mask).ffill().fillna(0)  # Count consecutive matches
    
    # Remove rows where the count of consecutive duplicates is >= n
    to_remove = count >= (n - 1)  # We need n consecutive, so count >= (n-1)
    
    # Filter out rows with consecutive duplicates
    return df[~to_remove]