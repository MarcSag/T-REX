import pandas as pd
import numpy as np
import nibabel as nib
import SimpleITK as sitk
from radiomics import featureextractor
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed
import logging
import os
import re

logging.getLogger("radiomics").setLevel(logging.ERROR)
logging.getLogger("pyradiomics").setLevel(logging.ERROR)

def sanitize_region_name(name):
    return re.sub(r"[^\w\s-]", "_", name)  # Remplace les caractères non alphanumériques

def extract_features(image_path, mask_path=None, region_label=None, region_name=None):
    try:
        if not Path(image_path).exists():
            raise FileNotFoundError(f"[ERROR] Image file not found: {image_path}")
        image = sitk.ReadImage(str(image_path))

        if mask_path:
            if not Path(mask_path).exists():
                raise FileNotFoundError(f"[ERROR] Mask file not found: {mask_path}")
            mask = sitk.ReadImage(str(mask_path))
            mask_array = sitk.GetArrayFromImage(mask)
            if np.sum(mask_array) == 0:
                print(f"[WARNING] Mask '{mask_path}' is empty. Skipping extraction.")
                return {}
        else:
            if region_label is None:
                raise ValueError("[ERROR] Either 'mask_path' or 'region_label' must be provided.")
            if np.sum(region_label) == 0:
                print(f"[WARNING] Region '{region_name}' is empty. Skipping extraction.")
                return {}
            mask = sitk.GetImageFromArray(np.transpose(region_label, (2, 1, 0)))
            mask.CopyInformation(image)

        extractor = featureextractor.RadiomicsFeatureExtractor()
        extractor.settings['enableDiagnostics'] = False
        extractor.settings['excludeFromFeatureClass'] = ['shape']
        features = extractor.execute(image, mask)
        features = {k: v for k, v in features.items() if k.startswith("original")}

        if region_name:
            features["region_name"] = region_name

        return features

    except Exception as e:
        print(f"[ERROR] Failed to extract radiomics for region '{region_name}': {e}")
        return {}

def process_radiomics(image_path, masks, output_csv, region_definitions=None):
    rows = []
    tasks = []

    for mask_config in masks:
        if isinstance(mask_config, str):
            mask_path = Path(mask_config)
            if not mask_path.exists():
                raise FileNotFoundError(f"[ERROR] Mask file not found: {mask_path}")
            region_name = mask_path.stem
            tasks.append((image_path, mask_config, None, region_name))
        elif isinstance(mask_config, tuple):
            region_label, region_name = mask_config
            tasks.append((image_path, None, region_label, region_name))

    print(f"[INFO] Starting radiomics extraction for {len(tasks)} regions or masks.")
    max_workers = min(8, len(tasks))
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = [executor.submit(extract_features, *task) for task in tasks]
        for future in as_completed(futures):
            try:
                result = future.result()
                if result:
                    rows.append(result)
            except Exception as e:
                print(f"[ERROR] A task failed with error: {e}")

    if rows:
        df = pd.DataFrame(rows)
        useful_columns = [col for col in df.columns if not col.startswith(("diagnostics_", "general_"))]
        df = df[useful_columns]
        df.to_csv(output_csv, index=False)
        print(f"[INFO] Radiomics extraction completed. Results saved to {output_csv}")
    else:
        print("[WARNING] No features were extracted.")

    return output_csv

def atlas_based_radiomics(image_path, atlas_path, labels_path, output_csv):
    if not Path(atlas_path).exists():
        raise FileNotFoundError(f"[ERROR] The provided atlas file '{atlas_path}' does not exist.")

    if not Path(labels_path).exists():
        raise FileNotFoundError(f"[ERROR] The provided labels file '{labels_path}' does not exist.")

    atlas_nib = nib.load(str(atlas_path))
    atlas_data = atlas_nib.get_fdata().astype(int)
    try:
        atlas_labels = pd.read_csv(labels_path, header=None)
        if atlas_labels.shape[1] != 2:
            raise ValueError(f"[ERROR] Labels file '{labels_path}' must contain exactly 2 columns: [Label, Name].")
        atlas_labels.columns = ["Label", "Name"]
    except Exception as e:
        raise ValueError(f"[ERROR] Failed to read labels file '{labels_path}': {e}")

    regions = [
        ((atlas_data == label).astype(np.uint8), sanitize_region_name(name))
        for label, name in zip(atlas_labels["Label"], atlas_labels["Name"])
        if label != 0 and np.sum(atlas_data == label) > 0
    ]

    print(f"[INFO] Found {len(regions)} regions in the atlas for radiomics extraction.")
    return process_radiomics(image_path, regions, output_csv)