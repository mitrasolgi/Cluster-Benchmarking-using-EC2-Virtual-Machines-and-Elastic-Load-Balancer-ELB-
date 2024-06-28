import requests
import threading
import json
import config
from datetime import datetime

# Replace the URL with the public IP of the orchestrator instance
url = f"http://{config.orchestrator_ip}/new_request"

# Sample data for the request
request_data = {"key": "value"}

# Make a POST request to the /new_request endpoint
try:
    response = requests.post(url, json=request_data)

    # Print the status code and response content
    print(f"Status Code: {response.status_code}")
    print("Response Content:")
    print(json.dumps(response.json(), indent=2))

except json.JSONDecodeError:
    # Handle the case where the response is not valid JSON
    print(f"Non-JSON response received: {response.text}")

except requests.exceptions.RequestException as e:
    # Handle other request exceptions
    print(f"Request failed: {e}")

def send_requests(orchestrator_url):
    """Sets up requests threads"""
    start_time = datetime.utcnow()

    # Create a list to store thread instances
    threads = []

    # Start 10 threads, each sending 5 POST requests
    for _ in range(1):
        thread = threading.Thread(target=post_requests, args=(orchestrator_url,1))
        threads.append(thread)
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    end_time = datetime.utcnow()
    print("Result for Requests:")

def post_requests(url, n):
    """Makes a post request n times at the given url"""
    for i in range(n):
        call_end_point_http_post(url)

def call_end_point_http_post(url):
    headers = {'content-type': 'application/json'}
    res = requests.post(url, json=request_data, headers=headers)
    return res

if __name__ == "__main__":
    print("POST requests concurrently:")
    send_requests(url)
