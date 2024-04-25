import pandas as pd

def get_df(csvfile, columns=False):
    try:
        df = pd.read_csv(csvfile)
        df = df.rename(columns=lambda x: x.strip())
        df = df.apply(lambda col: col.apply(lambda x: x.strip() if isinstance(x, str) else x))
        df.set_index('id', inplace=True)
        return df
    except FileNotFoundError:
        if columns:
            return pd.DataFrame(columns=columns).set_index('id')
        return False
