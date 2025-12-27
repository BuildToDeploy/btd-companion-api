"""Add simulation tables for transaction testing and what-if analysis

Revision ID: 001_add_simulation
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_add_simulation'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create simulation_results table
    op.create_table(
        'simulation_results',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('simulation_type', sa.String(50), nullable=False),
        sa.Column('calldata', sa.Text(), nullable=True),
        sa.Column('state_assumptions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('result_status', sa.String(50), nullable=False),
        sa.Column('gas_used', sa.Integer(), nullable=True),
        sa.Column('execution_trace', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('findings', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_insights', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['ai_requests.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_simulation_user', 'simulation_results', ['user_id'])
    op.create_index('idx_simulation_contract', 'simulation_results', ['contract_id'])
    op.create_index('idx_simulation_type', 'simulation_results', ['simulation_type'])
    
    # Create simulation_scenarios table
    op.create_table(
        'simulation_scenarios',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('simulation_id', sa.Integer(), nullable=True),
        sa.Column('scenario_name', sa.String(255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('initial_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('modified_state', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('expected_behavior', sa.Text(), nullable=True),
        sa.Column('actual_behavior', sa.Text(), nullable=True),
        sa.Column('outcome', sa.String(50), nullable=True),
        sa.Column('ai_analysis', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['simulation_id'], ['simulation_results.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_scenario_simulation', 'simulation_scenarios', ['simulation_id'])
    
    # Create failure_paths table
    op.create_table(
        'failure_paths',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('simulation_id', sa.Integer(), nullable=True),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('path_description', sa.Text(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('trigger_conditions', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('consequences', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('mitigation_steps', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('ai_reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['simulation_id'], ['simulation_results.id'], ),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_failure_simulation', 'failure_paths', ['simulation_id'])
    op.create_index('idx_failure_contract', 'failure_paths', ['contract_id'])
    op.create_index('idx_failure_severity', 'failure_paths', ['severity'])


def downgrade() -> None:
    op.drop_index('idx_failure_severity')
    op.drop_index('idx_failure_contract')
    op.drop_index('idx_failure_simulation')
    op.drop_table('failure_paths')
    
    op.drop_index('idx_scenario_simulation')
    op.drop_table('simulation_scenarios')
    
    op.drop_index('idx_simulation_type')
    op.drop_index('idx_simulation_contract')
    op.drop_index('idx_simulation_user')
    op.drop_table('simulation_results')
