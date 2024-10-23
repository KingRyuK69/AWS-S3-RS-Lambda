import json
import boto3
import os
import time

def lambda_handler(event, context):
    start_time = time.time()
    print("Lambda function started.")

    # Initializing AWS clients for S3 and Redshift Data API
    s3_client = boto3.client('s3')
    redshift_client = boto3.client('redshift-data')
    
    # Checking if 'Records' is present in the event
    if 'Records' not in event:
        print("No Records found in the event.")
        return {
            'statusCode': 400,
            'body': 'Invalid event format'
        }
        
    print("Event received: ", event)
    
    # Iterating over each record in the event
    for record in event['Records']:
        try:
            s3_bucket = record['s3']['bucket']['name']
            s3_key = record['s3']['object']['key']
            from_path = f"s3://{s3_bucket}/{s3_key}"
            print(f"S3 Bucket: {s3_bucket}, S3 Key: {s3_key}, File Path: {from_path}")
        except KeyError as e:
            print(f"KeyError in extracting S3 details: {e}")
            return {"statusCode": 400, "body": f"Invalid S3 structure: {e}"}

        # Retrieving environment variables for db connection
        dbname = os.getenv('DBNAME')
        user = os.getenv('REDSHIFT_USER')
        tablename = os.getenv('Tbl1')
        
        print(f"DB Name: {dbname}, User: {user}, Table: {tablename}")
        
        # Constructing Redshift COPY command
        copy_command = f"""
            COPY {tablename}
            FROM '{from_path}'
            IAM_ROLE 'arn:aws:iam::730335479574:role/S3-RS-custom-policy-demo'
            CSV
            IGNOREHEADER 1
            NULL 'NULL'
            BLANKSASNULL
            EMPTYASNULL
            DATEFORMAT 'auto' 
            TIMEFORMAT 'auto'
            ACCEPTINVCHARS;
        """
        
        try:
            # Executing the COPY command
            response = redshift_client.execute_statement(
                ClusterIdentifier='redshift-cluster-1',
                Database=dbname,
                DbUser=user,
                Sql=copy_command
            )
            statement_id = response['Id']
            print(f"COPY command executed. Statement ID: {statement_id}")
            
            # Polling the status of COPY command until it finishes execution
            while True:
                status_response = redshift_client.describe_statement(Id=statement_id)
                status = status_response['Status']
                print(f"Statement status: {status}")
                if status in ['FINISHED', 'FAILED', 'ABORTED']:
                    break
                time.sleep(1)

            # Checking if the COPY command has failed
            if status == 'FAILED':
                print(f"Error in COPY command: {status_response['Error']}")
                return {"statusCode": 500, "body": str(status_response['Error'])}

            print("Data loaded successfully.")
            
        except Exception as e:
            # Handling any else exceptions that occur during the process
            print(f"Error loading data from {from_path}: {e}")
            return {"statusCode": 500, "body": str(e)}
    
    end_time = time.time()
    print(f"Lambda function completed in {end_time - start_time} seconds.")
    
    return {"statusCode": 200, "body": "Function executed successfully."}
