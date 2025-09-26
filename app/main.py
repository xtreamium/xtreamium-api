import logging
import os

from app.services.app_factory import create_app
from app.services.db_factory import create_database
from app.services.logger import get_logger
from app.services.tasks.register_tasks import register_tasks

logger = get_logger(__name__)

logger.info("Starting Xtreamium API")

try:
    logger.info("Creating database...")
    create_database()

    logger.info("Creating FastAPI application...")
    app = create_app()

    logger.info("Registering background tasks...")
    register_tasks(app)

except Exception as e:
    logger.error(f"Failed to initialize application: {e}")
    raise

if __name__ == '__main__':
    import uvicorn

    # Configure uvicorn loggers to use the same format as our application
    uvicorn_logger = get_logger("uvicorn")
    uvicorn_access_logger = get_logger("uvicorn.access")

    # Disable uvicorn's default handlers to prevent duplicate logs
    logging.getLogger("uvicorn").handlers = []
    logging.getLogger("uvicorn.access").handlers = []

    port = int(os.environ.get('XTREAMIUM_BACKEND_PORT', 8000))
    reload = os.environ.get('RELOAD', 'true').lower() == 'true'
    disable_ssl = os.environ.get('DISABLE_SSL', 'false').lower() == 'true'
    
    logger.info(f"Starting uvicorn server on port {port}")

    # SSL configuration - only use if certificates exist and SSL is not disabled
    ssl_keyfile = '/etc/letsencrypt/live/dev.fergl.ie/privkey.pem'
    ssl_certfile = '/etc/letsencrypt/live/dev.fergl.ie/fullchain.pem'
    
    use_ssl = (not disable_ssl and 
               os.path.exists(ssl_keyfile) and 
               os.path.exists(ssl_certfile))
    
    if use_ssl:
        logger.info("SSL certificates found, starting with HTTPS")
    else:
        logger.info("Starting without SSL (HTTP only)")
        ssl_keyfile = None
        ssl_certfile = None

    uvicorn.run(
        'main:app',
        host='0.0.0.0',
        reload=reload,
        port=port,
        ssl_keyfile=ssl_keyfile,
        ssl_certfile=ssl_certfile,
        log_config=None,  # Disable uvicorn's built-in logging config
        use_colors=False  # Disable colored output to match our format
    )
