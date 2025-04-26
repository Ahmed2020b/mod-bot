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
            # Get credentials from environment variables
            host = os.getenv('SQLITECLOUD_HOST', 'ccnvo0ujhk.g4.sqlite.cloud')
            port = os.getenv('SQLITECLOUD_PORT', '8860')
            database = os.getenv('SQLITECLOUD_DB', 'chinook.sqlite')
            apikey = os.getenv('SQLITECLOUD_API_KEY', 'pk8J7e64Pt8yfjaYeR5S6L9Emj0CwZw8RYBno8fi7p4')
            
            print(f"Attempting to connect to SQLiteCloud with:")
            print(f"Host: {host}")
            print(f"Port: {port}")
            print(f"Database: {database}")
            
            # Construct connection URL
            connection_url = f"sqlitecloud://{host}:{port}/{database}?apikey={apikey}"
            
            # Open the connection to SQLite Cloud
            self.conn = sqlitecloud.connect(connection_url)
            self.cursor = self.conn.cursor()
            print("Successfully connected to SQLiteCloud database")
            
            # Test the connection with a simple query
            self.cursor.execute("SELECT 1")
            result = self.cursor.fetchone()
            if result and result[0] == 1:
                print("Database connection test successful")
            else:
                print("Warning: Database connection test failed")
                
        except Exception as e:
            print(f"Error connecting to SQLiteCloud database: {str(e)}")
            print("Please check your SQLiteCloud credentials and connection settings")
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

    def check_and_create_tables(self):
        """Check if all required tables exist and create them if they don't"""
        try:
            # Check and create economy table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS economy (
                    user_id INTEGER PRIMARY KEY,
                    balance INTEGER DEFAULT 0
                )
            ''')

            # Check and create mod_roles table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS mod_roles (
                    role_id INTEGER PRIMARY KEY
                )
            ''')

            # Check and create ticket_panel table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticket_panel (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT,
                    description TEXT,
                    color TEXT
                )
            ''')

            # Check and create auto_responder table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS auto_responder (
                    trigger TEXT PRIMARY KEY,
                    response TEXT
                )
            ''')

            # Check and create daily_cooldown table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS daily_cooldown (
                    user_id INTEGER PRIMARY KEY,
                    last_claim TEXT
                )
            ''')

            # Check and create jobs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS jobs (
                    role_id INTEGER PRIMARY KEY,
                    salary INTEGER
                )
            ''')

            self.conn.commit()
            print("All required tables verified and created if needed")
        except Exception as e:
            print(f"Error checking/creating tables: {str(e)}")
            self.conn.rollback()
            raise

    # Economy methods
    def get_balance(self, user_id):
        try:
            print(f"Attempting to get balance for user {user_id}")
            self.cursor.execute('SELECT balance FROM economy WHERE user_id = ?', (user_id,))
            result = self.cursor.fetchone()
            balance = result[0] if result else 0
            print(f"Retrieved balance for user {user_id}: {balance}")
            return balance
        except Exception as e:
            print(f"Error getting balance: {str(e)}")
            print("Current connection status:", "Connected" if self.conn else "Disconnected")
            return 0

    def set_balance(self, user_id, amount):
        try:
            print(f"Attempting to set balance for user {user_id} to {amount}")
            self.cursor.execute('''
                INSERT INTO economy (user_id, balance)
                VALUES (?, ?)
                ON CONFLICT (user_id) DO UPDATE SET balance = ?
            ''', (user_id, amount, amount))
            self.conn.commit()
            print(f"Successfully set balance for user {user_id}")
        except Exception as e:
            print(f"Error setting balance: {str(e)}")
            print("Current connection status:", "Connected" if self.conn else "Disconnected")
            self.conn.rollback()
            raise

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
    def get_ticket_panel(self, panel_id: int = None):
        try:
            # Ensure the table exists
            self.check_and_create_tables()
            
            if panel_id is not None:
                self.cursor.execute('SELECT id, title, description, color FROM ticket_panel WHERE id = ?', (panel_id,))
            else:
                self.cursor.execute('SELECT id, title, description, color FROM ticket_panel ORDER BY id DESC LIMIT 1')
            
            result = self.cursor.fetchone()
            if result:
                return {
                    "id": result[0],
                    "title": result[1],
                    "description": result[2],
                    "color": result[3]
                }
            return {
                "id": 0,
                "title": "Support Ticket System",
                "description": "Click the button below to create a new support ticket. A moderator will assist you shortly.",
                "color": "blue"
            }
        except Exception as e:
            print(f"Error getting ticket panel: {str(e)}")
            return {
                "id": 0,
                "title": "Support Ticket System",
                "description": "Click the button below to create a new support ticket. A moderator will assist you shortly.",
                "color": "blue"
            }

    def set_ticket_panel(self, title, description, color):
        try:
            # Ensure the table exists
            self.check_and_create_tables()
            
            self.cursor.execute('''
                INSERT INTO ticket_panel (title, description, color)
                VALUES (?, ?, ?)
            ''', (title, description, color))
            self.conn.commit()
            
            # Get the ID of the newly created panel
            self.cursor.execute('SELECT last_insert_rowid()')
            panel_id = self.cursor.fetchone()[0]
            return panel_id
        except Exception as e:
            print(f"Error setting ticket panel: {str(e)}")
            self.conn.rollback()
            return None

    def list_ticket_panels(self):
        try:
            # Ensure the table exists
            self.check_and_create_tables()
            
            self.cursor.execute('SELECT id, title FROM ticket_panel ORDER BY id DESC')
            return self.cursor.fetchall()
        except Exception as e:
            print(f"Error listing ticket panels: {str(e)}")
            return []

    # Auto responder methods
    def get_auto_responses(self):
        try:
            # Ensure the table exists
            self.check_and_create_tables()
            
            self.cursor.execute('SELECT trigger, response FROM auto_responder')
            return {row[0]: row[1] for row in self.cursor.fetchall()}
        except Exception as e:
            print(f"Error getting auto responses: {str(e)}")
            return {}

    def add_auto_response(self, trigger, response):
        try:
            # Ensure the table exists
            self.check_and_create_tables()
            
            self.cursor.execute('''
                INSERT INTO auto_responder (trigger, response)
                VALUES (?, ?)
                ON CONFLICT (trigger) DO UPDATE SET response = ?
            ''', (trigger, response, response))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error adding auto response: {str(e)}")
            self.conn.rollback()
            return False

    def remove_auto_response(self, trigger):
        try:
            # Ensure the table exists
            self.check_and_create_tables()
            
            self.cursor.execute('DELETE FROM auto_responder WHERE trigger = ?', (trigger,))
            self.conn.commit()
            return True
        except Exception as e:
            print(f"Error removing auto response: {str(e)}")
            self.conn.rollback()
            return False

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