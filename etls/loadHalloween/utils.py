def show_or_load(df, table_name, schema_name, engine, load=False):
    if load:
        print(f'Loading {table_name}')
        df.to_sql(table_name, schema=schema_name, con=engine,
                  if_exists='append', index=False)
    else:
        print(df.head())
