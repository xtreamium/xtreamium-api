import datetime as dt
import json

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app import database


class Channel(database.Base):
    class Config:
        from_attributes = True

    __tablename__ = "channels"
    
    # Primary key
    id = sa.Column(sa.Integer, primary_key=True, index=True)
    
    # Foreign keys
    user_id = sa.Column(sa.String(36), sa.ForeignKey("users.id"), nullable=False)
    server_id = sa.Column(sa.Integer, sa.ForeignKey("servers.id"), nullable=False)
    
    # Channel identification
    xmltv_id = sa.Column(sa.String, nullable=False, index=True)  # The original channel ID from XMLTV
    
    # Channel data - stored as JSON for flexibility since the structure can vary
    display_names = sa.Column(sa.Text, nullable=True)  # JSON array of display names
    icons = sa.Column(sa.Text, nullable=True)  # JSON array of icon data
    urls = sa.Column(sa.Text, nullable=True)  # JSON array of URL data
    
    # Metadata
    date_created = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
    date_last_updated = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
    
    # Relationships
    user = orm.relationship("User")
    server = orm.relationship("Server")
    programmes = orm.relationship("Programme", back_populates="channel", cascade="all, delete-orphan")
    
    # Composite unique constraint to prevent duplicates
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'server_id', 'xmltv_id', name='uq_channel_user_server_xmltv'),
    )
    
    def get_display_names(self):
        """Return parsed display names as Python objects"""
        if self.display_names:
            return json.loads(self.display_names)
        return []
    
    def set_display_names(self, display_names):
        """Store display names as JSON"""
        self.display_names = json.dumps(display_names)
    
    def get_icons(self):
        """Return parsed icons as Python objects"""
        if self.icons:
            return json.loads(self.icons)
        return []
    
    def set_icons(self, icons):
        """Store icons as JSON"""
        self.icons = json.dumps(icons)
    
    def get_urls(self):
        """Return parsed URLs as Python objects"""
        if self.urls:
            return json.loads(self.urls)
        return []
    
    def set_urls(self, urls):
        """Store URLs as JSON"""
        self.urls = json.dumps(urls)