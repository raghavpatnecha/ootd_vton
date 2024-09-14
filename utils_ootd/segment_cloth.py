import numpy as np
import cv2
from PIL import Image, ImageDraw
from transformers import pipeline
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
sys.path.insert(0, str(PROJECT_ROOT))

#Initialize segmentation pipeline
#segmenter = pipeline(
#    task="image-segmentation",
#    model="./segformer_b2_clothes"
#)
segmenter = pipeline(model="mattmdjaga/segformer_b2_clothes")
def detect_face(img):
    # Convert PIL Image to cv2 format
    img_cv = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)

    # Load the pre-trained face detection model
    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    # Detect faces
    faces = face_cascade.detectMultiScale(img_cv, 1.1, 4)

    if len(faces) == 0:
        return None

    # Return the first detected face
    (x, y, w, h) = faces[0]
    return (x, y, x + w, y + h)

def remove_face(img, mask):
    face = detect_face(img)

    if face is None:
        return mask

    x1, y1, x2, y2 = face
    w, h = x2 - x1, y2 - y1

    face_locations = [
        (x1 - w * 0.1, y1 - h * 0.1),
        (x2 + w * 0.1, y2 + h * 0.1)
    ]

    ImageDraw.Draw(mask).rectangle(face_locations, fill=0)
    return mask

def segment_clothing(original_img, include_face=True, segment_type='upperclothes'):
    img = original_img.convert("RGBA")  # Ensure the image has an alpha channel
    segments = segmenter(img)

    # Define segment types
    segment_dict = {
        'upperclothes': ["Upper-clothes"],
        'torso': ["Upper-clothes", "Dress", "Belt", "Face", "Left-arm", "Right-arm"],
        'clothing': ["Hat", "Upper-clothes", "Skirt", "Pants", "Dress", "Belt", "Left-shoe", "Right-shoe", "Scarf"],
        'dress': ["Dress"],
        'lowerclothes': ["Skirt", "Pants", "Left-shoe", "Right-shoe"]
    }

    # Get the segments to include based on the segment_type
    segment_include = segment_dict.get(segment_type, segment_dict['upperclothes'])

    # Create mask list for the specified segment type
    mask_list = [s['mask'] for s in segments if s['label'] in segment_include]

    # Combine masks and create final mask
    if mask_list:
        final_mask = np.sum(mask_list, axis=0)
        final_mask = Image.fromarray((final_mask > 0).astype(np.uint8) * 255)
    else:
        final_mask = Image.new('L', img.size, 0)  # Create a black mask if no segments found

    if not include_face:
        final_mask = remove_face(img, final_mask)

    # Create an image showing only the clothing with transparent background
    clothing_image = Image.new("RGBA", img.size, (0, 0, 0, 0))  # Fully transparent background
    clothing_image.paste(img, mask=final_mask.convert("L"))  # Apply mask to the original image to remove the background

    return clothing_image

# # Example usage
# if __name__ == "__main__":
#     original_img = Image.open('downloaded_image.jpg')  # Replace with your image path
#     clothing_image = segment_clothing(original_img, include_face=False, segment_type='upperclothes')
#     clothing_image.save('clothing_image_transparent.png')  # Save as PNG with transparent background
