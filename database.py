import os
import sqlitecloud
from datetime import datetime, timedelta
from dotenv import load_dotenv
import time

load_dotenv()

class Database:
    def __init__(self):
        self.conn = None
        self.cursor = None
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.cache = {
            'auto_responses': {},
            'mod_roles': [],
            'jobs': {},
            'cache_time': {}
        }
        self.cache_duration = 5  # Reduced cache duration to 5 seconds
        self.connect()
        self.create_tables()

    def connect(self):
        """Connect to the SQLiteCloud database with retry logic"""
        retries = 0
        while retries < self.max_retries:
            try:
                # Get credentials from environment variables
                host = os.getenv('SQLITECLOUD_HOST', 'ccnvo0ujhk.g4.sqlite.cloud')
                port = os.getenv('SQLITECLOUD_PORT', '8860')
                database = os.getenv('SQLITECLOUD_DB', 'chinook.sqlite')
                apikey = os.getenv('SQLITECLOUD_API_KEY', 'pk8J7e64Pt8yfjaYeR5S6L9Emj0CwZw8RYBno8fi7p4')
                
                print(f"Attempting to connect to SQLiteCloud (attempt {retries + 1}/{self.max_retries})")
                
                # Construct connection URL
                connection_url = f"sqlitecloud://{host}:{port}/{database}?apikey={apikey}"
                
                # Close existing connection if it exists
                if self.conn:
                    try:
                        self.conn.close()
                    except:
                        pass
                
                # Open the connection to SQLite Cloud
                self.conn = sqlitecloud.connect(connection_url)
                self.cursor = self.conn.cursor()
                
                # Test the connection
                self.cursor.execute("SELECT 1")
                result = self.cursor.fetchone()
                if result and result[0] == 1:
                    print("Successfully connected to SQLiteCloud database")
                    return True
                else:
                    raise Exception("Connection test failed")
                    
            except Exception as e:
                print(f"Error connecting to SQLiteCloud database (attempt {retries + 1}): {str(e)}")
                retries += 1
                if retries < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max retries reached. Could not connect to database.")
                    raise

    def ensure_connection(self):
        """Ensure database connection is active, reconnect if necessary"""
        try:
            # Test the connection
            self.cursor.execute("SELECT 1")
            self.cursor.fetchone()
        except:
            print("Connection lost, attempting to reconnect...")
            self.connect()

    def execute_with_retry(self, query, params=None):
        """Execute a query with retry logic"""
        retries = 0
        while retries < self.max_retries:
            try:
                self.ensure_connection()
                if params:
                    self.cursor.execute(query, params)
                else:
                    self.cursor.execute(query)
                return True
            except Exception as e:
                print(f"Error executing query (attempt {retries + 1}): {str(e)}")
                retries += 1
                if retries < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    self.connect()
                else:
                    print("Max retries reached. Query failed.")
                    raise

    def commit_with_retry(self):
        """Commit changes with retry logic"""
        retries = 0
        while retries < self.max_retries:
            try:
                self.ensure_connection()
                self.conn.commit()
                return True
            except Exception as e:
                print(f"Error committing changes (attempt {retries + 1}): {str(e)}")
                retries += 1
                if retries < self.max_retries:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                    self.connect()
                else:
                    print("Max retries reached. Commit failed.")
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

            # Tickets table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    channel_id INTEGER,
                    created_at TEXT,
                    closed_at TEXT
                )
            ''')

            # Ticket logs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticket_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER,
                    action TEXT,
                    timestamp TEXT,
                    details TEXT
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

            # Check and create tickets table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS tickets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    channel_id INTEGER,
                    created_at TEXT,
                    closed_at TEXT
                )
            ''')

            # Check and create ticket_logs table
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS ticket_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticket_id INTEGER,
                    action TEXT,
                    timestamp TEXT,
                    details TEXT
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
            self.execute_with_retry('''
                INSERT INTO economy (user_id, balance)
                VALUES (?, ?)
                ON CONFLICT (user_id) DO UPDATE SET balance = ?
            ''', (user_id, amount, amount))
            self.commit_with_retry()
            print(f"Successfully set balance for user {user_id}")
        except Exception as e:
            print(f"Error setting balance: {str(e)}")
            print("Current connection status:", "Connected" if self.conn else "Disconnected")
            raise

    # Mod roles methods
    def get_mod_roles(self):
        """Get mod roles with caching"""
        if self.is_cache_valid('mod_roles'):
            return self.cache['mod_roles']
        
        try:
            self.ensure_connection()
            self.cursor.execute('SELECT role_id FROM mod_roles')
            roles = [row[0] for row in self.cursor.fetchall()]
            self.update_cache('mod_roles', roles)
            return roles
        except Exception as e:
            print(f"Error getting mod roles: {e}")
            return self.cache['mod_roles']  # Return cached data if available

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
        """Get auto responses with caching"""
        try:
            print("Fetching auto responses from database...")
            self.ensure_connection()
            self.cursor.execute('SELECT trigger, response FROM auto_responder')
            responses = {row[0]: row[1] for row in self.cursor.fetchall()}
            print(f"Found {len(responses)} auto responses: {responses}")
            self.update_cache('auto_responses', responses)
            return responses
        except Exception as e:
            print(f"Error getting auto responses: {str(e)}")
            return {}  # Return empty dict instead of cached data on error

    def add_auto_response(self, trigger, response):
        """Add auto response and update cache"""
        try:
            print(f"Adding auto response: trigger='{trigger}', response='{response}'")
            self.ensure_connection()
            self.execute_with_retry('''
                INSERT INTO auto_responder (trigger, response)
                VALUES (?, ?)
                ON CONFLICT (trigger) DO UPDATE SET response = ?
            ''', (trigger, response, response))
            self.commit_with_retry()
            
            # Force cache refresh
            self.cache['auto_responses'] = {}
            self.cache['cache_time']['auto_responses'] = datetime.now()
            print("Auto response added successfully")
            return True
        except Exception as e:
            print(f"Error adding auto response: {str(e)}")
            return False

    def remove_auto_response(self, trigger):
        """Remove auto response and update cache"""
        try:
            self.ensure_connection()
            self.execute_with_retry('DELETE FROM auto_responder WHERE trigger = ?', (trigger,))
            self.commit_with_retry()
            
            # Force cache refresh
            self.cache['auto_responses'] = {}
            self.cache['cache_time']['auto_responses'] = datetime.now()
            return True
        except Exception as e:
            print(f"Error removing auto response: {str(e)}")
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
        """Get jobs with caching"""
        if self.is_cache_valid('jobs'):
            return self.cache['jobs']
        
        try:
            self.ensure_connection()
            self.cursor.execute('SELECT role_id, salary FROM jobs')
            jobs = {row[0]: row[1] for row in self.cursor.fetchall()}
            self.update_cache('jobs', jobs)
            return jobs
        except Exception as e:
            print(f"Error getting jobs: {e}")
            return self.cache['jobs']  # Return cached data if available

    def add_job(self, role_id, salary):
        try:
            self.execute_with_retry('''
                INSERT INTO jobs (role_id, salary)
                VALUES (?, ?)
                ON CONFLICT (role_id) DO UPDATE SET salary = ?
            ''', (role_id, salary, salary))
            self.commit_with_retry()
        except Exception as e:
            print(f"Error adding job: {e}")
            raise

    def remove_job(self, role_id):
        try:
            self.cursor.execute('DELETE FROM jobs WHERE role_id = ?', (role_id,))
            self.conn.commit()
        except Exception as e:
            print(f"Error removing job: {e}")
            self.conn.rollback()

    def create_ticket(self, user_id, channel_id):
        try:
            self.check_and_create_tables()
            now = datetime.now().isoformat()
            self.execute_with_retry('''
                INSERT INTO tickets (user_id, channel_id, created_at, closed_at)
                VALUES (?, ?, ?, NULL)
            ''', (user_id, channel_id, now))
            self.commit_with_retry()
            ticket_id = self.cursor.lastrowid
            return ticket_id
        except Exception as e:
            print(f"Error creating ticket: {str(e)}")
            raise

    def close_ticket(self, channel_id):
        try:
            self.check_and_create_tables()
            now = datetime.now().isoformat()
            self.cursor.execute('''
                UPDATE tickets SET closed_at = ? WHERE channel_id = ?
            ''', (now, channel_id))
            self.conn.commit()
        except Exception as e:
            print(f"Error closing ticket: {str(e)}")
            self.conn.rollback()

    def log_ticket_action(self, ticket_id, action, details=None):
        try:
            self.check_and_create_tables()
            now = datetime.now().isoformat()
            self.cursor.execute('''
                INSERT INTO ticket_logs (ticket_id, action, timestamp, details)
                VALUES (?, ?, ?, ?)
            ''', (ticket_id, action, now, details))
            self.conn.commit()
        except Exception as e:
            print(f"Error logging ticket action: {str(e)}")
            self.conn.rollback()

    def get_ticket_by_channel(self, channel_id):
        try:
            self.check_and_create_tables()
            self.cursor.execute('SELECT id, user_id, created_at, closed_at FROM tickets WHERE channel_id = ?', (channel_id,))
            return self.cursor.fetchone()
        except Exception as e:
            print(f"Error getting ticket by channel: {str(e)}")
            return None

    def is_cache_valid(self, cache_key):
        """Check if the cache is still valid"""
        if cache_key not in self.cache['cache_time']:
            return False
        return (datetime.now() - self.cache['cache_time'][cache_key]).total_seconds() < self.cache_duration

    def update_cache(self, cache_key, data):
        """Update the cache with new data"""
        self.cache[cache_key] = data
        self.cache['cache_time'][cache_key] = datetime.now()

    def close(self):
        """Close the database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close() 