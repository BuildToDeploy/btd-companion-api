"""Add multi-chain support with Move, CosmWasm, TEAL, and Circuit analysis

Revision ID: 004_multi_chain
Revises: 003_add_x402_payment_tables
Create Date: 2026-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = '004_multi_chain'
down_revision = '003_add_x402_payment_tables'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create blockchain and language enums
    blockchain_enum = postgresql.ENUM(
        'ethereum', 'polygon', 'arbitrum', 'base', 'xlayer',
        'solana', 'cosmos', 'algorand', 'aptos', 'sui', 'peaq', 'sei',
        name='blockchain', create_type=False
    )
    blockchain_enum.create(op.get_bind(), checkfirst=True)
    
    language_enum = postgresql.ENUM(
        'solidity', 'vyper', 'rust', 'cosmwasm', 'teal', 'pyteal', 'move',
        name='smartcontractlanguage', create_type=False
    )
    language_enum.create(op.get_bind(), checkfirst=True)
    
    # Create multi_chain_contracts table
    op.create_table(
        'multi_chain_contracts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('contract_id', sa.Integer(), nullable=False),
        sa.Column('blockchain', sa.Enum('ethereum', 'polygon', 'arbitrum', 'base', 'xlayer',
                                        'solana', 'cosmos', 'algorand', 'aptos', 'sui', 'peaq', 'sei',
                                        name='blockchain'), nullable=False),
        sa.Column('language', sa.Enum('solidity', 'vyper', 'rust', 'cosmwasm', 'teal', 'pyteal', 'move',
                                      name='smartcontractlanguage'), nullable=False),
        sa.Column('contract_address', sa.String(), nullable=True),
        sa.Column('abi_json', sa.JSON(), nullable=True),
        sa.Column('idl_json', sa.JSON(), nullable=True),
        sa.Column('move_module_name', sa.String(), nullable=True),
        sa.Column('bytecode', sa.Text(), nullable=True),
        sa.Column('deployment_tx', sa.String(), nullable=True),
        sa.Column('compiler_version', sa.String(), nullable=True),
        sa.Column('optimization_enabled', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['contract_id'], ['contracts.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.Index('ix_multi_chain_contracts_contract_id', 'contract_id'),
        sa.Index('ix_multi_chain_contracts_blockchain', 'blockchain'),
        sa.Index('ix_multi_chain_contracts_address', 'contract_address'),
    )
    
    # Create move_language_analysis table
    op.create_table(
        'move_language_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('multi_chain_contract_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('modules_found', sa.JSON(), nullable=True),
        sa.Column('abilities_used', sa.JSON(), nullable=True),
        sa.Column('resource_patterns', sa.JSON(), nullable=True),
        sa.Column('type_parameters', sa.JSON(), nullable=True),
        sa.Column('safety_issues', sa.JSON(), nullable=True),
        sa.Column('reentrancy_risks', sa.JSON(), nullable=True),
        sa.Column('resource_leaks_found', sa.Boolean(), default=False),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('ai_insights', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['multi_chain_contract_id'], ['multi_chain_contracts.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['ai_requests.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create cosmwasm_analysis table
    op.create_table(
        'cosmwasm_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('multi_chain_contract_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('entry_points', sa.JSON(), nullable=True),
        sa.Column('message_types', sa.JSON(), nullable=True),
        sa.Column('state_structure', sa.JSON(), nullable=True),
        sa.Column('cw_standards_used', sa.JSON(), nullable=True),
        sa.Column('ibc_integration', sa.Boolean(), default=False),
        sa.Column('cross_chain_risks', sa.JSON(), nullable=True),
        sa.Column('state_consistency_issues', sa.JSON(), nullable=True),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('ai_insights', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['multi_chain_contract_id'], ['multi_chain_contracts.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['ai_requests.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create teal_analysis table
    op.create_table(
        'teal_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('multi_chain_contract_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('is_stateful', sa.Boolean(), nullable=True),
        sa.Column('is_stateless', sa.Boolean(), nullable=True),
        sa.Column('global_state_keys', sa.JSON(), nullable=True),
        sa.Column('local_state_keys', sa.JSON(), nullable=True),
        sa.Column('abi_methods', sa.JSON(), nullable=True),
        sa.Column('stack_depth_issues', sa.JSON(), nullable=True),
        sa.Column('transaction_group_risks', sa.JSON(), nullable=True),
        sa.Column('inner_transaction_usage', sa.JSON(), nullable=True),
        sa.Column('atomic_transaction_safety', sa.JSON(), nullable=True),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('ai_insights', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['multi_chain_contract_id'], ['multi_chain_contracts.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['ai_requests.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    
    # Create circuit_analysis table
    op.create_table(
        'circuit_analysis',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('multi_chain_contract_id', sa.Integer(), nullable=False),
        sa.Column('request_id', sa.Integer(), nullable=True),
        sa.Column('circuit_framework', sa.String(), nullable=True),
        sa.Column('number_of_constraints', sa.Integer(), nullable=True),
        sa.Column('number_of_signals', sa.Integer(), nullable=True),
        sa.Column('number_of_public_inputs', sa.Integer(), nullable=True),
        sa.Column('soundness_issues', sa.JSON(), nullable=True),
        sa.Column('completeness_verified', sa.Boolean(), nullable=True),
        sa.Column('witness_generation_safety', sa.JSON(), nullable=True),
        sa.Column('trusted_setup_requirements', sa.JSON(), nullable=True),
        sa.Column('proof_system_type', sa.String(), nullable=True),
        sa.Column('verification_key_analysis', sa.JSON(), nullable=True),
        sa.Column('findings', sa.JSON(), nullable=True),
        sa.Column('risk_score', sa.Integer(), nullable=True),
        sa.Column('ai_insights', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(['multi_chain_contract_id'], ['multi_chain_contracts.id'], ),
        sa.ForeignKeyConstraint(['request_id'], ['ai_requests.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade() -> None:
    op.drop_table('circuit_analysis')
    op.drop_table('teal_analysis')
    op.drop_table('cosmwasm_analysis')
    op.drop_table('move_language_analysis')
    op.drop_table('multi_chain_contracts')
