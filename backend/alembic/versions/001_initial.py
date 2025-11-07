"""Initial migration

Revision ID: 001_initial
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Users
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Settings
    op.create_table(
        'settings',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(), nullable=False),
        sa.Column('value', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_settings_id'), 'settings', ['id'], unique=False)
    op.create_index(op.f('ix_settings_key'), 'settings', ['key'], unique=True)
    
    # Stores
    op.create_table(
        'stores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('url', sa.String(), nullable=False),
        sa.Column('selectors', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_stores_id'), 'stores', ['id'], unique=False)
    op.create_index(op.f('ix_stores_name'), 'stores', ['name'], unique=False)
    
    # Products
    op.create_table(
        'products',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('asin', sa.String(), nullable=False),
        sa.Column('title', sa.String(), nullable=True),
        sa.Column('brand', sa.String(), nullable=True),
        sa.Column('category', sa.String(), nullable=True),
        sa.Column('image_url', sa.String(), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_products_id'), 'products', ['id'], unique=False)
    op.create_index(op.f('ix_products_asin'), 'products', ['asin'], unique=True)
    
    # Offers Amazon
    op.create_table(
        'offers_amz',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('marketplace', sa.String(), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('shipping_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('fba_fee', sa.Numeric(10, 2), nullable=True),
        sa.Column('referral_fee', sa.Numeric(10, 2), nullable=True),
        sa.Column('sellers_count', sa.Integer(), nullable=True),
        sa.Column('buybox_stable', sa.Boolean(), nullable=True),
        sa.Column('bsr', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offers_amz_id'), 'offers_amz', ['id'], unique=False)
    op.create_index(op.f('ix_offers_amz_product_id'), 'offers_amz', ['product_id'], unique=False)
    op.create_index(op.f('ix_offers_amz_marketplace'), 'offers_amz', ['marketplace'], unique=False)
    
    # Offers Retail
    op.create_table(
        'offers_retail',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('store_id', sa.Integer(), nullable=False),
        sa.Column('price', sa.Numeric(10, 2), nullable=False),
        sa.Column('shipping_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('availability', sa.Boolean(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['store_id'], ['stores.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_offers_retail_id'), 'offers_retail', ['id'], unique=False)
    op.create_index(op.f('ix_offers_retail_product_id'), 'offers_retail', ['product_id'], unique=False)
    op.create_index(op.f('ix_offers_retail_store_id'), 'offers_retail', ['store_id'], unique=False)
    
    # Scores
    op.create_table(
        'scores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('marketplace', sa.String(), nullable=False),
        sa.Column('landed_cost', sa.Numeric(10, 2), nullable=True),
        sa.Column('margin_eur', sa.Numeric(10, 2), nullable=True),
        sa.Column('roi_percent', sa.Numeric(5, 2), nullable=True),
        sa.Column('best_retail_offer_id', sa.Integer(), nullable=True),
        sa.Column('best_amazon_offer_id', sa.Integer(), nullable=True),
        sa.Column('calculated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.ForeignKeyConstraint(['best_retail_offer_id'], ['offers_retail.id'], ),
        sa.ForeignKeyConstraint(['best_amazon_offer_id'], ['offers_amz.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_scores_id'), 'scores', ['id'], unique=False)
    op.create_index(op.f('ix_scores_product_id'), 'scores', ['product_id'], unique=False)
    op.create_index(op.f('ix_scores_marketplace'), 'scores', ['marketplace'], unique=False)
    
    # Lists
    op.create_table(
        'lists',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_lists_id'), 'lists', ['id'], unique=False)
    
    # List Items
    op.create_table(
        'list_items',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('list_id', sa.Integer(), nullable=False),
        sa.Column('product_id', sa.Integer(), nullable=False),
        sa.Column('notes', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['list_id'], ['lists.id'], ),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_list_items_id'), 'list_items', ['id'], unique=False)
    op.create_index(op.f('ix_list_items_list_id'), 'list_items', ['list_id'], unique=False)
    op.create_index(op.f('ix_list_items_product_id'), 'list_items', ['product_id'], unique=False)
    
    # Alerts
    op.create_table(
        'alerts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String(), nullable=True),
        sa.Column('filters', postgresql.JSON(astext_type=sa.Text()), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=True),
        sa.Column('last_run_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_alerts_id'), 'alerts', ['id'], unique=False)
    
    # Jobs
    op.create_table(
        'jobs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('job_type', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('PENDING', 'RUNNING', 'COMPLETED', 'FAILED', name='jobstatus'), nullable=True),
        sa.Column('parameters', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('result', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error', sa.String(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('completed_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_jobs_id'), 'jobs', ['id'], unique=False)
    op.create_index(op.f('ix_jobs_job_type'), 'jobs', ['job_type'], unique=False)
    op.create_index(op.f('ix_jobs_status'), 'jobs', ['status'], unique=False)


def downgrade() -> None:
    op.drop_index(op.f('ix_jobs_status'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_job_type'), table_name='jobs')
    op.drop_index(op.f('ix_jobs_id'), table_name='jobs')
    op.drop_table('jobs')
    op.drop_index(op.f('ix_alerts_id'), table_name='alerts')
    op.drop_table('alerts')
    op.drop_index(op.f('ix_list_items_product_id'), table_name='list_items')
    op.drop_index(op.f('ix_list_items_list_id'), table_name='list_items')
    op.drop_index(op.f('ix_list_items_id'), table_name='list_items')
    op.drop_table('list_items')
    op.drop_index(op.f('ix_lists_id'), table_name='lists')
    op.drop_table('lists')
    op.drop_index(op.f('ix_scores_marketplace'), table_name='scores')
    op.drop_index(op.f('ix_scores_product_id'), table_name='scores')
    op.drop_index(op.f('ix_scores_id'), table_name='scores')
    op.drop_table('scores')
    op.drop_index(op.f('ix_offers_retail_store_id'), table_name='offers_retail')
    op.drop_index(op.f('ix_offers_retail_product_id'), table_name='offers_retail')
    op.drop_index(op.f('ix_offers_retail_id'), table_name='offers_retail')
    op.drop_table('offers_retail')
    op.drop_index(op.f('ix_offers_amz_marketplace'), table_name='offers_amz')
    op.drop_index(op.f('ix_offers_amz_product_id'), table_name='offers_amz')
    op.drop_index(op.f('ix_offers_amz_id'), table_name='offers_amz')
    op.drop_table('offers_amz')
    op.drop_index(op.f('ix_products_asin'), table_name='products')
    op.drop_index(op.f('ix_products_id'), table_name='products')
    op.drop_table('products')
    op.drop_index(op.f('ix_stores_name'), table_name='stores')
    op.drop_index(op.f('ix_stores_id'), table_name='stores')
    op.drop_table('stores')
    op.drop_index(op.f('ix_settings_key'), table_name='settings')
    op.drop_index(op.f('ix_settings_id'), table_name='settings')
    op.drop_table('settings')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')

