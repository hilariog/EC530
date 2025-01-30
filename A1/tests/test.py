import subprocess
import os
import time

def run_command(command, cwd=None):
    """Run a terminal command and print its output."""
    result = subprocess.run(command, shell=True, cwd=cwd, text=True, capture_output=True)
    print(result.stdout)
    print(result.stderr)
    return result.returncode

def run_tests():
    # Start the server
    print("Starting server...")
    server_command = "node ../server.js"
    server_process = subprocess.Popen(server_command, shell=True, cwd="../../A1", text=True)

    # Allow time for the server to start (adjust as needed)
    time.sleep(5)

    # Navigate to the client directory and start npm
    print("Starting client...")
    client_command = "npm start"
    client_return_code = run_command(client_command, cwd="../../A1/client")
    
    # Wait for the client to finish or timeout
    time.sleep(10)  # Adjust this depending on how long the client takes

    # If the server process is still running, terminate it
    if server_process.poll() is None:
        server_process.terminate()

    return client_return_code

if __name__ == "__main__":
    if run_tests() == 0:
        print("Test passed successfully!")
    else:
        print("Test failed.")
