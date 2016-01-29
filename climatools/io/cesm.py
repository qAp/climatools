


import xray



def load_camhistory(readfrom=None):
    with xray.open_dataset(readfrom, decode_cf=False) as ds:
        return ds.copy(deep = True)



