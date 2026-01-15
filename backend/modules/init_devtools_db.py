"""
Initialize dev_tools database for advanced features
"""
import sqlite3
import os

# Get database path
db_path = os.path.join(os.path.dirname(__file__), '..', 'dev_tools.db')

# Create/connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create snippets table
cursor.execute('''
CREATE TABLE IF NOT EXISTS snippets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT,
    code TEXT NOT NULL,
    language TEXT,
    tags TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
''')

# Create index on tags for faster searching
cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_tags ON snippets(tags)')
cursor.execute('CREATE INDEX IF NOT EXISTS idx_snippets_language ON snippets(language)')

conn.commit()
conn.close()

print(f" Database initialized successfully at {db_path}")
