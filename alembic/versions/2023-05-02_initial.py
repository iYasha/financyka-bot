"""initial

Revision ID: 54f01b19fa0d
Revises: 
Create Date: 2023-05-02 20:10:27.055169

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '54f01b19fa0d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        'currencies',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('ccy', sa.String(), nullable=False),
        sa.Column('base_ccy', sa.String(), nullable=False),
        sa.Column('buy', sa.Float(), nullable=False),
        sa.Column('sale', sa.Float(), nullable=False),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_currencies')),
    )
    op.create_index(op.f('ix_currencies_id'), 'currencies', ['id'], unique=False)
    op.create_table(
        'users',
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('chat_id', sa.Integer(), nullable=False),
        sa.Column('first_name', sa.String(), nullable=True),
        sa.Column('last_name', sa.String(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.PrimaryKeyConstraint('chat_id', name=op.f('pk_users')),
    )
    op.create_table(
        'operations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('received_amount', sa.Integer(), nullable=True),
        sa.Column('currency', sa.String(), nullable=False),
        sa.Column('operation_type', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('repeat_type', sa.String(), nullable=True),
        sa.Column('repeat_days', sa.JSON(), nullable=True),
        sa.Column('is_approved', sa.Boolean(), nullable=False),
        sa.Column('is_regular_operation', sa.Boolean(), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ['creator_id'],
            ['users.chat_id'],
            name=op.f('fk_operations_creator_id_users'),
            ondelete='CASCADE',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_operations')),
    )
    op.create_index(op.f('ix_operations_id'), 'operations', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_operations_id'), table_name='operations')
    op.drop_table('operations')
    op.drop_table('users')
    op.drop_index(op.f('ix_currencies_id'), table_name='currencies')
    op.drop_table('currencies')
    # ### end Alembic commands ###
