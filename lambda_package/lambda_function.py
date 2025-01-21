import os
from datetime import datetime

def lambda_handler(event, context):
    print(f"Running task at {datetime.now()}...")
    # Replace these with the appropriate commands for your project
    os.system('python fetch_crypto.py')
    os.system('python fetch_stocks.py')
    os.system('python VaR.py')
    return {
        'statusCode': 200,
        'body': 'Task completed successfully'
    }
