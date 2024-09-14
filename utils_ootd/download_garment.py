import requests
from bs4 import BeautifulSoup
import json
import os

def get_image_url_from_myntra(product_url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    try:
        response = requests.get(product_url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        scripts = soup.find_all('script')

        for script in scripts:
            if script.string and 'pdpData' in script.string:
                data = json.loads(script.string.split('=', 1)[1].strip().rstrip(';'))
                image_url = data["pdpData"]["media"]["albums"][0]["images"][0]["imageURL"]
                return image_url

        raise ValueError("Image URL not found in the product page")
    except Exception as e:
        print(f"Error fetching image URL: {e}")
        return None




def download_image(url, output_filename):
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()  # Check for HTTP request errors

        # Check if the output path directory exists
        output_dir = os.path.dirname(output_filename)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        with open(output_filename, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)

        # Confirm the file is saved and report file size
        if os.path.isfile(output_filename):
            file_size = os.path.getsize(output_filename)
            print(f"Image downloaded and saved to {output_filename}, size: {file_size} bytes")
            return True
        else:
            print(f"Image file not saved at {output_filename}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Error downloading image: {e}")
        return False
