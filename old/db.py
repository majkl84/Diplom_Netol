import sqlite3

class DB:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()

    def create_table(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                            (id INTEGER PRIMARY KEY AUTOINCREMENT,
                            vk_id INT NOT NULL,
                            photo_url TEXT NOT NULL);''')
        self.conn.commit()

    def user_exists(self, vk_id):
        self.cursor.execute("SELECT * FROM users WHERE vk_id=?", (vk_id,))
        return self.cursor.fetchone() is not None

    def add_user(self, vk_id, photo_url):
        self.cursor.execute("INSERT INTO users (vk_id, photo_url) VALUES (?, ?)", (vk_id, photo_url))
        self.conn.commit()