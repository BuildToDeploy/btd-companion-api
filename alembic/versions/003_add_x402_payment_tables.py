"""Add x402 payment tables

Revision ID: 003
Revises: 002
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '003'
down_revision = '002'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create x402_payments table
    op.create_table(
        'x402_payments',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=True),
        sa.Column('transaction_hash', sa.String(), nullable=False),
        sa.Column('network', sa.String(), nullable=False),
        sa.Column('amount_lamports', sa.Integer(), nullable=False),
        sa.Column('amount_usd', sa.Float(), nullable=True),
        sa.Column('payer_address', sa.String(), nullable=False),
        sa.Column('receiver_address', sa.String(), nullable=False),
        sa.Column('payment_status', sa.String(), server_default='pending'),
        sa.Column('tier', sa.String(), nullable=False),
        sa.Column('access_level', sa.Integer(), nullable=False),
        sa.Column('features_unlocked', sa.JSON(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('confirmed_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('transaction_hash')
    )
    op.create_index(op.f('ix_x402_payments_id'), 'x402_payments', ['id'], unique=False)
    op.create_index(op.f('ix_x402_payments_transaction_hash'), 'x402_payments', ['transaction_hash'], unique=True)
    op.create_index(op.f('ix_x402_payments_payer_address'), 'x402_payments', ['payer_address'], unique=False)

    # Create x402_subscriptions table
    op.create_table(
        'x402_subscriptions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('tier', sa.String(), nullable=False),
        sa.Column('recurring_payment_hash', sa.String(), nullable=True),
        sa.Column('network', sa.String(), nullable=False),
        sa.Column('monthly_price_lamports', sa.Integer(), nullable=False),
        sa.Column('monthly_price_usd', sa.Float(), nullable=True),
        sa.Column('status', sa.String(), server_default='active'),
        sa.Column('next_billing_date', sa.DateTime(), nullable=True),
        sa.Column('auto_renew', sa.Boolean(), server_default='true'),
        sa.Column('features', sa.JSON(), nullable=False),
        sa.Column('api_calls_limit', sa.Integer(), server_default='10000'),
        sa.Column('monthly_calls_used', sa.Integer(), server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_x402_subscriptions_id'), 'x402_subscriptions', ['id'], unique=False)

    # Create x402_access_logs table
    op.create_table(
        'x402_access_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('payment_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('endpoint', sa.String(), nullable=False),
        sa.Column('feature_accessed', sa.String(), nullable=False),
        sa.Column('request_type', sa.String(), nullable=False),
        sa.Column('tokens_used', sa.Integer(), nullable=True),
        sa.Column('execution_time_ms', sa.Float(), nullable=False),
        sa.Column('success', sa.Boolean(), server_default='true'),
        sa.Column('error_message', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['payment_id'], ['x402_payments.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_x402_access_logs_id'), 'x402_access_logs', ['id'], unique=False)


def downgrade() -> None:
    op.drop_table('x402_access_logs')
    op.drop_table('x402_subscriptions')
    op.drop_table('x402_payments')
