"""Add intent verification tables

Revision ID: 002_add_intent_verification
Revises: 001_add_simulation_tables
Create Date: 2025-01-15 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_intent_verification'
down_revision = '001_add_simulation_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create intent_verifications table
    op.create_table(
        'intent_verifications',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        
        # Intent vs Behavior
        sa.Column('documented_intent', sa.Text(), nullable=True),
        sa.Column('actual_behavior', sa.Text(), nullable=True),
        sa.Column('intent_match_score', sa.Integer(), nullable=True),
        sa.Column('intent_findings', postgresql.JSON(), nullable=True),
        
        # Hidden Logic Detection
        sa.Column('hidden_logic_detected', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('dead_code_areas', postgresql.JSON(), nullable=True),
        sa.Column('delayed_execution_logic', postgresql.JSON(), nullable=True),
        sa.Column('conditional_activation', postgresql.JSON(), nullable=True),
        
        # Malicious Pattern Fingerprinting
        sa.Column('malicious_patterns_found', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('rug_pull_indicators', postgresql.JSON(), nullable=True),
        sa.Column('honeypot_indicators', postgresql.JSON(), nullable=True),
        sa.Column('malicious_risk_score', sa.Integer(), nullable=True),
        
        # Overall scores and recommendations
        sa.Column('overall_trust_score', sa.Integer(), nullable=True),
        sa.Column('ai_recommendation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['ai_requests.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_intent_verifications_contract_id', 'contract_id'),
        sa.Index('ix_intent_verifications_user_id', 'user_id'),
    )
    
    # Create hidden_logic_details table
    op.create_table(
        'hidden_logic_details',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('intent_verification_id', sa.Integer(), nullable=False),
        sa.Column('logic_type', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('location', sa.String(), nullable=True),
        sa.Column('line_numbers', postgresql.JSON(), nullable=True),
        sa.Column('risk_level', sa.String(), nullable=True),
        sa.Column('explanation', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        
        sa.ForeignKeyConstraint(['intent_verification_id'], ['intent_verifications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_hidden_logic_details_verification_id', 'intent_verification_id'),
    )
    
    # Create malicious_patterns table
    op.create_table(
        'malicious_patterns',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('intent_verification_id', sa.Integer(), nullable=False),
        sa.Column('pattern_type', sa.String(), nullable=False),
        sa.Column('pattern_name', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('indicators', postgresql.JSON(), nullable=True),
        sa.Column('affected_functions', postgresql.JSON(), nullable=True),
        sa.Column('severity', sa.String(), nullable=True),
        sa.Column('ai_reasoning', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        
        sa.ForeignKeyConstraint(['intent_verification_id'], ['intent_verifications.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_malicious_patterns_verification_id', 'intent_verification_id'),
    )


def downgrade() -> None:
    op.drop_table('malicious_patterns')
    op.drop_table('hidden_logic_details')
    op.drop_table('intent_verifications')
