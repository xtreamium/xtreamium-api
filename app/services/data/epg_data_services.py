import sqlalchemy.orm as orm
from app.models.epg import EPG
from app.services.logger import get_logger

logger = get_logger(__name__)


async def get_epg_data(user_id: str, server_id: int, db: orm.Session):
    """Get EPG data for a specific user and server"""
    logger.debug(f"Fetching EPG data for user {user_id}, server {server_id}")
    try:
        epg = db.query(EPG).filter(EPG.user_id == user_id, EPG.server_id == server_id).first()
        if epg:
            logger.debug(f"Found EPG data with {epg.program_count} programs")
            return epg.get_programs()
        else:
            logger.debug("No EPG data found")
            return []
    except Exception as e:
        logger.error(f"Failed to fetch EPG data for user {user_id}, server {server_id}: {e}")
        return []


async def upsert_epg_data(user_id: str, server_id: int, programs: list, db: orm.Session):
    """Insert or update EPG data for a specific user and server"""
    logger.info(f"Upserting EPG data for user {user_id}, server {server_id} with {len(programs)} programs")
    try:
        # Check if EPG record already exists
        epg = db.query(EPG).filter(EPG.user_id == user_id, EPG.server_id == server_id).first()

        if epg:
            # Update existing record
            logger.debug("Updating existing EPG record")
            epg.set_programs(programs)
        else:
            # Create new record
            logger.debug("Creating new EPG record")
            epg = EPG(user_id=user_id, server_id=server_id)
            epg.set_programs(programs)
            db.add(epg)

        db.commit()
        db.refresh(epg)
        logger.info(f"EPG data updated successfully: {epg.program_count} programs")
        return epg

    except Exception as e:
        logger.error(f"Failed to upsert EPG data for user {user_id}, server {server_id}: {e}")
        db.rollback()
        raise


async def delete_epg_data(user_id: str, server_id: int, db: orm.Session):
    """Delete EPG data for a specific user and server"""
    logger.info(f"Deleting EPG data for user {user_id}, server {server_id}")
    try:
        result = db.query(EPG).filter(EPG.user_id == user_id, EPG.server_id == server_id).delete()
        db.commit()
        if result:
            logger.info(f"EPG data deleted successfully")
        else:
            logger.warning(f"No EPG data found to delete")
        return result > 0
    except Exception as e:
        logger.error(f"Failed to delete EPG data for user {user_id}, server {server_id}: {e}")
        db.rollback()
        raise


async def get_listings_for_channel(user_id: str, server_id: int, channel_id: str, db: orm.Session):
    """Get current and future listings for a specific channel"""
    import time

    logger.debug(f"Fetching listings for channel {channel_id}")
    try:
        programs = await get_epg_data(user_id, server_id, db)
        current_time = int(time.time() * 1000)  # Convert to milliseconds to match EPG format

        listings = [
            program for program in programs
            if program.get('channel') == channel_id and program.get('stop', 0) > current_time
        ]

        logger.debug(f"Found {len(listings)} current/future listings for channel {channel_id}")
        return listings

    except Exception as e:
        logger.error(f"Failed to get listings for channel {channel_id}: {e}")
        return []
