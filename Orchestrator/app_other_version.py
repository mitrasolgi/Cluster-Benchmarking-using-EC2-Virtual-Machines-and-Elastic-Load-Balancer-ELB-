from flask import Flask, request, jsonify
import threading
import json
import time
import requests
from queue import Queue

app = Flask(__name__)
lock = threading.Lock()
request_queue = Queue()

def send_request_to_container(container_id, container_info, incoming_request_data):
    print(f"Sending request to {container_id} with data: {incoming_request_data}...")

    container_ip = container_info["ip"]
    container_port = container_info["port"]

    # Construct the URL for the container
    container_url = f"http://{container_ip}:{container_port}/run_model"

    try:
        # Make a POST request to the container
        response = requests.post(container_url, json=incoming_request_data)

        if response.status_code == 200:
            print(f"Received response from container {container_id}.")
        else:
            print(f"Error: Unable to communicate with container {container_id}.")

    except Exception as e:
        print(f"Error: {e}")

def update_container_status(container_id, status):
    with lock:
        with open("container_info.json", "r") as f:
            data = json.load(f)
        data[container_id]["status"] = status
        with open("container_info.json", "w") as f:
            json.dump(data, f)

def process_request():
    while True:
        incoming_request_data = request_queue.get()
        with lock:
            with open("container_info.json", "r") as f:
                data = json.load(f)

        free_container = next((cid for cid, info in data.items() if info["status"] == "free"), None)

        if free_container:
            update_container_status(free_container, "busy")
            send_request_to_container(
                free_container, data[free_container], incoming_request_data
            )
            update_container_status(free_container, "free")
        else:
            # Handle the case where no free container is available even after dequeuing from the request_queue
            print("No free container available for the request:", incoming_request_data)

        request_queue.task_done()

@app.route("/new_request", methods={"POST"})
def new_request():
    incoming_request_data = request.json
    with lock:
        with open("container_info.json", "r") as f:
            data = json.load(f)

    free_container = next((cid for cid, info in data.items() if info["status"] == "free"), None)

    if free_container:
        threading.Thread(target=send_request_to_container, args=(free_container, data[free_container], incoming_request_data)).start()
    else:
        request_queue.put(incoming_request_data)

    return jsonify({"message": "Request received and processing started."})

if __name__ == "__main__":
    # Start the thread to continuously process the request queue
    queue_processing_thread = threading.Thread(target=process_request)
    queue_processing_thread.start()

    app.run(port=80)
