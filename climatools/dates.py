

import numpy as np
import pandas as pd



def time2datetimes(ds):
    '''
    Converts time in \'number of days since\' to
    Python datetime objects.
    INPUT:
    ds --- xray Dataset or DataArray object with time dimension
    OUTPUT:
    a Numpy array of Python datetime objects
    '''
    t0 = pd.to_datetime(ds['time'].units.split('since')[-1])
    timestamps = [t0 + pd.DateOffset(days = v)
                  for v in ds['time'].values]
    return np.array([stamp.to_datetime() for stamp in timestamps])



def to_daytime_nighttime(ts, hour_daystart = 8, hour_nightstart = 18):
        '''
        The start hour of daytime and nighttime are defined.
        If the hour of the timestamp is between the start hour of
        daytime and nighttime, its hourstamp is set to the start hour
        of daytime.  If it is smaller, its daystamp is rolled backward
        by one day and its hourstamp is set to the start hour of nighttime.
        If it is larger, its hourstamp i set to the start hour of nighttime.
        INPUT:
        ts --- Pandas Timestamp object
        hour_daystart --- hour of the day that daytime starts (0 to 23)
        hour_nightstart -- hour of the day that nighttime starts (0 to 23)
        '''
        if ts.hour < hour_daystart:
            return (ts - pd.DateOffset(days = 1))\
                   .replace(hour = hour_nightstart,
                            minute = 0, second = 0)
        elif hour_daystart <= ts.hour < hour_nightstart:
            return ts.replace(hour = hour_daystart,
                              minute = 0, second = 0)
        else:
            return ts.replace(hour = hour_nightstart,
                              minute = 0, second = 0)



    
def longitude_to_houroffset(lon = 0):
    '''
    returns how many hours to add/subtract from UTC\'s,
    given longitude.
    e.g. 0 < longitude <= 7.5 is +0 hours;
        -7.5 <= longitude < 0 is + 0 hours;
        7.5 < longitude <= 7.5 + 15 is + 1 hours.
    '''
    dlon = 15.
    if 0 < lon < 180:
        lon_from_0 = lon
    elif 180 < lon < 360:
        lon_from_0 = 360 - lon
    else:
        raise ValueError('0 < longitude < 180 and 180 < longitude < 360 degrees only')
    
    if (lon_from_0 - dlon / 2) < 0:
        return 0.
    else:
        tz = np.ceil((lon_from_0 - dlon / 2) / dlon)
        return - tz if 180 < lon < 360 else tz



        
def UTCtime_to_localtime(datetime_UTC, lon = 0.):
    '''
    Converts UTC time to local time given longitude.
    This assumes that there are 24 time zones, and each spans 15 degrees.
    '''
    hour_offset = longitude_to_houroffset(lon)
    return datetime_UTC + pd.Timedelta(hours = hour_offset)




        
def UTC_to_local_datetime_countrywise(datetime_UTC, longitude = 0.1275, latitude = 51.5072):
    '''
    Convert time from UTC to local time, given longitude and latitude, using
    https://maps.googleapis.com/maps/api/timezone/json?location=LAT,LON&timestamp=TIME_SINCE_1970_00:00:00
    INPUT:
    datetime_UTC --- pandas Timestamp, or datetime.datetime
    longitude --- longitude of location [degrees]
    latitude --- latitude of location [degrees]
    OUTPUT:
    datetime with local time
    NOTE:
    This only works for where there is data. i.e. where there is a country
    '''
    dt0_google = pd.Timestamp('1970-1-1 00:00:00')
    timedelta = datetime_UTC - dt0_google
    timedelta_in_seconds = timedelta.days * 24 * 60**2 + timedelta.seconds
    
    url = 'https://maps.googleapis.com/maps/api/timezone/json?location={},{}&timestamp={}'\
          .format(latitude, longitude, timedelta_in_seconds)

    with urllib.request.urlopen(
        url.format(latitude, longitude, timedelta_in_seconds)) as response:
        timezone = json.loads(response.read().decode('utf-8'))
        
    return datetime_UTC + pd.Timedelta(seconds = timezone['rawOffset'])


    
def average_over_time(da):
    '''
    Average over time dimension of DA, while
    retaining its units and long_name attributes
    '''
    avgda = da.mean(dim = 'time')
    avgda.attrs['units'] = da.attrs['units']
    avgda.attrs['long_name'] = da.attrs['long_name']
    return avgda
