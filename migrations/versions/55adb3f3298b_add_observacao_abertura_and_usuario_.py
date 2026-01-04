"""Add observacao_abertura and usuario_abertura_id to caixa

Revision ID: 55adb3f3298b
Revises: 
Create Date: 2026-01-03 20:10:38.973834

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '55adb3f3298b'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add columns to caixa table
    op.add_column('caixa', sa.Column('observacao_abertura', sa.String(length=200), nullable=True))
    op.add_column('caixa', sa.Column('usuario_abertura_id', sa.Integer(), nullable=True))


def downgrade():
    # Remove columns from caixa table
    op.drop_column('caixa', 'usuario_abertura_id')
    op.drop_column('caixa', 'observacao_abertura')
