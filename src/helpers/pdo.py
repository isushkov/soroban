import pandas as pd
import src.helpers.colors as c

# fs
def load(csvfile, columns=False, allow_empty=False):
    try:
        df = pd.read_csv(csvfile, sep=',', quotechar='"')
        df = df.rename(columns=lambda x: x.strip())
        df = df.apply(lambda col: col.apply(lambda x: x.strip() if isinstance(x, str) else x))
        df.set_index('id', inplace=True)
    except FileNotFoundError:
        if columns:
            df = pd.DataFrame(columns=columns).set_index('id')
        if not allow_empty:
            raise FileNotFoundError(c.z(f'[r]ERROR:[c] csv-file not found: {csvfile}'))
    return df
def save(df, csvfile):
    df = df.reset_index().rename(columns={'index': 'id'})
    df.to_csv(csvfile, index=False)
# filter:select/sort
def filter(df, where=None, where_not=None, sorts=None, allow_empty=False, allow_many=False):
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
        if df.empty and not allow_empty:
            raise Exception(c.z(f'[r]ERROR:[c] no matches found. [y]<addnew> is not allowed.'))
        if len(df) > 1 and not allow_many:
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
def update(df, where, values, allow_addnew=False, allow_many=False):
    """
    :param where: Словарь условий {column_name: value} для поиска строк.
    :param values: Словарь с обновлениями {column_name: new_value}.
    :param allow_addnew: Разрешить добавление строки, если не найдено совпадений.
    :param allow_many: Разрешить обновление, если найдено более одной строки.
    """
    # mask
    mask = pd.Series(True, index=df.index)
    for col, val in where.items():
        mask &= (df[col] == val)
    matches = df[mask]
    # check
    if matches.empty:
        if not allow_addnew:
            raise Exception(c.z(f'[r]ERROR:[c] no matches found. [y]<addnew> is not allowed.'))
        return addnew(df, {**where, **values})
    if len(matches) > 1:
        if not allow_many:
            raise Exception(c.z(f'[r]ERROR:[c] found more than 1 matches. [y]<many> is not allowed.'))
    for key, value in values.items():
        # Check if the value type is compatible with the column type and convert if necessary
        if not pd.api.types.is_dtype_equal(df[key].dtype, pd.Series([value]).dtype):
            value = pd.Series([value]).astype(df[key].dtype).iloc[0]
        df.loc[mask, key] = value
    return df
