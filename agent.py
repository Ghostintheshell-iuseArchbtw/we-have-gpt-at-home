import requests
import json
import sys
import datetime
import subprocess
import platform
import psutil
from bs4 import BeautifulSoup

# Local LLM server URL and port
SERVER_URL = 'http://192.168.1.187:9003/v1/chat/completions'

# Google search URL
GOOGLE_SEARCH_URL = 'https://www.google.com/search'

# Initialize chat history
chat_history = []

def make_inference_request(prompt):
    """
    Send a request to the local LLM server with the user's input prompt.

    Args:
        prompt (str): The user's input prompt.

    Returns:
        None
    """
    # Add the new user message to the chat history
    chat_history.append({"role": "user", "content": prompt})

    # Request payload
    payload = {
        "messages": chat_history,
        "temperature": 0.7,
        "max_tokens": 150,  # Adjust as needed
        "stream": True
    }

    try:
        with requests.post(SERVER_URL, json=payload, headers={"Content-Type": "application/json"}, stream=True) as response:
            if response.status_code != 200:
                print(f"\nError: Received status code {response.status_code}\n")
                return

            sys.stdout.write("GPT: ")  # Start the GPT response line
            sys.stdout.flush()

            full_response = ""
            for line in response.iter_lines():
                if line:
                    line_str = line.decode('utf-8').strip()
                    if line_str.startswith('data: '):
                        line_str = line_str[len('data: '):]
                    if line_str == '[DONE]':
                        break
                    try:
                        response_json = json.loads(line_str)
                        if 'choices' in response_json:
                            for choice in response_json['choices']:
                                if 'delta' in choice:
                                    delta_content = choice['delta'].get('content', '')
                                    sys.stdout.write(delta_content)
                                    sys.stdout.flush()
                                    full_response += delta_content
                    except json.JSONDecodeError:
                        print(f"\nNon-JSON response: {line_str}\n")

            chat_history.append({"role": "assistant", "content": full_response})
            print()  # Ensure prompt returns to the new line after the response is completed
    except Exception as e:
        print(f"\nAn error occurred: {e}\n")


def search_web(query):
    """
    Perform a web search using Google and print the results.

    Args:
        query (str): The search query.

    Returns:
        None
    """
    search_url = f"{GOOGLE_SEARCH_URL}?q={query}"
    headers = {"User-Agent": "Mozilla/5.0"}

    try:
        response = requests.get(search_url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            results = soup.find_all('div', class_='BNeawe vvjwJb AP7Wnd')
            urls = soup.find_all('a', href=True)
            print("\nSearch Results:")
            for i, result in enumerate(results[:5], 1):  # Display only first 5 results
                title = result.get_text()
                url = urls[i]['href']
                print(f"{i}. {title}: {url}")
            print()  # Blank line after search results
        else:
            print(f"\nError: Received status code {response.status_code}\n")
    except Exception as e:
        print(f"\nAn error occurred during the web search: {e}\n")


def get_current_time():
    """
    Get the current time.

    Returns:
        str: The current time in the format HH:MM:SS.
    """
    return datetime.datetime.now().strftime("%H:%M:%S")


def get_current_date():
    """
    Get the current date.

    Returns:
        str: The current date in the format YYYY-MM-DD.
    """
    return datetime.datetime.now().strftime("%Y-%m-%d")


def execute_command(command):
    """
    Execute a terminal command and print the output.

    Args:
        command (str): The command to execute.

    Returns:
        None
    """
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        print(f"\nCommand Output:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        print(f"\nError: Command failed with return code {e.returncode}\n{e.stderr}")
    except Exception as e:
        print(f"\nAn error occurred while executing the command: {e}\n")


def get_system_info():
    """
    Get system information.

    Returns:
        str: System information.
    """
    system_info = ""
    system_info += f"System: {platform.system()}\n"
    system_info += f"Release: {platform.release()}\n"
    system_info += f"Version: {platform.version()}\n"
    system_info += f"Machine: {platform.machine()}\n"
    system_info += f"Processor: {platform.processor()}\n"
    return system_info


def get_process_info():
    """
    Get process information.

    Returns:
        str: Process information.
    """
    process_info = ""
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            process_info += f"PID: {proc.info['pid']}, Name: {proc.info['name']}\n"
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return process_info


def get_disk_info():
    """
    Get disk information.

    Returns:
        str: Disk information.
    """
    disk_info = ""
    disk_info += f"Total Memory: {psutil.virtual_memory().total / (1024.0 ** 3):.2f} GB\n"
    disk_info += f"Available Memory: {psutil.virtual_memory().available / (1024.0 ** 3):.2f} GB\n"
    disk_info += f"Used Memory: {psutil.virtual_memory().used / (1024.0 ** 3):.2f} GB\n"
    disk_info += f"Memory Percentage: {psutil.virtual_memory().percent}%\n"
    return disk_info


def get_cpu_info():
    """
    Get CPU information.

    Returns:
        str: CPU information.
    """
    cpu_info = ""
    cpu_info += f"CPU Count: {psutil.cpu_count()}\n"
    cpu_info += f"CPU Frequency: {psutil.cpu_freq().current / 1000.0} GHz\n"
    cpu_info += f"CPU Usage: {psutil.cpu_percent()}%\n"
    return cpu_info


def main():
    print("Welcome to the Local LLM Chat!")
    print("Type 'search:<query>' to perform a web search.")
    print("Type 'time' to get the current time.")
    print("Type 'date' to get the current date.")
    print("Type 'cmd:<command>' to execute a terminal command.")
    print("Type 'system' to get system information.")
    print("Type 'processes' to get process information.")
    print("Type 'disk' to get disk information.")
    print("Type 'cpu' to get CPU information.")
    print("Type 'exit' to end the conversation.\n")

    while True:
        prompt = input("You: ")

        if prompt.lower() == 'exit':
            print("\nGoodbye!\n")
            break
        elif prompt.startswith("search:"):
            query = prompt[len("search:"):].strip()
            if query:
                search_web(query)
            else:
                print("\nPlease provide a search query after 'search:'.\n")
        elif prompt.lower() == 'time':
            print(f"\nThe current time is: {get_current_time()}\n")
        elif prompt.lower() == 'date':
            print(f"\nThe current date is: {get_current_date()}\n")
        elif prompt.startswith("cmd:"):
            command = prompt[len("cmd:"):].strip()
            if command:
                execute_command(command)
            else:
                print("\nPlease provide a command after 'cmd:'.\n")
        elif prompt.lower() == 'system':
            print(f"\nSystem Information:\n{get_system_info()}\n")
        elif prompt.lower() == 'processes':
            print(f"\nProcess Information:\n{get_process_info()}\n")
        elif prompt.lower() == 'disk':
            print(f"\nDisk Information:\n{get_disk_info()}\n")
        elif prompt.lower() == 'cpu':
            print(f"\nCPU Information:\n{get_cpu_info()}\n")
        else:
            print("\nCommand not recognized. Please try again.\n")

if __name__ == "__main__":
    main()
