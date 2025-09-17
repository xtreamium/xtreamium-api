import datetime as dt
import json

import sqlalchemy as sa
from sqlalchemy import orm as orm

from app import database


class Programme(database.Base):
    class Config:
        from_attributes = True

    __tablename__ = "programmes"

    id = sa.Column(sa.Integer, primary_key=True, index=True)

    channel_id = sa.Column(sa.Integer, sa.ForeignKey(
        "channels.id"), nullable=False)

    start_time = sa.Column(sa.String, nullable=False, index=True)
    stop_time = sa.Column(sa.String, nullable=True, index=True)

    # Optional programme attributes
    pdc_start = sa.Column(sa.String, nullable=True)
    vps_start = sa.Column(sa.String, nullable=True)
    showview = sa.Column(sa.String, nullable=True)
    videoplus = sa.Column(sa.String, nullable=True)
    clumpidx = sa.Column(sa.String, default="0/1")

    # Programme content - stored as JSON for flexibility
    titles = sa.Column(sa.Text, nullable=True)  # JSON array of title data
    sub_titles = sa.Column(sa.Text, nullable=True)
    descriptions = sa.Column(sa.Text, nullable=True)
    credits = sa.Column(sa.Text, nullable=True)  # JSON object of credits data
    date = sa.Column(sa.String, nullable=True)  # Programme date
    categories = sa.Column(sa.Text, nullable=True)
    keywords = sa.Column(sa.Text, nullable=True)  # JSON array of keyword data
    language = sa.Column(sa.Text, nullable=True)
    orig_language = sa.Column(sa.Text, nullable=True)
    length = sa.Column(sa.Text, nullable=True)  # JSON object of length data
    icons = sa.Column(sa.Text, nullable=True)  # JSON array of icon data
    urls = sa.Column(sa.Text, nullable=True)  # JSON array of URL data
    countries = sa.Column(sa.Text, nullable=True)  # JSON array of country data
    episode_nums = sa.Column(sa.Text, nullable=True)
    video = sa.Column(sa.Text, nullable=True)  # JSON object of video data
    audio = sa.Column(sa.Text, nullable=True)  # JSON object of audio data
    previously_shown = sa.Column(sa.Text, nullable=True)
    premiere = sa.Column(sa.Text, nullable=True)
    last_chance = sa.Column(sa.Text, nullable=True)
    new = sa.Column(sa.Boolean, default=False)  # New programme flag
    subtitles = sa.Column(sa.Text, nullable=True)
    ratings = sa.Column(sa.Text, nullable=True)  # JSON array of rating data
    star_ratings = sa.Column(sa.Text, nullable=True)
    reviews = sa.Column(sa.Text, nullable=True)  # JSON array of review data
    images = sa.Column(sa.Text, nullable=True)  # JSON array of image data

    # Metadata
    date_created = sa.Column(
        sa.DateTime, default=dt.datetime.now(dt.timezone.utc))
    date_last_updated = sa.Column(
        sa.DateTime, default=dt.datetime.now(dt.timezone.utc))

    # Relationships
    channel = orm.relationship("Channel", back_populates="programmes")

    # Index for performance - commonly queried together
    __table_args__ = (
        sa.Index('idx_programme_channel_start', 'channel_id', 'start_time'),
        sa.Index('idx_programme_start_stop', 'start_time', 'stop_time'),
    )

    def get_titles(self):
        """Return parsed titles as Python objects"""
        if self.titles:
            return json.loads(self.titles)
        return []

    def set_titles(self, titles):
        """Store titles as JSON"""
        self.titles = json.dumps(titles)

    def get_default_title(self):
        """Return the first titles entry's text as default title"""
        titles = self.get_titles()
        if titles and isinstance(titles, list) and len(titles) > 0:
            first_title = titles[0]
            if isinstance(first_title, dict) and 'text' in first_title:
                return first_title['text']
            elif isinstance(first_title, str):
                return first_title
        return ""

    def get_default_description(self):
        """Return the first descriptions entry's text as default description"""
        descriptions = self.get_descriptions()
        if descriptions and isinstance(descriptions, list) and len(descriptions) > 0:
            first_desc = descriptions[0]
            if isinstance(first_desc, dict) and 'text' in first_desc:
                return first_desc['text']
            elif isinstance(first_desc, str):
                return first_desc
        return ""

    def get_descriptions(self):
        """Return parsed descriptions as Python objects"""
        if self.descriptions:
            return json.loads(self.descriptions)
        return []

    def set_descriptions(self, descriptions):
        """Store descriptions as JSON"""
        self.descriptions = json.dumps(descriptions)

    def get_categories(self):
        """Return parsed categories as Python objects"""
        if self.categories:
            return json.loads(self.categories)
        return []

    def set_categories(self, categories):
        """Store categories as JSON"""
        self.categories = json.dumps(categories)

    def get_credits(self):
        """Return parsed credits as Python objects"""
        if self.credits:
            return json.loads(self.credits)
        return {}

    def set_credits(self, credits):
        """Store credits as JSON"""
        self.credits = json.dumps(credits)

    # Helper methods for common JSON fields
    def get_json_field(self, field_name):
        """Generic method to get JSON field data"""
        field_value = getattr(self, field_name, None)
        if field_value:
            return json.loads(field_value)
        return [] if field_name in ['titles', 'sub_titles', 'descriptions', 'categories',
                                    'keywords', 'icons', 'urls', 'countries', 'episode_nums',
                                    'subtitles', 'ratings', 'star_ratings', 'reviews', 'images'] else {}

    def set_json_field(self, field_name, value):
        """Generic method to set JSON field data"""
        setattr(self, field_name, json.dumps(value) if value else None)
