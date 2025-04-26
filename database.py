import os
import sqlitecloud
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.connect()
        self.create_tables()

    def connect(self):
        """Connect to the SQLiteCloud database"""
        try:
            # Construct the connection URL using environment variables
            connection_url = f"sqlitecloud://{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}?apikey={os.getenv('DB_PASSWORD')}"
            
            # Open the connection to SQLite Cloud
            self.conn = sqlitecloud.connect(connection_url)
            self.cursor = self.conn.cursor()
            print("Successfully connected to SQLiteCloud database")
        except Exception as e:
            print(f"Error connecting to SQLiteCloud database: {e}")
            raise

    def create_tables(self):
        """Create necessary tables if they don't exist"""
        try:
            # Economy table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS economy (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0
                )
            ''')

            # Mod roles table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mod_roles (
                    role_id INTEGER PRIMARY KEY
                )
            ''')

            # Ticket panel settings table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticket_panel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    color TEXT
                )
            ''')

            # Auto responder table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_responder (
                    trigger TEXT PRIMARY KEY,
                    response TEXT
                )
            ''')

            # Daily cooldown table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_cooldown (
                    user_id INTEGER PRIMARY KEY,
                    last_claim TEXT
                )
            ''')

            # Jobs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    role_id INTEGER PRIMARY KEY,
                    salary INTEGER
                )
            ''')

            self.conn.commit()
            print("Tables created successfully")
        except Exception as e:
            print(f"Error creating tables: {e}")
            self.conn.rollback()
            raise

    # Economy methods
    def get_balance(self, user_id):
        try:
            self.cursor.execute('SELECT balance FROM economy WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            return result[0] if result else 0
        except Exception as e:
            print(f"Error getting balance: {e}")
            return 0

    def set_balance(self, user_id, amount):
        try:
            self.cursor.execute('''
                INSERT INTO economy (user_id, balance)
                VALUES (?, ?)
                ON CONFLICT (user_id) DO UPDATE SET balance = ?
            ''', (user_id, amount, amount))
            self.conn.commit()
        except Exception as e:
            print(f"Error setting balance: {e}")
            self.conn.rollback()

    # Mod roles methods
    def get_mod_roles(self):
        try:
            self.cursor.execute('SELECT role_id FROM mod_roles')
            return [row[0] for row in self.cursor.fetchall()]
        except Exception as e:
            print(f"Error getting mod roles: {e}")
            return []

    def add_mod_role(self, role_id):
        try:
            self.cursor.execute('INSERT INTO mod_roles (role_id) VALUES (?) ON CONFLICT DO NOTHING', (role_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding mod role: {e}")
            self.conn.rollback()

    def remove_mod_role(self, role_id):
        try:
            self.cursor.execute('DELETE FROM mod_roles WHERE role_id = ?', (role_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing mod role: {e}")
            self.conn.rollback()

    # Ticket panel methods
    def get_ticket_panel(self):
        try:
            self.cursor.execute('SELECT title, description, color FROM ticket_panel ORDER BY id DESC LIMIT 1')
            result = self.cursor.fetchone()
            if result:
                return {
                    "title": result[0],
                    "description": result[1],
                    "color": result[2]
                }
            return {
                "title": "Support Ticket System",
                "description": "Click the button below to create a new support ticket. A moderator will assist you shortly.",
                "color": "blue"
            }
        except Exception as e:
            print(f"Error getting ticket panel: {e}")
            return {
                "title": "Support Ticket System",
                "description": "Click the button below to create a new support ticket. A moderator will assist you shortly.",
                "color": "blue"
            }

    def set_ticket_panel(self, title, description, color):
        try:
            self.cursor.execute('''
                INSERT INTO ticket_panel (title, description, color)
                VALUES (?, ?, ?)
            ''', (title, description, color))
            self.conn.commit()
        except Exception as e:
            print(f"Error setting ticket panel: {e}")
            self.conn.rollback()

    # Auto responder methods
    def get_auto_responses(self):
        try:
            self.cursor.execute('SELECT trigger, response FROM auto_responder')
            return {row[0]: row[1] for row in self.cursor.fetchall()}
        except Exception as e:
            print(f"Error getting auto responses: {e}")
            return {}

    def add_auto_response(self, trigger, response):
        try:
            self.cursor.execute('''
                INSERT INTO auto_responder (trigger, response)
                VALUES (?, ?)
                ON CONFLICT (trigger) DO UPDATE SET response = ?
            ''', (trigger, response, response))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding auto response: {e}")
            self.conn.rollback()

    def remove_auto_response(self, trigger):
        try:
            self.cursor.execute('DELETE FROM auto_responder WHERE trigger = ?', (trigger,))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing auto response: {e}")
            self.conn.rollback()

    # Daily cooldown methods
    def can_claim_daily(self, user_id):
        try:
            self.cursor.execute('SELECT last_claim FROM daily_cooldown WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            if not result:
                return True
            last_claim = result[0]
            return datetime.now() - last_claim >= timedelta(hours=24)
        except Exception as e:
            print(f"Error checking daily claim: {e}")
            return True

    def set_daily_claimed(self, user_id):
        try:
            self.cursor.execute('''
                INSERT INTO daily_cooldown (user_id, last_claim)
                VALUES (?, ?)
                ON CONFLICT (user_id) DO UPDATE SET last_claim = ?
            ''', (user_id, datetime.now(), datetime.now()))
            self.conn.commit()
        except Exception as e:
            print(f"Error setting daily claimed: {e}")
            self.conn.rollback()

    # Jobs methods
    def get_jobs(self):
        try:
            self.cursor.execute('SELECT role_id, salary FROM jobs')
            return {row[0]: row[1] for row in self.cursor.fetchall()}
        except Exception as e:
            print(f"Error getting jobs: {e}")
            return {}

    def add_job(self, role_id, salary):
        try:
            self.cursor.execute('''
                INSERT INTO jobs (role_id, salary)
                VALUES (?, ?)
                ON CONFLICT (role_id) DO UPDATE SET salary = ?
            ''', (role_id, salary, salary))
            self.conn.commit()
        except Exception as e:
            print(f"Error adding job: {e}")
            self.conn.rollback()

    def remove_job(self, role_id):
        try:
            self.cursor.execute('DELETE FROM jobs WHERE role_id = ?', (role_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing job: {e}")
            self.conn.rollback()

    def close(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close() 