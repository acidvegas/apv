import logging
import json
import socket
import zlib

class GraylogHandler(logging.Handler):
    def __init__(self, host, port):
        super().__init__()
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        
        # Mapping from Python logging levels to Graylog (syslog) levels
        self.level_mapping = {
            logging.CRITICAL : 2, # Critical
            logging.ERROR    : 3, # Error
            logging.WARNING  : 4, # Warning
            logging.INFO     : 6, # Informational
            logging.DEBUG    : 7, # Debug
            logging.NOTSET   : 7  # Default to Debug
        }

    def emit(self, record):
        try:
            log_entry = self.format(record)
            graylog_level = self.level_mapping.get(record.levelno, 7)
            
            gelf_message = {
                'version'       : '1.1',
                'host'          : socket.gethostname(),
                'short_message' : record.getMessage(),
                'full_message'  : log_entry,
                'timestamp'     : record.created,
                'level'         : graylog_level,
                '_logger_name'  : record.name,
                '_file'         : record.pathname,
                '_line'         : record.lineno,
                '_function'     : record.funcName,
                '_module'       : record.module,
            }
            
            message = json.dumps(gelf_message).encode('utf-8')
            compressed = zlib.compress(message)
            self.sock.sendto(compressed, (self.host, self.port))
        except Exception:
            self.handleError(record) 

def setup_graylog_handler(level_num: int, graylog_host: str, graylog_port: int):
    '''Set up the Graylog handler.'''
    if graylog_host is None or graylog_port is None:
        logging.error('Graylog host and port must be specified for Graylog handler.')
        return

    graylog_handler = GraylogHandler(graylog_host, graylog_port)
    graylog_handler.setLevel(level_num)
    graylog_formatter = logging.Formatter(fmt='%(message)s')
    graylog_handler.setFormatter(graylog_formatter)
    logging.getLogger().addHandler(graylog_handler) 