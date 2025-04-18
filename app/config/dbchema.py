from app.utils import db

def create_users_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL UNIQUE,
            email TEXT NOT NULL UNIQUE,
            password TEXT NOT NULL,
            bio TEXT,
            gender TEXT
        )
    """)

def create_posts_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            content TEXT NOT NULL,
            caption TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (username) REFERENCES users(username)
        )
    """)

def create_comments_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS comments (
            id INTEGER PRIMARY KEY,
            post_id INTEGER,
            username TEXT,
            content TEXT,
            comment_date DATE,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """)

def create_likes_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS likes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            author TEXT,
            post_id INTEGER,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (author) REFERENCES users(username) ON DELETE CASCADE,
            FOREIGN KEY (post_id) REFERENCES posts(id) ON DELETE CASCADE
        )
    """)

def create_comment_trigger():
    db.execute("""
        CREATE TRIGGER IF NOT EXISTS set_comment_date
        BEFORE INSERT ON comments
        FOR EACH ROW
        BEGIN
            UPDATE comments SET comment_date = COALESCE(NEW.comment_date, CURRENT_DATE);
        END
    """)

def create_followers_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS followers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            follower_id INTEGER NOT NULL,
            followed_id INTEGER NOT NULL,
            CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (follower_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (followed_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE (follower_id, followed_id)
        )
    """)

def create_messages_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender_id INTEGER NOT NULL,
            receiver_id INTEGER NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id),
            FOREIGN KEY (receiver_id) REFERENCES users(id)
        )
    """)

def create_blocked_users_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS blocked_users (
            user_id INTEGER NOT NULL,
            blocked_id INTEGER NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id),
            FOREIGN KEY (blocked_id) REFERENCES users(id)
        )
    """)

def create_sessions_table():
    db.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id text PRIMARY KEY not null,
            user_id INTEGER,
            accesstoken TEXT,
            refreshtoken TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            revoked_at TEXT,
            ip TEXT,
            useragent TEXT,
            jti TEXT NOT NULL,
            refresh_jti TEXT NOT NULL,
            access_expire TEXT,
            refresh_expire TEXT
        )
    """)


def create_blacklistedtokens_table():
    db.execute("""create table if not exists blackListedTokens(
               jti text not null ,
               token_type text not null,
               expires_at TIMESTAMP NOT NULL  
               )""")



def create_indexes():
    db.execute("CREATE INDEX IF NOT EXISTS idx_followers_followed_id ON followers (followed_id)")
    db.execute("CREATE INDEX IF NOT EXISTS idx_posts_username_created_at ON posts (username, created_at)")

def initialize_all():
    create_users_table()
    create_posts_table()
    create_comments_table()
    create_likes_table()
    create_comment_trigger()
    create_followers_table()
    create_messages_table()
    create_blocked_users_table()
    create_sessions_table()
    create_indexes()
    create_blacklistedtokens_table()
