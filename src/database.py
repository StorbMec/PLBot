import sqlite3

class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.connection = None
        self.connect()
        self.create_table()

    def connect(self):
        if self.connection is None:
            self.connection = sqlite3.connect(self.database_url)
            print("Conectado ao banco de dados.")

    def close(self):
        if self.connection:
            self.connection.close()
            self.connection = None
            print("Conexão com o banco de dados fechada.")
            
    def create_table(self):
        cursor = self.connection.cursor()

        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS voice_activity (
                user_id INTEGER PRIMARY KEY,
                total_time INTEGER DEFAULT 0
            )
            """
        )

        self.connection.commit()
        
    def insert_voice_activity(self, user_id: int, total_time: int):
        cursor = self.connection.cursor()
        
        cursor.execute(
            """
            INSERT INTO voice_activity (user_id, total_time)
            VALUES (?, ?)
            ON CONFLICT(user_id) DO UPDATE SET
            total_time = total_time + excluded.total_time
            """, 
            (user_id, total_time)
        )
        
        self.connection.commit()
        
    def get_voice_activity(self, user_id: int):
        cursor = self.connection.cursor()
        
        cursor.execute(
            "SELECT total_time FROM voice_activity WHERE user_id = ?", (user_id,)
        )
        
        result = cursor.fetchone()
        
        return result[0] if result else 0