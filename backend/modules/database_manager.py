"""
Database Query Builder
Natural language to SQL with multiple database support
"""
from typing import Dict, List, Optional, Any
import json

try:
    from sqlalchemy import create_engine, inspect, text
    from sqlalchemy.engine import Engine
    SQLALCHEMY_AVAILABLE = True
except ImportError:
    SQLALCHEMY_AVAILABLE = False
    print("SQLAlchemy not installed. Run: pip install sqlalchemy psycopg2-binary pymysql")

class DatabaseManager:
    def __init__(self):
        self.engines: Dict[str, Engine] = {}
        self.current_db: Optional[str] = None
    
    def connect(self, connection_string: str, db_name: str = 'default') -> bool:
        """Connect to a database"""
        if not SQLALCHEMY_AVAILABLE:
            return False
        
        try:
            engine = create_engine(connection_string)
            # Test connection
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            
            self.engines[db_name] = engine
            self.current_db = db_name
            return True
        except Exception as e:
            print(f"Database connection error: {e}")
            return False
    
    def get_schema(self, db_name: str = None) -> Dict[str, Any]:
        """Get database schema"""
        db_name = db_name or self.current_db
        if not db_name or db_name not in self.engines:
            return {'error': 'No database connected'}
        
        try:
            engine = self.engines[db_name]
            inspector = inspect(engine)
            
            schema = {
                'tables': [],
                'database': db_name
            }
            
            for table_name in inspector.get_table_names():
                columns = []
                for column in inspector.get_columns(table_name):
                    columns.append({
                        'name': column['name'],
                        'type': str(column['type']),
                        'nullable': column['nullable'],
                        'default': str(column['default']) if column['default'] else None
                    })
                
                # Get primary keys
                pk = inspector.get_pk_constraint(table_name)
                primary_keys = pk['constrained_columns'] if pk else []
                
                # Get foreign keys
                foreign_keys = []
                for fk in inspector.get_foreign_keys(table_name):
                    foreign_keys.append({
                        'column': fk['constrained_columns'][0],
                        'references': f"{fk['referred_table']}.{fk['referred_columns'][0]}"
                    })
                
                schema['tables'].append({
                    'name': table_name,
                    'columns': columns,
                    'primary_keys': primary_keys,
                    'foreign_keys': foreign_keys
                })
            
            return schema
        except Exception as e:
            return {'error': str(e)}
    
    def execute_query(self, query: str, db_name: str = None) -> Dict[str, Any]:
        """Execute SQL query"""
        db_name = db_name or self.current_db
        if not db_name or db_name not in self.engines:
            return {'error': 'No database connected'}
        
        try:
            engine = self.engines[db_name]
            with engine.connect() as conn:
                result = conn.execute(text(query))
                
                # Check if it's a SELECT query
                if query.strip().upper().startswith('SELECT'):
                    rows = result.fetchall()
                    columns = list(result.keys())
                    
                    data = []
                    for row in rows:
                        data.append(dict(zip(columns, row)))
                    
                    return {
                        'success': True,
                        'data': data,
                        'columns': columns,
                        'row_count': len(data)
                    }
                else:
                    # For INSERT, UPDATE, DELETE
                    conn.commit()
                    return {
                        'success': True,
                        'message': 'Query executed successfully',
                        'rows_affected': result.rowcount
                    }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def natural_language_to_sql(self, nl_query: str, schema: Dict = None) -> str:
        """Convert natural language to SQL (simplified version)"""
        # In production, use Gemini API for better conversion
        # This is a simple heuristic-based approach
        
        nl_lower = nl_query.lower()
        
        # Get schema if not provided
        if not schema:
            schema = self.get_schema()
        
        # Simple patterns
        if 'show' in nl_lower or 'get' in nl_lower or 'list' in nl_lower:
            # Find table name
            for table in schema.get('tables', []):
                if table['name'].lower() in nl_lower:
                    if 'where' in nl_lower or 'created' in nl_lower:
                        return f"SELECT * FROM {table['name']} LIMIT 100;"
                    return f"SELECT * FROM {table['name']} LIMIT 10;"
            
            # Default
            if schema.get('tables'):
                return f"SELECT * FROM {schema['tables'][0]['name']} LIMIT 10;"
        
        elif 'count' in nl_lower:
            for table in schema.get('tables', []):
                if table['name'].lower() in nl_lower:
                    return f"SELECT COUNT(*) as count FROM {table['name']};"
        
        elif 'insert' in nl_lower or 'add' in nl_lower:
            return "-- Please provide specific values for INSERT query"
        
        return "-- Could not parse query. Please provide SQL directly."
    
    def get_table_preview(self, table_name: str, limit: int = 10, db_name: str = None) -> Dict:
        """Get preview of table data"""
        query = f"SELECT * FROM {table_name} LIMIT {limit};"
        return self.execute_query(query, db_name)
    
    def list_connections(self) -> List[str]:
        """List all database connections"""
        return list(self.engines.keys())
    
    def disconnect(self, db_name: str) -> bool:
        """Disconnect from database"""
        if db_name in self.engines:
            self.engines[db_name].dispose()
            del self.engines[db_name]
            if self.current_db == db_name:
                self.current_db = list(self.engines.keys())[0] if self.engines else None
            return True
        return False
