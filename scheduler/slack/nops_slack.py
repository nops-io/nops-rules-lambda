import boto3
import urllib3
import json
import os

# Define the base URL for the RESTful API
base_url = 'https://app.nops.io/svc/notifications/scheduler/nops_scheduler'

# Define the function to make the POST request with access key
def post_request(endpoint_url, request_body, access_key):
    # Set the API headers with the access key
    headers = {'Authorization': 'Bearer ' + access_key, "accept" : "application/json, text/plain, */*", "content-type": "application/json;charset=UTF-8"}
    encoded_data = json.dumps(request_body).encode('utf-8')
    http = urllib3.PoolManager()

    # Send the POST request to the API endpoint with the request body as JSON and headers
    response = http.request('POST', endpoint_url, body=encoded_data, headers=headers)

    # Return the response from the API
    return response
    
# Define the main Lambda function to handle incoming chatbot requests
def lambda_handler(event, context):
    # Get the input message and parse the arguments from the chatbot event
    schedule_id = event['schedule_id']
    schedule_action = event['schedule_action']

    # Get the access key for the API call from the Lambda environment variables
    access_key = os.environ['ACCESS_KEY']

    # Define the endpoint URL for the API based on the argument that parameterizes a portion of the REST URI
    endpoint_url = f"{base_url}/{schedule_id}/trigger?api_key={access_key}"

    # Define the request body for the API call based on the remaining arguments
    request_body = {
        "action_name": f"{schedule_action}"
    }


    # Make the POST request to the API with the endpoint URL, request body, and access key
    response = post_request(endpoint_url, request_body, access_key)

    # Build the response message to send back to the chatbot user
    response_message = f"The API response code: {response.status} (202 is success)"

    # Return the response message to the chatbot user
    return {
        "response_type": "in_channel",
        "text": response_message
    }
