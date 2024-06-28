from flask import Flask, request, jsonify
import threading
import json
import time
import requests

app = Flask(__name__)
file_lock = threading.Lock()
queue_lock = threading.Lock()
request_queue = []


def send_request_to_container(container_id, container_info, incoming_request_data):
    response = f"Sending request to {container_id} with data: {incoming_request_data}"

    container_ip = container_info["ip"]
    container_port = container_info["port"]

    # Construct the URL for the container
    container_url = f"http://{container_ip}:{container_port}/run_model"

    try:
        # Make a POST request to the container
        #received_response = requests.post(container_url, json=incoming_request_data)
        #received_response_string = json.dumps(received_response)
        #response = response + received_response_string
        response = requests.post(container_url, json=incoming_request_data)
        print(f"Received response from container {container_id}.")
        print(response)

    except Exception as e:
        #response = response + f"Error: {e}"
        response = None
        print(f"Error: {e}")

    return response


def update_container_status(container_id, status):
    with file_lock:
        with open("container_info.json", "r") as f:
            data = json.load(f)
        data[container_id]["status"] = status
        with open("container_info.json", "w") as f:
            json.dump(data, f)


def queue_check():
    with queue_lock:
        if request_queue:
            return request_queue.pop
        else:
            return None
    

def handle_everything_in_queue(free_container, data, incoming_request_data):

    request = queue_check()

    while request:
        update_container_status(free_container, "busy")
        send_request_to_container(free_container, data[free_container], incoming_request_data)
        update_container_status(free_container, "free")
        request = queue_check()


def process_request(incoming_request_data):
    with file_lock:
        with open("container_info.json", "r") as f:
            data = json.load(f)
    free_container = None
    for container_id, container_info in data.items():
        if container_info["status"] == "free":
            free_container = container_id
            break
    
    #Test 
    if True:

        update_container_status(free_container, "busy")
        response = send_request_to_container(free_container, data[free_container], incoming_request_data)
        update_container_status(free_container, "free")

        threading.Thread(target=handle_everything_in_queue, args=(free_container, data, incoming_request_data)).start()
        # 
        # return response


    else:
        with queue_lock:
            request_queue.append(incoming_request_data)
            
        return "Request added to queue"

@app.route("/new_request", methods={"POST"})
def new_request():
    incoming_request_data = request.json
    response = process_request(incoming_request_data)
    return jsonify({"message": "Request received and processing started."})


if __name__ == "__main__":
    app.run(port=80)