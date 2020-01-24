

def make_query(param=None):
    molecules = {'h2o', 'co2', 'o3', 'n2o', 'ch4'}
    q = {}
    for n, v in param.items():
        if n == 'molecule' and type(v) == dict:
            for mol, conc in v.items():
                q[f'param.molecule.{mol}'] = conc
            for mol in molecules - set(v.keys()):
                q[f'param.molecule.{mol}'] = {'$exists': 0}
        else:
            q[f'param.{n}'] = v
    q = {n: v for n, v in q.items()
         if n == 'param.conc' or (n != 'param.conc' and v)}
    return q
