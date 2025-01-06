# Automated Data Pipeline for S3 to Redshift Integration

This project demonstrates the creation of an automated data pipeline using **AWS Lambda**, **Amazon S3**, and **Amazon Redshift**. The pipeline is designed to transfer data from S3 to Redshift upon the upload of a file to the S3 bucket. 

---

## Features
- **Serverless Architecture**: Built using AWS Lambda to handle S3 events and execute Redshift COPY commands.
- **Automated Triggers**: S3 event notifications automatically invoke the Lambda function.
- **Secure Data Flow**: Configured IAM roles for secure access between S3, Lambda, and Redshift.
- **Monitoring**: AWS CloudWatch integration for tracking performance and troubleshooting errors.

---

## Architecture Overview
1. **Amazon S3**: Stores incoming files (e.g., CSV files) that trigger the Lambda function.
2. **AWS Lambda**: Processes the event, formats the data, and executes the Redshift COPY command.
3. **Amazon Redshift**: Serves as the data warehouse where the uploaded data is ingested and stored.
4. **IAM Roles**: Ensure secure communication between the services.

---

## Prerequisites
- AWS Account with permissions to create and manage S3, Redshift, Lambda, and IAM roles.
- Python 3.x installed locally for Lambda function development.
- Basic knowledge of AWS CLI and SQL for interacting with Redshift.

---

## Setup Steps

### 1. Create a Redshift Cluster
1. Navigate to Amazon Redshift in the AWS Management Console.
2. Create a cluster with appropriate settings:
   - **Cluster Identifier**: Unique name for your cluster.
   - **Node Type**: Select based on your workload.
   - **Master Credentials**: Provide a username and password.
3. Configure security groups and VPC to allow access from the Lambda function.

### 2. Create an S3 Bucket
1. Navigate to Amazon S3 and create a bucket:
   - Provide a unique name and region.
   - Configure permissions to allow Redshift and Lambda access.

### 3. Set Up IAM Roles
- **Redshift Role**:
  - Attach `AmazonS3ReadOnlyAccess` or create a custom policy.
- **Lambda Role**:
  - Attach policies for S3, Redshift, and basic Lambda execution:
    - `AWSLambdaBasicExecutionRole`
    - `AmazonS3ReadOnlyAccess`
    - Custom policy for Redshift.

### 4. Create a Lambda Function
1. Navigate to AWS Lambda and create a new function.
2. Write the Lambda function using Boto3 to:
   - Trigger on S3 events.
   - Execute the Redshift COPY command.
3. Configure environment variables:
   - `S3_BUCKET`: Name of the S3 bucket.
   - `REDSHIFT_CLUSTER`: Cluster endpoint.
   - `DB_NAME`, `DB_USER`, `DB_PASSWORD`: Redshift database credentials.
4. Add an S3 trigger to invoke the Lambda function upon file upload.

---

## Lambda Function Example (Python)
```python
import boto3
import psycopg2
import os

def lambda_handler(event, context):
    # Parse S3 event
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = event['Records'][0]['s3']['object']['key']

    # Redshift details
    redshift_host = os.environ['REDSHIFT_CLUSTER']
    redshift_db = os.environ['DB_NAME']
    redshift_user = os.environ['DB_USER']
    redshift_password = os.environ['DB_PASSWORD']
    table_name = 'your_table_name'

    # Establish connection to Redshift
    conn = psycopg2.connect(
        host=redshift_host,
        dbname=redshift_db,
        user=redshift_user,
        password=redshift_password
    )
    cursor = conn.cursor()

    # Copy data from S3 to Redshift
    copy_command = f"""
        COPY {table_name}
        FROM 's3://{bucket}/{key}'
        IAM_ROLE 'your-redshift-iam-role-arn'
        CSV
        IGNOREHEADER 1;
    """
    cursor.execute(copy_command)
    conn.commit()

    # Close connection
    cursor.close()
    conn.close()

    return {
        'statusCode': 200,
        'body': f'Successfully loaded {key} into {table_name}'
    }
```

---

## Testing
1. **Upload a File**: Place a CSV file in the S3 bucket.
2. **Monitor Lambda Execution**: Check AWS Lambda logs in CloudWatch for errors or success messages.
3. **Verify Data in Redshift**: Use the Redshift Query Editor to validate the data transfer.

---

## Monitoring and Maintenance
- **CloudWatch Logs**: Monitor Lambda execution and troubleshoot errors.
- **Redshift Monitoring**: Use Redshift's monitoring tools to check performance and query efficiency.
- **Pipeline Optimization**: Periodically review IAM roles and resource usage.

---

## Future Enhancements
- Add support for different file formats (e.g., JSON, Parquet).
- Implement data validation checks before ingestion.
- Automate cluster scaling based on workload.

---

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
