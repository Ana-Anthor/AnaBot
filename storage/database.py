""" import sqlite3
import asyncio

class Database:
    def __init__(self):
        self.conn = sqlite3.connect('bot.db')
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS onboarding_roles (
                user_id INTEGER PRIMARY KEY,
                role_ids TEXT
            )
        ''')
        self.conn.commit()

    async def store_roles(self, user_id, role_ids):
        cursor = self.conn.cursor()
        role_ids_str = ','.join(map(str, role_ids))
        cursor.execute('''
            INSERT OR REPLACE INTO onboarding_roles (user_id, role_ids)
            VALUES (?, ?)
        ''', (user_id, role_ids_str))
        self.conn.commit()

    async def get_roles(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('SELECT role_ids FROM onboarding_roles WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        if result:
            return [int(rid) for rid in result[0].split(',') if rid]
        return []

    async def delete_roles(self, user_id):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM onboarding_roles WHERE user_id = ?', (user_id,))
        self.conn.commit()

    def close(self):
        self.conn.close() """