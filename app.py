import imghdr
import uuid
from flask import Flask, render_template, request, jsonify, send_file,url_for
from PIL import Image
import os
import tempfile
import mimetypes
from utils_ootd.cloth_difussion import process_hd, load_models
import time
import requests
from utils_ootd.download_garment import download_image,get_image_url_from_myntra
from utils_ootd.segment_cloth import segment_clothing  # Import your segmentation module
import json
app = Flask(__name__)

# Load models at startup
device, openpose_model_hd, parsing_model_hd, ootd_model_hd = load_models()

def save_upload_file(file):
    file_ext = os.path.splitext(file.filename)[1]
    if not file_ext:
        mime_type = file.content_type
        file_ext = mimetypes.guess_extension(mime_type) or '.jpg'

    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        file.save(temp_file.name)
        return temp_file.name



def wait_for_file(file_path, retries=5, delay=1):
    for _ in range(retries):
        if os.path.isfile(file_path):
            return True
        time.sleep(delay)
    return False


def process_image(vton_img_path, garment_img_path):
    try:
        garment_img = Image.open(garment_img_path)
        segmented_garment_img = segment_clothing(garment_img, include_face=False, segment_type='upperclothes')
        # Save the segmented garment image
        segmented_garment_path = f'static/segmented_{os.path.basename(garment_img_path)}'
        segmented_garment_img.save(segmented_garment_path)
        images = process_hd(
            vton_img_path=vton_img_path,
            garm_img_path=garment_img_path,
            device=device,
            openpose_model_hd=openpose_model_hd,
            parsing_model_hd=parsing_model_hd,
            ootd_model_hd=ootd_model_hd,
            category=0,
            n_samples=1,
            n_steps=20,
            image_scale=2.0,
            seed=-1
        )

        output_path = f'static/output_{os.path.basename(vton_img_path)}.png'
        images[0].save(output_path)

        # Ensure the output file is saved and accessible
        if not os.path.exists(output_path):
            raise Exception(f"Output file {output_path} not created")
            # Wait for the file to be available
        if not wait_for_file(output_path):
            raise Exception(f"Output file {output_path} not created")

        # Remove the temporary files after processing
        os.remove(vton_img_path)
        #os.remove(garment_img_path)
        os.remove(segmented_garment_path)

        return output_path
    except Exception as e:
        app.logger.error(f"Error processing image: {str(e)}")
        return None



@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process', methods=['POST'])
def process():
    try:
        vton_img_file = request.files['vton_img']
        garment_img_url = request.form['garment_img_url']
        garment_temp_url = get_image_url_from_myntra(garment_img_url)

        # Save vton image
        vton_temp_path = save_upload_file(vton_img_file)

        # Save garment image to the static directory
        garment_filename = 'garment_image.png'  # Or use a unique name
        garment_temp_path = os.path.join('static', garment_filename)

        # Download garment image
        if download_image(garment_temp_url, garment_temp_path):
            print("Image downloaded and saved to static folder")

            # Return the garment image path to show in the slider
            garment_url = url_for('static', filename=garment_filename)

            # Process the image
            result_path = process_image(vton_temp_path, garment_temp_path)

            return jsonify({"garment_image": garment_url, "result": result_path}), 200
        else:
            return jsonify({"error": "Failed to download garment image"}), 500

    except Exception as e:
        app.logger.error(f"Error in /process: {str(e)}")
        return jsonify({"error": str(e)}), 500

def process_image_other(image_path, operation):
    if operation == 'upscale':
        API_URL = "https://YOURURL.ngrok-free.app/upscale-image/" # replace with your ngrok URL
    elif operation == 'expand':
        API_URL = "https://YOURURL.ngrok-free.app/process-image/"
    else:
        raise ValueError("Invalid operation")

    try:
        with open(image_path, 'rb') as img_file:
            files = {'file': (os.path.basename(image_path), img_file, 'image/jpeg')}

            if operation == 'expand':
                params = {
                    "prompt": "A man stands confidently in a vibrant café with a modern interior. The background includes decorative items, illuminated by warm lighting. The atmosphere is lively and inviting. The background features a stylish interior with floral wallpaper, green plant decor, and soft seating, ",
                    "negative_prompt": "",
                    "direction": "right",
                    "inpaint_mask_color": 50,
                    "expand_pixels": 256,
                    "times_to_expand": 4
                }
                data = {"params": json.dumps(params)}
                response = requests.post(API_URL, files=files, data=data)
            else:
                response = requests.post(API_URL, files=files)

        if response.status_code == 200:
            unique_filename = f"{operation}_{uuid.uuid4().hex}.png"
            processed_image_path = os.path.join('static', 'results', unique_filename)
            os.makedirs(os.path.dirname(processed_image_path), exist_ok=True)
            with open(processed_image_path, 'wb') as f:
                f.write(response.content)
            return processed_image_path
        else:
            raise Exception(f"API request failed with status code {response.status_code}")
    except Exception as e:
        app.logger.error(f"Error in process_image: {str(e)}")
        raise


@app.route('/operations', methods=['POST'])
def operations():
    try:
        if 'file' not in request.files:
            raise ValueError("No file part in the request")
        file = request.files['file']
        operation = request.form.get('operation')
        if file.filename == '':
            raise ValueError("No selected file")
        if file and operation:
            file_content = file.read()
            img_type = imghdr.what(None, h=file_content)
            if img_type not in ['jpeg', 'png']:
                raise ValueError(f"Unsupported image type: {img_type}")
            temp_filename = f"temp_{uuid.uuid4().hex}.{img_type}"
            temp_path = os.path.join('static', 'temp', temp_filename)
            os.makedirs(os.path.dirname(temp_path), exist_ok=True)
            with open(temp_path, 'wb') as f:
                f.write(file_content)
            try:
                processed_image_path = process_image_other(temp_path, operation)
                if not os.path.exists(processed_image_path):
                    raise Exception(f"Processed image {processed_image_path} not created")
                return jsonify(
                    {"processed_image": url_for('static',
                                                filename=os.path.relpath(processed_image_path, 'static').replace('\\',
                                                                                                                 '/'))}), 200
            finally:
                if os.path.exists(temp_path):
                    os.remove(temp_path)
    except Exception as e:
        app.logger.error(f"Error in /process_image_other: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/result/<path:result_path>')
def result(result_path):
    try:
        if not os.path.isfile(result_path):
            raise FileNotFoundError(f"File {result_path} does not exist")
        return send_file(result_path, mimetype='image/png')
    except Exception as e:
        app.logger.error(f"Error in /result: {str(e)}")
        return jsonify({"error": str(e)}), 500



if __name__ == "__main__":
    app.run(debug=False)