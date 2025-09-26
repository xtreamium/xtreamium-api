import datetime as dt
import json

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app import database


class EPG(database.Base):
    class Config:
        from_attributes = True

    __tablename__ = "epg"

    # Composite primary key
    user_id = sa.Column(sa.String(36), sa.ForeignKey("users.id"), primary_key=True)
    server_id = sa.Column(sa.String(36), sa.ForeignKey("servers.id"), primary_key=True)

    # Store the parsed programs as JSON
    programs_data = sa.Column(sa.Text, nullable=False)

    # Metadata
    last_updated = sa.Column(sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
    program_count = sa.Column(sa.Integer, default=0)

    # Relationships
    user = orm.relationship("User")
    server = orm.relationship("Server")

    def get_programs(self):
        """Return parsed programs as Python objects"""
        if self.programs_data:
            return json.loads(self.programs_data)
        return []

    def set_programs(self, programs):
        """Store programs as JSON and update metadata"""
        self.programs_data = json.dumps(programs)
        self.program_count = len(programs)
        self.last_updated = dt.datetime.now(dt.timezone.utc)
