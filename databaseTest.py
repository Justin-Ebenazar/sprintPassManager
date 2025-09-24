import sqlite3

DB_NAME = 'password_manager.db'

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def list_tables():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    conn.close()
    print("📋 Tables:")
    for table in tables:
        print(f"- {table[0]}")

def show_table_data(table_name):
    conn = connect_db()
    cursor = conn.cursor()
    try:
        cursor.execute(f"SELECT * FROM {table_name};")
        rows = cursor.fetchall()
        print(f"📄 Data from '{table_name}':")
        for row in rows:
            print(row)
    except sqlite3.Error as e:
        print(f"⚠️ Error: {e}")
    finally:
        conn.close()

def insert_into_table(table_name, columns, values):
    conn = connect_db()
    cursor = conn.cursor()
    placeholders = ', '.join(['?'] * len(values))
    query = f"INSERT INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"✅ Inserted into '{table_name}'")
    except sqlite3.Error as e:
        print(f"⚠️ Insert error: {e}")
    finally:
        conn.close()

def update_table_value(table_name, set_clause, where_clause, values):
    conn = connect_db()
    cursor = conn.cursor()
    query = f"UPDATE {table_name} SET {set_clause} WHERE {where_clause}"
    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"🔄 Updated '{table_name}'")
    except sqlite3.Error as e:
        print(f"⚠️ Update error: {e}")
    finally:
        conn.close()

def delete_from_table(table_name, where_clause, values):
    conn = connect_db()
    cursor = conn.cursor()
    query = f"DELETE FROM {table_name} WHERE {where_clause}"
    try:
        cursor.execute(query, values)
        conn.commit()
        print(f"🗑️ Deleted from '{table_name}'")
    except sqlite3.Error as e:
        print(f"⚠️ Delete error: {e}")
    finally:
        conn.close()

def check_foreign_keys():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys;")
    status = cursor.fetchone()[0]
    conn.close()
    print(f"🔐 Foreign Keys Enabled: {'Yes' if status else 'No'}")

def get_schema(table_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"PRAGMA table_info({table_name});")
    schema = cursor.fetchall()
    conn.close()
    print(f"📐 Schema for '{table_name}':")
    for col in schema:
        print(col)

def count_rows(table_name):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute(f"SELECT COUNT(*) FROM {table_name};")
    count = cursor.fetchone()[0]
    conn.close()
    print(f"🔢 Row count in '{table_name}': {count}")

# list_tables()
show_table_data("credentials")
# insert_into_table("users", ["username", "password"], ["justin", "secure123"])
# update_table_value("users", "password = ?", "id = ?", ["newpass456", 1])
# delete_from_table("users", "id = ?", [1])
# check_foreign_keys()
# get_schema("credentials")
# count_rows("credentials")
