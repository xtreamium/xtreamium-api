import datetime as dt
from typing import List, Optional, Dict

import sqlalchemy.orm as orm
from sqlalchemy import text

from app.models.channel import Channel
from app.models.programme import Programme
from app.services.logger import get_logger
from app.utils.iptv_parser_ng import Channel as XMLTVChannel, Programme as XMLTVProgramme

logger = get_logger(__name__)


async def store_epg_channels(channels: List[XMLTVChannel], user_id: str, server_id: int, db: orm.Session):
    """
    Store parsed XMLTV channels and programmes in the database using bulk operations for performance

    Args:
        channels: List of Channel objects from XMLTV parser
        user_id: User ID who owns the EPG data
        server_id: Server ID where the EPG data comes from
        db: Database session
    """
    logger.info(f"Storing EPG data for user {user_id}, server {server_id} - {len(channels)} channels")

    try:
        # Collect all XMLTV channel IDs for bulk lookup
        xmltv_ids = [channel.id for channel in channels]

        # Bulk query to get all existing channels
        existing_channels = db.query(Channel).filter(
            Channel.user_id == user_id,
            Channel.server_id == server_id,
            Channel.xmltv_id.in_(xmltv_ids)
        ).all()

        # Create lookup map for existing channels
        existing_channels_map: Dict[str, Channel] = {
            channel.xmltv_id: channel for channel in existing_channels
        }

        # Collect existing channel IDs for bulk programme deletion
        existing_channel_ids = [channel.id for channel in existing_channels]

        # Bulk delete existing programmes to avoid duplicates
        if existing_channel_ids:
            # Use SQLAlchemy's .in_() method instead of raw SQL for better handling of large lists
            db.query(Programme).filter(Programme.channel_id.in_(existing_channel_ids)).delete(synchronize_session=False)
            logger.debug(f"Deleted existing programmes for {len(existing_channel_ids)} channels")

        # Prepare bulk data for channels and programmes
        channels_to_insert = []
        programmes_to_insert = []

        new_channels_count = 0
        updated_channels_count = 0

        # Process all channels and prepare bulk operations
        for xmltv_channel in channels:
            if xmltv_channel.id in existing_channels_map:
                # Update existing channel
                existing_channel = existing_channels_map[xmltv_channel.id]
                existing_channel.set_display_names(xmltv_channel.display_names)
                existing_channel.set_icons(xmltv_channel.icons)
                existing_channel.set_urls(xmltv_channel.urls)
                existing_channel.date_last_updated = dt.datetime.now(dt.timezone.utc)
                updated_channels_count += 1
                channel_db_id = existing_channel.id
            else:
                # Prepare new channel data with JSON serialization
                import json
                channel_data = {
                    'user_id': user_id,
                    'server_id': server_id,
                    'xmltv_id': xmltv_channel.id,
                    'display_names': json.dumps(xmltv_channel.display_names) if xmltv_channel.display_names else None,
                    'icons': json.dumps(xmltv_channel.icons) if xmltv_channel.icons else None,
                    'urls': json.dumps(xmltv_channel.urls) if xmltv_channel.urls else None,
                    'date_created': dt.datetime.now(dt.timezone.utc),
                    'date_last_updated': dt.datetime.now(dt.timezone.utc)
                }
                channels_to_insert.append(channel_data)
                new_channels_count += 1
                channel_db_id = None

            # For new channels, we need to handle programmes after channel insertion
            if xmltv_channel.id not in existing_channels_map:
                # Store programmes data temporarily with xmltv_id reference
                for xmltv_programme in xmltv_channel.programmes:
                    programme_data = _prepare_programme_data(xmltv_programme, None)
                    programme_data['_xmltv_channel_id'] = xmltv_channel.id  # Temporary reference
                    programmes_to_insert.append(programme_data)
            else:
                # For existing channels, add programmes directly
                for xmltv_programme in xmltv_channel.programmes:
                    programme_data = _prepare_programme_data(xmltv_programme, channel_db_id)
                    programmes_to_insert.append(programme_data)

        # Bulk insert new channels
        if channels_to_insert:
            logger.debug(f"Bulk inserting {len(channels_to_insert)} new channels")
            db.bulk_insert_mappings(Channel, channels_to_insert)
            db.flush()

            # Get the newly inserted channels to map their IDs
            new_channel_xmltv_ids = [ch['xmltv_id'] for ch in channels_to_insert]
            newly_inserted_channels = db.query(Channel).filter(
                Channel.user_id == user_id,
                Channel.server_id == server_id,
                Channel.xmltv_id.in_(new_channel_xmltv_ids)
            ).all()

            # Create mapping of xmltv_id to database ID for new channels
            new_channel_id_map = {ch.xmltv_id: ch.id for ch in newly_inserted_channels}

            # Update programme data with correct channel IDs for new channels
            for programme_data in programmes_to_insert:
                if '_xmltv_channel_id' in programme_data:
                    xmltv_channel_id = programme_data.pop('_xmltv_channel_id')
                    programme_data['channel_id'] = new_channel_id_map[xmltv_channel_id]

        # Bulk insert programmes
        if programmes_to_insert:
            logger.debug(f"Bulk inserting {len(programmes_to_insert)} programmes")
            db.bulk_insert_mappings(Programme, programmes_to_insert)

        # Commit all changes
        db.commit()

        total_programmes = len(programmes_to_insert)

        logger.info(f"EPG storage completed successfully:")
        logger.info(f"  - New channels: {new_channels_count}")
        logger.info(f"  - Updated channels: {updated_channels_count}")
        logger.info(f"  - Total programmes stored: {total_programmes}")
        logger.info(f"  - User: {user_id}, Server: {server_id}")

        return {
            "channels": new_channels_count,
            "programmes": total_programmes,
            "success": True
        }

    except Exception as e:
        logger.error(f"Failed to store EPG data for user {user_id}, server {server_id}: {e}")
        db.rollback()
        raise


def _prepare_programme_data(xmltv_programme: XMLTVProgramme, channel_id: int) -> dict:
    """
    Convert an XMLTV Programme object to a dictionary for bulk insert

    Args:
        xmltv_programme: Programme object from XMLTV parser
        channel_id: Database ID of the channel this programme belongs to

    Returns:
        dict: Programme data ready for bulk insert
    """
    import json

    # Helper function to safely serialize JSON
    def safe_json_dumps(data):
        return json.dumps(data) if data is not None else None

    return {
        'channel_id': channel_id,
        'start_time': xmltv_programme.start,
        'stop_time': xmltv_programme.stop,
        'pdc_start': xmltv_programme.pdc_start,
        'vps_start': xmltv_programme.vps_start,
        'showview': xmltv_programme.showview,
        'videoplus': xmltv_programme.videoplus,
        'clumpidx': xmltv_programme.clumpidx,
        'date': xmltv_programme.date,
        'new': xmltv_programme.new,
        'titles': safe_json_dumps(xmltv_programme.titles),
        'sub_titles': safe_json_dumps(xmltv_programme.sub_titles),
        'descriptions': safe_json_dumps(xmltv_programme.descriptions),
        'credits': safe_json_dumps(xmltv_programme.credits),
        'categories': safe_json_dumps(xmltv_programme.categories),
        'keywords': safe_json_dumps(xmltv_programme.keywords),
        'language': safe_json_dumps(xmltv_programme.language),
        'orig_language': safe_json_dumps(xmltv_programme.orig_language),
        'length': safe_json_dumps(xmltv_programme.length),
        'icons': safe_json_dumps(xmltv_programme.icons),
        'urls': safe_json_dumps(xmltv_programme.urls),
        'countries': safe_json_dumps(xmltv_programme.countries),
        'episode_nums': safe_json_dumps(xmltv_programme.episode_nums),
        'video': safe_json_dumps(xmltv_programme.video),
        'audio': safe_json_dumps(xmltv_programme.audio),
        'previously_shown': safe_json_dumps(xmltv_programme.previously_shown),
        'premiere': safe_json_dumps(xmltv_programme.premiere),
        'last_chance': safe_json_dumps(xmltv_programme.last_chance),
        'subtitles': safe_json_dumps(xmltv_programme.subtitles),
        'ratings': safe_json_dumps(xmltv_programme.ratings),
        'star_ratings': safe_json_dumps(xmltv_programme.star_ratings),
        'reviews': safe_json_dumps(xmltv_programme.reviews),
        'images': safe_json_dumps(xmltv_programme.images),
        'date_created': dt.datetime.now(dt.timezone.utc),
        'date_last_updated': dt.datetime.now(dt.timezone.utc)
    }


def _create_programme_from_xmltv(xmltv_programme: XMLTVProgramme, channel_id: int) -> Programme:
    """
    Convert an XMLTV Programme object to a database Programme object
    NOTE: This method is kept for backwards compatibility but is not used in the optimized bulk operations

    Args:
        xmltv_programme: Programme object from XMLTV parser
        channel_id: Database ID of the channel this programme belongs to

    Returns:
        Programme: Database Programme object ready to be stored
    """
    db_programme = Programme(
        channel_id=channel_id,
        start_time=xmltv_programme.start,
        stop_time=xmltv_programme.stop,
        pdc_start=xmltv_programme.pdc_start,
        showview=xmltv_programme.showview,
        videoplus=xmltv_programme.videoplus,
        clumpidx=xmltv_programme.clumpidx,
        date=xmltv_programme.date,
        new=xmltv_programme.new
    )

    # Set JSON fields using the helper methods
    db_programme.set_titles(xmltv_programme.titles)
    db_programme.set_json_field('sub_titles', xmltv_programme.sub_titles)
    db_programme.set_descriptions(xmltv_programme.descriptions)
    db_programme.set_credits(xmltv_programme.credits)
    db_programme.set_categories(xmltv_programme.categories)
    db_programme.set_json_field('keywords', xmltv_programme.keywords)
    db_programme.set_json_field('language', xmltv_programme.language)
    db_programme.set_json_field('orig_language', xmltv_programme.orig_language)
    db_programme.set_json_field('length', xmltv_programme.length)
    db_programme.set_json_field('icons', xmltv_programme.icons)
    db_programme.set_json_field('urls', xmltv_programme.urls)
    db_programme.set_json_field('countries', xmltv_programme.countries)
    db_programme.set_json_field('episode_nums', xmltv_programme.episode_nums)
    db_programme.set_json_field('video', xmltv_programme.video)
    db_programme.set_json_field('audio', xmltv_programme.audio)
    db_programme.set_json_field('previously_shown', xmltv_programme.previously_shown)
    db_programme.set_json_field('premiere', xmltv_programme.premiere)
    db_programme.set_json_field('last_chance', xmltv_programme.last_chance)
    db_programme.set_json_field('subtitles', xmltv_programme.subtitles)
    db_programme.set_json_field('ratings', xmltv_programme.ratings)
    db_programme.set_json_field('star_ratings', xmltv_programme.star_ratings)
    db_programme.set_json_field('reviews', xmltv_programme.reviews)
    db_programme.set_json_field('images', xmltv_programme.images)

    return db_programme


async def get_channel_by_xmltv_id(user_id: str, server_id: int, xmltv_id: str, db: orm.Session) -> Optional[Channel]:
    """
    Get a channel by its XMLTV ID for a specific user and server

    Args:
        user_id: User ID
        server_id: Server ID
        xmltv_id: XMLTV channel ID
        db: Database session

    Returns:
        Channel object or None if not found
    """
    return db.query(Channel).filter(
        Channel.user_id == user_id,
        Channel.server_id == server_id,
        Channel.xmltv_id == xmltv_id
    ).first()


async def get_channels_for_user_server(user_id: str, server_id: int, db: orm.Session) -> List[Channel]:
    """
    Get all channels for a specific user and server

    Args:
        user_id: User ID
        server_id: Server ID
        db: Database session

    Returns:
        List of Channel objects
    """
    return db.query(Channel).filter(
        Channel.user_id == user_id,
        Channel.server_id == server_id
    ).all()


async def get_programmes_for_channel(channel_id: int, db: orm.Session, start_time: Optional[str] = None,
                                     end_time: Optional[str] = None) -> List[Programme]:
    """
    Get programmes for a specific channel, optionally filtered by time range

    Args:
        channel_id: Database channel ID
        start_time: Optional start time filter (XMLTV format)
        end_time: Optional end time filter (XMLTV format)
        db: Database session

    Returns:
        List of Programme objects
    """
    query = db.query(Programme).filter(Programme.channel_id == channel_id)

    if start_time:
        query = query.filter(Programme.start_time >= start_time)

    if end_time:
        query = query.filter(Programme.start_time <= end_time)

    return query.order_by(Programme.start_time).all()


async def get_current_and_next_programmes(channel_id: int, current_time: str, db: orm.Session) -> dict:
    """
    Get current and next programmes for a channel based on the given time

    Args:
        channel_id: Database channel ID
        current_time: Current time in XMLTV format
        db: Database session

    Returns:
        Dict with 'current' and 'next' programme objects
    """
    # Get current programme (started before current_time, ends after current_time)
    current_programme = db.query(Programme).filter(
        Programme.channel_id == channel_id,
        Programme.start_time <= current_time,
        Programme.stop_time > current_time
    ).first()

    # Get next programme (starts after current time)
    next_programme = db.query(Programme).filter(
        Programme.channel_id == channel_id,
        Programme.start_time > current_time
    ).order_by(Programme.start_time).first()

    return {
        "current": current_programme,
        "next": next_programme
    }


async def delete_epg_data_for_user_server(user_id: str, server_id: int, db: orm.Session):
    """
    Delete all EPG data (channels and programmes) for a specific user and server

    Args:
        user_id: User ID
        server_id: Server ID
        db: Database session
    """
    try:
        # Get all channels for this user/server
        channels = db.query(Channel).filter(
            Channel.user_id == user_id,
            Channel.server_id == server_id
        ).all()

        channel_ids = [channel.id for channel in channels]

        if channel_ids:
            # Delete programmes first (due to foreign key constraint)
            programmes_deleted = db.query(Programme).filter(
                Programme.channel_id.in_(channel_ids)
            ).delete(synchronize_session=False)

            # Delete channels
            channels_deleted = db.query(Channel).filter(
                Channel.user_id == user_id,
                Channel.server_id == server_id
            ).delete(synchronize_session=False)

            db.commit()

            logger.info(f"Deleted EPG data for user {user_id}, server {server_id}: "
                        f"{channels_deleted} channels, {programmes_deleted} programmes")
        else:
            logger.info(f"No EPG data found to delete for user {user_id}, server {server_id}")

    except Exception as e:
        logger.error(f"Failed to delete EPG data for user {user_id}, server {server_id}: {e}")
        db.rollback()
        raise
