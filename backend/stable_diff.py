import requests

# Replace with your model's API URL
API_URL = "https://huggingface.co/xue089/stable_diffusion_pixelart4/tree/main"
# Replace with your Hugging Face API token
headers = {"Authorization": "Bearer YOUR_HUGGINGFACE_API_TOKEN"}

def query(payload):
    response = requests.post(API_URL, headers=headers, json=payload)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return None

if __name__ == "__main__":
    # Define your prompt here
    prompt = "A fantasy landscape with mountains and a river at sunset"

    # Prepare the payload
    payload = {
        "inputs": prompt,
        # You can include additional parameters if your model supports them
        "options": {"wait_for_model": True}  # This waits for the model to be ready
    }

    # Query the model
    output = query(payload)

    # Save the output image if successful
    if output:
        with open("output.png", "wb") as f:
            f.write(output)
        print("Image generated and saved as output.png")
    else:
        print("Failed to generate image.")
