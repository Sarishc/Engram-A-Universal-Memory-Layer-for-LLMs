"""Initial tables

Revision ID: 001_init_tables
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_init_tables'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create tenants table
    op.create_table('tenants',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_tenants_id'), 'tenants', ['id'], unique=False)

    # Create memories table
    op.create_table('memories',
    sa.Column('id', sa.String(length=26), nullable=False),
    sa.Column('tenant_id', sa.String(length=26), nullable=False),
    sa.Column('user_id', sa.String(length=26), nullable=False),
    sa.Column('text', sa.Text(), nullable=False),
    sa.Column('metadata', postgresql.JSON(astext_type=sa.Text()), nullable=False),
    sa.Column('importance', sa.Float(), nullable=False),
    sa.Column('decay_weight', sa.Float(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('last_accessed_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_memories_active_created', 'memories', ['active', 'created_at'], unique=False)
    op.create_index('idx_memories_importance', 'memories', ['importance'], unique=False)
    op.create_index('idx_memories_last_accessed', 'memories', ['last_accessed_at'], unique=False)
    op.create_index('idx_memories_tenant_user', 'memories', ['tenant_id', 'user_id'], unique=False)
    op.create_index(op.f('ix_memories_tenant_id'), 'memories', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_memories_user_id'), 'memories', ['user_id'], unique=False)

    # Create user_memory_stats table
    op.create_table('user_memory_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tenant_id', sa.String(length=26), nullable=False),
    sa.Column('user_id', sa.String(length=26), nullable=False),
    sa.Column('total_memories', sa.Integer(), nullable=False),
    sa.Column('active_memories', sa.Integer(), nullable=False),
    sa.Column('avg_importance', sa.Float(), nullable=False),
    sa.Column('last_seen_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_user_stats_tenant_user', 'user_memory_stats', ['tenant_id', 'user_id'], unique=True)
    op.create_index(op.f('ix_user_memory_stats_tenant_id'), 'user_memory_stats', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_user_memory_stats_user_id'), 'user_memory_stats', ['user_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_user_memory_stats_user_id'), table_name='user_memory_stats')
    op.drop_index(op.f('ix_user_memory_stats_tenant_id'), table_name='user_memory_stats')
    op.drop_index('idx_user_stats_tenant_user', table_name='user_memory_stats')
    op.drop_table('user_memory_stats')
    
    op.drop_index(op.f('ix_memories_user_id'), table_name='memories')
    op.drop_index(op.f('ix_memories_tenant_id'), table_name='memories')
    op.drop_index('idx_memories_tenant_user', table_name='memories')
    op.drop_index('idx_memories_last_accessed', table_name='memories')
    op.drop_index('idx_memories_importance', table_name='memories')
    op.drop_index('idx_memories_active_created', table_name='memories')
    op.drop_table('memories')
    
    op.drop_index(op.f('ix_tenants_id'), table_name='tenants')
    op.drop_table('tenants')
