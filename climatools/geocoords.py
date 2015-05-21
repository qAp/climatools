



def positivise_longitude(lon):
    if lon >= 0:
        return lon
    else:
        return 180 + (180 + lon)
    
