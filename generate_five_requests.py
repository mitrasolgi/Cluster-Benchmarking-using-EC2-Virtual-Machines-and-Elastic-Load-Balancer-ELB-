import requests
import json
from multiprocessing import Pool
import config

def send_request(request_data):
    try:
        # Replace the URL with the public IP of the orchestrator instance
        url = f"http://{config.orchestrator_ip}/new_request"

        # Make a POST request to the /new_request endpoint
        response = requests.post(url, json=request_data)

        # Print the status code and response content
        print(f"Status Code: {response.status_code}")
        print("Response Content:")
        print(json.dumps(response.json(), indent=2))

    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    # Sample data for the request
    request_data = {"key": "value"}

    # Number of concurrent requests
    num_requests = 1

    # Use a Pool to create a pool of worker processes
    with Pool(processes=num_requests) as pool:
        # Map the send_request function to the pool of processes
        pool.map(send_request, [request_data] * num_requests)