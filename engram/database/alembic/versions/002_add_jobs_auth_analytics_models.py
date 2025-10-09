"""add_jobs_auth_analytics_models

Revision ID: 002
Revises: 001_init_tables
Create Date: 2024-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001_init_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create jobs table
    op.create_table('jobs',
        sa.Column('id', sa.String(26), nullable=False),
        sa.Column('tenant_id', sa.String(26), nullable=False),
        sa.Column('user_id', sa.String(26), nullable=False),
        sa.Column('job_type', sa.Enum('ingest_url', 'ingest_file', 'ingest_chat', 'consolidation', 'forgetting', 'connector_sync', name='jobtype'), nullable=False),
        sa.Column('status', sa.Enum('pending', 'running', 'completed', 'failed', 'cancelled', name='jobstatus'), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('error', sa.Text(), nullable=True),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('result', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_jobs_tenant_user_status', 'jobs', ['tenant_id', 'user_id', 'status'], unique=False)
    op.create_index('idx_jobs_type_status', 'jobs', ['job_type', 'status'], unique=False)
    op.create_index('idx_jobs_created_at', 'jobs', ['created_at'], unique=False)

    # Create api_keys table
    op.create_table('api_keys',
        sa.Column('id', sa.String(26), nullable=False),
        sa.Column('tenant_id', sa.String(26), nullable=False),
        sa.Column('user_id', sa.String(26), nullable=False),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('key_hash', sa.String(255), nullable=False),
        sa.Column('scopes', sa.JSON(), nullable=False),
        sa.Column('active', sa.Boolean(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('expires_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key_hash')
    )
    op.create_index('idx_api_keys_tenant_user', 'api_keys', ['tenant_id', 'user_id'], unique=False)
    op.create_index('idx_api_keys_active', 'api_keys', ['active'], unique=False)
    op.create_index('idx_api_keys_last_used', 'api_keys', ['last_used_at'], unique=False)
    op.create_index(op.f('ix_api_keys_key_hash'), 'api_keys', ['key_hash'], unique=True)

    # Create request_logs table
    op.create_table('request_logs',
        sa.Column('id', sa.String(26), nullable=False),
        sa.Column('tenant_id', sa.String(26), nullable=False),
        sa.Column('user_id', sa.String(26), nullable=False),
        sa.Column('request_id', sa.String(26), nullable=False),
        sa.Column('route', sa.String(255), nullable=False),
        sa.Column('method', sa.String(10), nullable=False),
        sa.Column('status_code', sa.Integer(), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('cost_usd', sa.Float(), nullable=True),
        sa.Column('user_agent', sa.String(500), nullable=True),
        sa.Column('ip_address', sa.String(45), nullable=True),
        sa.Column('request_metadata', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_request_logs_tenant_created', 'request_logs', ['tenant_id', 'created_at'], unique=False)
    op.create_index('idx_request_logs_user_created', 'request_logs', ['user_id', 'created_at'], unique=False)
    op.create_index('idx_request_logs_route_created', 'request_logs', ['route', 'created_at'], unique=False)
    op.create_index('idx_request_logs_status_created', 'request_logs', ['status_code', 'created_at'], unique=False)

    # Create system_metrics table
    op.create_table('system_metrics',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('tenant_id', sa.String(26), nullable=False),
        sa.Column('metric_name', sa.String(255), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('metric_unit', sa.String(50), nullable=True),
        sa.Column('tags', sa.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_system_metrics_tenant_name', 'system_metrics', ['tenant_id', 'metric_name'], unique=False)
    op.create_index('idx_system_metrics_created_at', 'system_metrics', ['created_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('system_metrics')
    op.drop_table('request_logs')
    op.drop_table('api_keys')
    op.drop_table('jobs')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS jobstatus')
    op.execute('DROP TYPE IF EXISTS jobtype')
