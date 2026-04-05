import logging
from logstash_async.handler import AsynchronousLogstashHandler

def setup_app_logging(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    try:
        # Logstash handler (TCP port 5044 as configured in logstash.conf)
        # We use a try-except because in CI/test environments, host 'logstash' might not resolve
        logstash_handler = AsynchronousLogstashHandler(
            host='logstash', 
            port=5044, 
            database_path=None
        )
        
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logstash_handler.setFormatter(formatter)
        logger.addHandler(logstash_handler)
    except Exception:
        # Fallback to standard logging if Logstash is unreachable or host resolution fails
        pass
    
    # Also log to console
    console_handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
