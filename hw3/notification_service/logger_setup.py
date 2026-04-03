import logging
from logstash_async.handler import AsynchronousLogstashHandler

def setup_app_logging(service_name: str):
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)

    # Logstash handler (TCP port 5044 as configured in logstash.conf)
    logstash_handler = AsynchronousLogstashHandler(
        host='logstash', 
        port=5044, 
        database_path=None
    )
    
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logstash_handler.setFormatter(formatter)
    
    logger.addHandler(logstash_handler)
    
    # Also log to console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger
