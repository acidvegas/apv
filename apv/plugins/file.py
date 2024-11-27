import logging
import logging.handlers
import json
import os
import gzip

class GZipRotatingFileHandler(logging.handlers.RotatingFileHandler):
    '''RotatingFileHandler that compresses old log files using gzip.'''

    def doRollover(self):
        '''Compress old log files using gzip.'''
        super().doRollover()
        if self.backupCount > 0:
            for i in range(self.backupCount, 0, -1):
                sfn = f'{self.baseFilename}.{i}'
                if os.path.exists(sfn):
                    with open(sfn, 'rb') as f_in:
                        with gzip.open(f'{sfn}.gz', 'wb') as f_out:
                            f_out.writelines(f_in)
                    os.remove(sfn)

class JsonFormatter(logging.Formatter):
    def __init__(self, date_format):
        super().__init__()
        self.date_format = date_format

    def format(self, record):
        log_record = {
            'time'        : self.formatTime(record, self.date_format),
            'level'       : record.levelname,
            'module'      : record.module,
            'function'    : record.funcName,
            'line'        : record.lineno,
            'message'     : record.getMessage(),
            'name'        : record.name,
            'filename'    : record.filename,
            'threadName'  : record.threadName,
            'processName' : record.processName,
        }
        return json.dumps(log_record)

def setup_file_handler(level_num: int, log_to_disk: bool, max_log_size: int, 
                      max_backups: int, log_file_name: str, json_log: bool,
                      ecs_log: bool, date_format: str, compress_backups: bool):
    '''Set up the file handler for logging to disk.'''
    if not log_to_disk:
        return

    # Create 'logs' directory if it doesn't exist
    logs_dir = os.path.join(os.getcwd(), 'logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Use the specified log file name and set extension based on json_log
    file_extension = '.json' if json_log else '.log'
    log_file_path = os.path.join(logs_dir, f'{log_file_name}{file_extension}')

    # Create the rotating file handler
    handler_class = GZipRotatingFileHandler if compress_backups else logging.handlers.RotatingFileHandler
    file_handler = handler_class(log_file_path, maxBytes=max_log_size, backupCount=max_backups)
    file_handler.setLevel(level_num)

    if ecs_log:
        try:
            import ecs_logging
        except ImportError:
            raise ImportError("The 'ecs-logging' library is required for ECS logging. Install it with 'pip install ecs-logging'.")
        file_formatter = ecs_logging.StdlibFormatter()
    elif json_log:
        file_formatter = JsonFormatter(date_format)
    else:
        file_formatter = logging.Formatter(
            fmt='%(asctime)s ┃ %(levelname)-8s ┃ %(module)s ┃ %(funcName)s ┃ %(lineno)d ┃ %(message)s',
            datefmt=date_format
        )

    file_handler.setFormatter(file_formatter)
    logging.getLogger().addHandler(file_handler) 