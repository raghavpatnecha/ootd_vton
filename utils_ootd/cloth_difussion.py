import sys
from pathlib import Path
import argparse
from PIL import Image
import torch
import spaces
from utils_ootd.utils_ootd import get_mask_location  # Assuming this function is defined for mask handling
torch.cuda.empty_cache()
# Adding project root to sys.path to ensure imports work
PROJECT_ROOT = Path(__file__).absolute().parents[1].absolute()
sys.path.insert(0, str(PROJECT_ROOT))
# Importing required modules from the project
from preprocess.openpose.run_openpose import OpenPose
from preprocess.humanparsing.run_parsing import Parsing
from ootd.inference_ootd_hd import OOTDiffusionHD



def load_models(gpu_id=0):
    device = torch.device(f'cuda:{gpu_id}' if torch.cuda.is_available() else 'cpu')
    print(f'Using device: {device}')

    openpose_model_hd = OpenPose(gpu_id)
    parsing_model_hd = Parsing(gpu_id)
    ootd_model_hd = OOTDiffusionHD(gpu_id)

    # Move models to the correct device
    openpose_model_hd.preprocessor.body_estimation.model.to(device)
    ootd_model_hd.pipe.to(device)
    ootd_model_hd.image_encoder.to(device)
    ootd_model_hd.text_encoder.to(device)

    return device, openpose_model_hd, parsing_model_hd, ootd_model_hd

@spaces.GPU
def process_hd(vton_img_path, garm_img_path, device, openpose_model_hd, parsing_model_hd, ootd_model_hd ,category, n_samples, n_steps, image_scale, seed):
    try:
        with torch.no_grad():
            # Ensure models are on the correct device
            openpose_model_hd.preprocessor.body_estimation.model.to(device)
            ootd_model_hd.pipe.to(device)
            ootd_model_hd.image_encoder.to(device)
            ootd_model_hd.text_encoder.to(device)
            # Open images and resize once
            vton_img = Image.open(vton_img_path).resize((768, 1024))
            garm_img = Image.open(garm_img_path).resize((768, 1024))

            # Generate keypoints and parsing results
            vton_img_resized = vton_img.resize((384, 512))
            keypoints = openpose_model_hd(vton_img_resized)
            model_parse, _ = parsing_model_hd(vton_img_resized)

            # Get mask for the region of interest
            mask, mask_gray = get_mask_location('hd', ['upper_body', 'lower_body', 'dresses'][category], model_parse, keypoints)
            mask = mask.resize((768, 1024), Image.NEAREST)
            mask_gray = mask_gray.resize((768, 1024), Image.NEAREST)

            # Apply the mask to the model image
            masked_vton_img = Image.composite(mask_gray, vton_img, mask)

            # Generate the final images using diffusion model
            images = ootd_model_hd(
                model_type='hd',
                category=['upperbody', 'lowerbody', 'dress'][category],
                image_garm=garm_img,
                image_vton=masked_vton_img,
                mask=mask,
                image_ori=vton_img,
                num_samples=n_samples,
                num_steps=n_steps,
                image_scale=image_scale,
                seed=seed,
            )

        return images
    except Exception as e:
        print(f"Error during processing: {e}")
        return None

