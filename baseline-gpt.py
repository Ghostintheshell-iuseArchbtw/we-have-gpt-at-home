import requests
import json

# Local LLM server URL and port
server_url = 'http://192.168.1.155:2333/v1/chat/completions'  ##### YOUR LMSTUDIO IPADDRESS AND PORT HERE #########

def make_inference_request(prompt):
    # Request payload
    payload = {
        "messages": [
            {"role": "system", "content": "You are my AI Assistant."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 150,  # Limit max tokens for response
        "stream": True
    }

    try:
        with requests.post(server_url, json=payload, headers={"Content-Type": "application/json"}, stream=True) as response:
            if response.status_code != 200:
                print(f"Error: Received status code {response.status_code}")
                return)

            print()  # Ensure the prompt returns to the new line after the response is completed

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Welcome to the Local LLM Chat!")
    print("Type 'exit' to end the conversation.")

    while True:
        prompt = input("You: ")
        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":
    main()

        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":
    main()

            print("GPT: ", end='', flush=True)  # Start the GPT response line

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
                                    print(delta_content, end='', flush=True)
                    except json.JSONDecodeError:
                        print(f"Non-JSON response: {line_str}")
)

            print()  # Ensure the prompt returns to the new line after the response is completed

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Welcome to the Local LLM Chat!")
    print("Type 'exit' to end the conversation.")

    while True:
        prompt = input("You: ")
        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":
    main()

        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":)

            print()  # Ensure the prompt returns to the new line after the response is completed

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Welcome to the Local LLM Chat!")
    print("Type 'exit' to end the conversation.")

    while True:
        prompt = input("You: ")
        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":
    main()

        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":
    main()
    main()
            print()  # Ensure the prompt returns to the new line after the response is completed

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    print("Welcome to the Local LLM Chat!")
    print("Type 'exit' to end the conversation.")

    while True:
        prompt = input("You: ")
        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":
    main()

        if prompt.lower() == 'exit':
            break
        make_inference_request(prompt)

if __name__ == "__main__":
    main()
