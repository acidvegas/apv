import logging
import json
import boto3
from botocore.exceptions import ClientError

class CloudWatchHandler(logging.Handler):
    def __init__(self, group_name, stream_name):
        super().__init__()
        self.group_name = group_name
        self.stream_name = stream_name
        self.client = boto3.client('logs')
        self._initialize_log_group_and_stream()

    def _initialize_log_group_and_stream(self):
        # Create log group if it doesn't exist
        try:
            self.client.create_log_group(logGroupName=self.group_name)
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise e

        # Create log stream if it doesn't exist
        try:
            self.client.create_log_stream(
                logGroupName=self.group_name,
                logStreamName=self.stream_name
            )
        except ClientError as e:
            if e.response['Error']['Code'] != 'ResourceAlreadyExistsException':
                raise e

    def _get_sequence_token(self):
        try:
            response = self.client.describe_log_streams(
                logGroupName=self.group_name,
                logStreamNamePrefix=self.stream_name,
                limit=1
            )
            log_streams = response.get('logStreams', [])
            return log_streams[0].get('uploadSequenceToken') if log_streams else None
        except Exception:
            return None

    def emit(self, record):
        try:
            log_entry = self.format(record)
            timestamp = int(record.created * 1000)
            
            event = {
                'timestamp': timestamp,
                'message': log_entry
            }
            
            kwargs = {
                'logGroupName': self.group_name,
                'logStreamName': self.stream_name,
                'logEvents': [event]
            }
            
            sequence_token = self._get_sequence_token()
            if sequence_token:
                kwargs['sequenceToken'] = sequence_token
                
            self.client.put_log_events(**kwargs)
        except Exception:
            self.handleError(record) 

def setup_cloudwatch_handler(level_num: int, group_name: str, stream_name: str, date_format: str):
    '''Set up the CloudWatch handler.'''
    try:
        import boto3
    except ImportError:
        raise ImportError('boto3 is required for CloudWatch logging. (pip install boto3)')

    if not group_name or not stream_name:
        logging.error('CloudWatch log group and log stream must be specified for CloudWatch handler.')
        return

    cloudwatch_handler = CloudWatchHandler(group_name, stream_name)
    cloudwatch_handler.setLevel(level_num)
    
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_record = {
                'time'        : self.formatTime(record, date_format),
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
    
    cloudwatch_formatter = JsonFormatter(datefmt=date_format)
    cloudwatch_handler.setFormatter(cloudwatch_formatter)
    logging.getLogger().addHandler(cloudwatch_handler) 