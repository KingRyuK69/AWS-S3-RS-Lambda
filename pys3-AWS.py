import json
import boto3
import os
import time

def lambda_handler(event, context):
    start_time = time.time()
    print("Lambda function started.")

    # Initialize AWS clients for S3 and Redshift Data API
    s3_client = boto3.client('s3')
    redshift_client = boto3.client('redshift-data')
    
    # Check if 'Records' is present in the event
    if 'Records' not in event:
        print("No Records found in the event.")
        return {
            'statusCode': 400,
            'body': 'Invalid event format'
        }
    
    # Iterate over each record in the event
    for record in event['Records']:
        s3_bucket = record['s3']['bucket']['name']
        s3_key = record['s3']['object']['key']
        from_path = f"s3://{s3_bucket}/{s3_key}"
        
        # Retrieve environment variables for database connection
        dbname = os.getenv('DBNAME')
        user = os.getenv('REDSHIFT_USER')
        tablename = os.getenv('TABLENAME')
        
        # Construct the Redshift COPY command
        copy_command = f"""
            COPY {tablename}
            FROM '{from_path}'
            IAM_ROLE 'arn:aws:iam::730335479574:role/S3-RS-custom-policy-demo'
            CSV
            IGNOREHEADER 1;
        """
        
        try:
            # Execute the COPY command
            response = redshift_client.execute_statement(
                ClusterIdentifier='redshift-cluster-1',
                Database=dbname,
                DbUser=user,
                Sql=copy_command
            )
            statement_id = response['Id']
            print(f"COPY command executed. Statement ID: {statement_id}")
            
            # Poll the status of the COPY command until it finishes
            while True:
                status_response = redshift_client.describe_statement(Id=statement_id)
                status = status_response['Status']
                print(f"Statement status: {status}")
                if status in ['FINISHED', 'FAILED', 'ABORTED']:
                    break
                time.sleep(1)

            # Check if the COPY command failed
            if status == 'FAILED':
                print(f"Error in COPY command: {status_response['Error']}")
                return {"statusCode": 500, "body": str(status_response['Error'])}

            print("Data loaded successfully.")
            
        except Exception as e:
            # Handle any exceptions that occur during the process
            print(f"Error loading data from {from_path}: {e}")
            return {"statusCode": 500, "body": str(e)}
    
    end_time = time.time()
    print(f"Lambda function completed in {end_time - start_time} seconds.")
    
    return {"statusCode": 200, "body": "Function executed successfully."}