import json
import boto3
import base64
s3 = boto3.client('s3')

client= boto3.client(service_name = 'sagemaker-runtime')
THRESHOLD = .94
ENDPOINT = 'image-classification-2022-12-20-21-30-19-894'


#Serialize Data
def lambda_handler(event, context):
    """A function to serialize target data from S3"""
    
    # Get the s3 address from the Step Function event input
    key = event['s3_key'] ## TODO: fill in
    bucket = event['s3_bucket'] ## TODO: fill in
    
    # Download the data from s3 to /tmp/image.png
    ## TODO: fill in
    local_file_name = "/tmp/image.png"
    s3.download_file(bucket, key, local_file_name)
    
    # We read the data from a file
    with open(local_file_name, "rb") as f:
        image_data = base64.b64encode(f.read())

    # Pass the data back to the Step Function
    print("Event:", event.keys())
    return {
        'statusCode': 200,
        'body': {
            "image_data": image_data,
            "s3_bucket": bucket,
            "s3_key": key,
            "inferences": []
        }
    }

#Classify Serialized Data
def lambda_handler(event, context):

    # Decode the image data
    image = base64.b64decode(event['body']['image_data'])## TODO: fill in)
    
    inferences = client.invoke_endpoint(EndpointName = ENDPOINT,
        Body = image,
        ContentType = 'image/png')
    
    print(inferences)
    # We return the data back to the Step Function    
    event["body"]["inferences"] = list(inferences['Body'].read().decode('utf-8').strip('][').split(', '))
    return {
        'statusCode': 200,
        'body': {
            "image_data": event['body']["image_data"],
            "s3_key": event['body']["s3_key"],
            "s3_bucket": event['body']["s3_bucket"],
            "inferences": event['body']["inferences"]
        }
    }


# Filter Low Confidence
def lambda_handler(event, context):
    
    # Grab the inferences from the event
    inferences = event["body"]["inferences"] ## TODO: fill in
    print(inferences)
    # Check if any values in our inferences are above THRESHOLD
    if (float(inferences[0]) > THRESHOLD) | (float(inferences[1]) > THRESHOLD):
        meets_threshold = True ## TODO: fill in
    else:
        meets_threshold = False
    # If our threshold is met, pass our data back out of the
    # Step Function, else, end the Step Function with an error
    if meets_threshold:
        pass
    else:
        raise ValueError("THRESHOLD_CONFIDENCE_NOT_MET")

    return {
        'statusCode': 200,
        'body': json.dumps(event['body'])
    }


