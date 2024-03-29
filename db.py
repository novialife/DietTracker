import sqlite3
import pandas as pd


def read_data(db_path, table_name):
    conn = sqlite3.connect(db_path)
    query = f"SELECT * FROM `{table_name}`"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df


def save_data(df, db_path, table_name):
    conn = sqlite3.connect(db_path)
    df.to_sql(table_name, conn, if_exists="append", index=False)
    conn.close()

def delete(db_path, table_name, column_name, value, additional_condition=""):
    conn = sqlite3.connect(db_path)
    query = f"DELETE FROM `{table_name}` WHERE `{column_name}` = '{value}' {additional_condition}"
    conn.execute(query)
    conn.commit()
    conn.close()

def change(db_path, table_name, column_name, value, new_value):
    conn = sqlite3.connect(db_path)
    query = f"UPDATE `{table_name}` SET `{column_name}` = '{new_value}' WHERE `{column_name}` = '{value}'"
    conn.execute(query)
    conn.commit()
    conn.close()