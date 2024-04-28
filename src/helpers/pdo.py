import pandas as pd
import src.helpers.colors as c

# fs
def load(csvfile, columns=False, empty_allowed=False):
    try:
        df = pd.read_csv(csvfile)
        df = df.rename(columns=lambda x: x.strip())
        df = df.apply(lambda col: col.apply(lambda x: x.strip() if isinstance(x, str) else x))
        df.set_index('id', inplace=True)
    except FileNotFoundError:
        if columns:
            df = pd.DataFrame(columns=columns).set_index('id')
        if not empty_allowed:
            raise FileNotFoundError(c.z(f'[r]ERROR:[c] csvfile not found - {csvfile}'))
    return df
def save(df, csvfile):
    df = df.reset_index().rename(columns={'index': 'id'})
    df.to_csv(csvfile, index=False)
# filter:select/sort
def filter(df, where=None, where_not=None, sorts=None, empty_allowed=False, many_allowed=False):
    if where:
        mask = pd.Series(True, index=df.index)
        for col, val in where.items():
            mask &= (df[col] == val)
        df = df[mask]
    if where_not:
        mask_not = pd.Series(True, index=df.index)
        for col, val in where_not.items():
            mask_not &= (df[col] != val)
        df = df[mask_not]
    if where or where_not:
        if df.empty and not empty_allowed:
            raise Exception(c.z(f'[r]ERROR:[c] no matches found. [y]<addnew> is not allowed.'))
        if len(df) > 1 and not many_allowed:
            raise Exception(c.z(f'[r]ERROR:[c] found more than 1 matches. [y]<many> is not allowed.'))
    if sorts:
        sort_columns = list(sorts.keys())
        ascending = [True if sorts[col] == 'up' else False for col in sort_columns]
        df = df.sort_values(by=sort_columns, ascending=ascending)
    return df
# +
def addnew(df, values):
    if isinstance(values, dict):
        values = pd.DataFrame([values])
    elif isinstance(values, pd.Series):
        values = pd.DataFrame([values])
    return pd.concat([df, values], ignore_index=True)
def update(df, where, values, addnew_allowed=False, many_allowed=False):
    """
    :param where: Словарь условий {column_name: value} для поиска строк.
    :param values: Словарь с обновлениями {column_name: new_value}.
    :param addnew_allowed: Разрешить добавление строки, если не найдено совпадений.
    :param many_allowed: Разрешить обновление, если найдено более одной строки.
    """
    # mask
    mask = pd.Series(True, index=df.index)
    for col, val in where.items():
        mask &= (df[col] == val)
    matches = df[mask]
    # check
    if matches.empty:
        if not addnew_allowed:
            raise Exception(c.z(f'[r]ERROR:[c] no matches found. [y]<addnew> is not allowed.'))
        return addnew(df, {**where, **values})
    if len(matches) > 1:
        if not many_allowed:
            raise Exception(c.z(f'[r]ERROR:[c] found more than 1 matches. [y]<many> is not allowed.'))
    for key, value in values.items():
        df.loc[mask, key] = value
    return df
