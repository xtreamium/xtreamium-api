"""Initial migration

Revision ID: 1cec460a3478
Revises: 
Create Date: 2025-09-17 17:59:12.625143

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1cec460a3478'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('hashed_password', sa.String(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=True),
        sa.Column('date_last_updated', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # Create servers table
    op.create_table('servers',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('owner_id', sa.String(length=36), nullable=False),
        sa.Column('name', sa.String(), nullable=True),
        sa.Column('url', sa.String(), nullable=True),
        sa.Column('username', sa.String(), nullable=True),
        sa.Column('password', sa.String(), nullable=True),
        sa.Column('epg_url', sa.String(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=True),
        sa.Column('date_last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.alter_column('programmes', 'videoplus',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programmes', 'showview',
               existing_type=sa.String(),

    # Create channels table
    op.create_table('channels',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('server_id', sa.String(length=36), nullable=False),
        sa.Column('xmltv_id', sa.String(), nullable=False),
        sa.Column('display_names', sa.Text(), nullable=True),
        sa.Column('icons', sa.Text(), nullable=True),
        sa.Column('urls', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=True),
        sa.Column('date_last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'server_id', 'xmltv_id', name='uq_channel_user_server_xmltv')
    )
    op.create_index(op.f('ix_channels_id'), 'channels', ['id'], unique=False)
    op.create_index(op.f('ix_channels_xmltv_id'), 'channels', ['xmltv_id'], unique=False)

    # Create programmes table
    op.create_table('programmes',
        sa.Column('id', sa.String(length=36), nullable=False),
        sa.Column('channel_id', sa.String(length=36), nullable=False),
        sa.Column('start_time', sa.String(), nullable=False),
        sa.Column('stop_time', sa.String(), nullable=True),
        sa.Column('pdc_start', sa.String(), nullable=True),
        sa.Column('vps_start', sa.String(), nullable=True),
        sa.Column('showview', sa.String(), nullable=True),
        sa.Column('videoplus', sa.String(), nullable=True),
        sa.Column('clumpidx', sa.String(), nullable=True, server_default=sa.text("'0/1'")),
        sa.Column('titles', sa.Text(), nullable=True),
        sa.Column('sub_titles', sa.Text(), nullable=True),
        sa.Column('descriptions', sa.Text(), nullable=True),
        sa.Column('credits', sa.Text(), nullable=True),
        sa.Column('date', sa.String(), nullable=True),
        sa.Column('categories', sa.Text(), nullable=True),
        sa.Column('keywords', sa.Text(), nullable=True),
        sa.Column('language', sa.Text(), nullable=True),
        sa.Column('orig_language', sa.Text(), nullable=True),
        sa.Column('length', sa.Text(), nullable=True),
        sa.Column('icons', sa.Text(), nullable=True),
        sa.Column('urls', sa.Text(), nullable=True),
        sa.Column('countries', sa.Text(), nullable=True),
        sa.Column('episode_nums', sa.Text(), nullable=True),
        sa.Column('video', sa.Text(), nullable=True),
        sa.Column('audio', sa.Text(), nullable=True),
        sa.Column('previously_shown', sa.Text(), nullable=True),
        sa.Column('premiere', sa.Text(), nullable=True),
        sa.Column('last_chance', sa.Text(), nullable=True),
        sa.Column('new', sa.Boolean(), nullable=True),
        sa.Column('subtitles', sa.Text(), nullable=True),
        sa.Column('ratings', sa.Text(), nullable=True),
        sa.Column('star_ratings', sa.Text(), nullable=True),
        sa.Column('reviews', sa.Text(), nullable=True),
        sa.Column('images', sa.Text(), nullable=True),
        sa.Column('date_created', sa.DateTime(), nullable=True),
        sa.Column('date_last_updated', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['channel_id'], ['channels.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_programmes_id'), 'programmes', ['id'], unique=False)
    op.create_index(op.f('ix_programmes_start_time'), 'programmes', ['start_time'], unique=False)
    op.create_index(op.f('ix_programmes_stop_time'), 'programmes', ['stop_time'], unique=False)
    op.create_index('idx_programme_channel_start', 'programmes', ['channel_id', 'start_time'], unique=False)
    op.create_index('idx_programme_start_stop', 'programmes', ['start_time', 'stop_time'], unique=False)

    # Create epg table
    op.create_table('epg',
        sa.Column('user_id', sa.String(length=36), nullable=False),
        sa.Column('server_id', sa.String(length=36), nullable=False),
        sa.Column('programs_data', sa.Text(), nullable=False),
        sa.Column('last_updated', sa.DateTime(), nullable=True),
        sa.Column('program_count', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('user_id', 'server_id')
    )
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('programmes', 'id',
               existing_type=sa.INTEGER(),
    # Drop tables in reverse order of creation to respect foreign key constraints
    op.drop_table('epg')

    # Drop programmes table with indexes
    op.drop_index('idx_programme_start_stop', table_name='programmes')
    op.drop_index('idx_programme_channel_start', table_name='programmes')
    op.drop_index(op.f('ix_programmes_stop_time'), table_name='programmes')
    op.drop_index(op.f('ix_programmes_start_time'), table_name='programmes')
    op.drop_index(op.f('ix_programmes_id'), table_name='programmes')
    op.drop_table('programmes')

    # Drop channels table with indexes
    op.drop_index(op.f('ix_channels_xmltv_id'), table_name='channels')
    op.drop_index(op.f('ix_channels_id'), table_name='channels')
    op.drop_table('channels')

    # Drop servers table with indexes
    op.alter_column('channels', 'xmltv_id',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('channels', 'user_id',
               existing_type=sa.String(length=36),
    op.drop_table('servers')

    # Drop users table with indexes
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.create_index(op.f('idx_users_email'), 'users', ['email'], unique=False)
    op.alter_column('users', 'hashed_password',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.alter_column('users', 'email',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.alter_column('users', 'id',
               existing_type=sa.String(length=36),
               type_=sa.TEXT(),
               nullable=True)
    op.drop_index(op.f('ix_servers_username'), table_name='servers')
    op.drop_index(op.f('ix_servers_url'), table_name='servers')
    op.drop_index(op.f('ix_servers_password'), table_name='servers')
    op.drop_index(op.f('ix_servers_name'), table_name='servers')
    op.drop_index(op.f('ix_servers_id'), table_name='servers')
    op.drop_index(op.f('ix_servers_epg_url'), table_name='servers')
    op.create_index(op.f('idx_servers_owner_id'), 'servers', ['owner_id'], unique=False)
    op.create_index(op.f('idx_servers_name'), 'servers', ['name'], unique=False)
    op.create_index(op.f('idx_servers_id'), 'servers', ['id'], unique=False)
    op.alter_column('servers', 'epg_url',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('servers', 'password',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('servers', 'username',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('servers', 'url',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('servers', 'name',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               nullable=False)
    op.alter_column('servers', 'owner_id',
               existing_type=sa.String(length=36),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('servers', 'id',
               existing_type=sa.String(length=36),
               type_=sa.TEXT(),
               nullable=True)
    op.drop_index(op.f('ix_programmes_stop_time'), table_name='programmes')
    op.drop_index(op.f('ix_programmes_start_time'), table_name='programmes')
    op.drop_index(op.f('ix_programmes_id'), table_name='programmes')
    op.alter_column('programmes', 'date',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programmes', 'clumpidx',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True,
               existing_server_default=sa.text("'0/1'"))
    op.alter_column('programmes', 'videoplus',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programmes', 'showview',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programmes', 'vps_start',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programmes', 'pdc_start',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programmes', 'stop_time',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=True)
    op.alter_column('programmes', 'start_time',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('programmes', 'id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)
    op.create_index(op.f('idx_epg_user_id'), 'epg', ['user_id'], unique=False)
    op.create_index(op.f('idx_epg_server_id'), 'epg', ['server_id'], unique=False)
    op.create_index(op.f('idx_epg_last_updated'), 'epg', ['last_updated'], unique=False)
    op.alter_column('epg', 'user_id',
               existing_type=sa.String(length=36),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.drop_constraint('uq_channel_user_server_xmltv', 'channels', type_='unique')
    op.drop_index(op.f('ix_channels_xmltv_id'), table_name='channels')
    op.drop_index(op.f('ix_channels_id'), table_name='channels')
    op.create_index(op.f('idx_channels_xmltv_id'), 'channels', ['xmltv_id'], unique=False)
    op.create_index(op.f('idx_channels_user_server'), 'channels', ['user_id', 'server_id'], unique=False)
    op.create_index(op.f('idx_channels_user_id'), 'channels', ['user_id'], unique=False)
    op.create_index(op.f('idx_channels_server_id'), 'channels', ['server_id'], unique=False)
    op.alter_column('channels', 'xmltv_id',
               existing_type=sa.String(),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('channels', 'user_id',
               existing_type=sa.String(length=36),
               type_=sa.TEXT(),
               existing_nullable=False)
    op.alter_column('channels', 'id',
               existing_type=sa.INTEGER(),
               nullable=True,
               autoincrement=True)
    # ### end Alembic commands ###
