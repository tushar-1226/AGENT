"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2026-03-03

"""
from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial tables"""
    
    # Users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('email', sa.String(255), unique=True, nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Sessions table
    op.create_table(
        'sessions',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text),
        sa.Column('path', sa.String(512)),
        sa.Column('user_id', sa.Integer, sa.ForeignKey('users.id')),
        sa.Column('created_at', sa.DateTime, default=datetime.utcnow),
        sa.Column('updated_at', sa.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    )
    
    # Create indexes
    op.create_index('idx_users_email', 'users', ['email'])
    op.create_index('idx_sessions_user_id', 'sessions', ['user_id'])
    op.create_index('idx_projects_user_id', 'projects', ['user_id'])


def downgrade() -> None:
    """Drop all tables"""
    op.drop_index('idx_projects_user_id')
    op.drop_index('idx_sessions_user_id')
    op.drop_index('idx_users_email')
    
    op.drop_table('projects')
    op.drop_table('sessions')
    op.drop_table('users')
