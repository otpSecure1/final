from boto.s3.connection import S3Connection
s3 = S3Connection(os.environ['account_sid'],os.environ['auth_token'],os.environ['twilionumber'],os.environ['twiliosmsnumber'],os.environ['API_TOKEN'],os.environ['callurl'], os.environ['twiliosmsurl'])
