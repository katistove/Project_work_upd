import sqlite3
import datetime

def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('records.db')
        return conn
    except sqlite3.Error as e:
        print(f"Ошибка подключения к БД: {e}")
    return conn

def init_db():
    conn = create_connection()
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    player_name TEXT NOT NULL,
                    wave INTEGER NOT NULL,
                    score INTEGER NOT NULL,
                    timestamp TEXT NOT NULL
                )
            ''')
            conn.commit()
        except sqlite3.Error as e:
            print(f"Ошибка создания таблицы: {e}")
        finally:
            conn.close()

def save_record(player_name, wave, score):
    conn = create_connection()
    if conn is not None:
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO records (player_name, wave, score, timestamp)
                VALUES (?, ?, ?, ?)
            ''', (player_name, wave, score, timestamp))
            conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Ошибка сохранения рекорда: {e}")
        finally:
            conn.close()
    return False

def get_top_records(limit=10):
    conn = create_connection()
    records = []
    if conn is not None:
        try:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT player_name, wave, score, timestamp
                FROM records
                ORDER BY score DESC, wave DESC
                LIMIT ?
            ''', (limit,))
            records = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Ошибка получения рекордов: {e}")
        finally:
            conn.close()
    return records

# Инициализация БД при импорте
init_db()