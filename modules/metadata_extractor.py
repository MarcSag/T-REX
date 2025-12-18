import json
import os
from pathlib import Path

# List of selected fields to extract
SELECTED_FIELDS = [
    "MagneticFieldStrength",
    "ImagingFrequency",
    "Manufacturer",
    "ManufacturersModelName",
    "BodyPartExamined",
    "MRAcquisitionType",
    "SeriesDescription",
    "ProtocolName",
    "ScanningSequence",
    "SequenceVariant",
    "ScanOptions",
    "SeriesNumber",
    "SliceThickness",
    "SpacingBetweenSlices",
    "EchoTime",
    "RepetitionTime",
    "FlipAngle",
    "EchoTrainLength",
    "PhaseEncodingSteps",
    "AcquisitionMatrixPE",
    "PixelBandwidth",
    "InPlanePhaseEncodingDirectionDICOM",
    "NumberOfAverages",
    "EchoNumber",
    "InversionTime"
]

def extract_metadata(nii_path, json_path):
    """
    Extracts metadata from the associated JSON file.
    Returns a dictionary containing:
        - 'Image': Name of the NIfTI file
        - The selected metadata fields (set to None if missing).
    """
    result = {}

    # Add the image name to the result
    result["Image"] = os.path.basename(nii_path)

    # If the JSON file does not exist, populate the fields with None
    if json_path is None or not os.path.exists(json_path):
        print(f"Warning: JSON metadata file not found for {nii_path}.")
        for field in SELECTED_FIELDS:
            result[field] = None
        return result

    # Attempt to load the JSON file
    try:
        with open(json_path, "r") as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error: Could not read JSON file {json_path}: {e}")
        for field in SELECTED_FIELDS:
            result[field] = None
        return result

    # Extract the selected metadata fields
    for field in SELECTED_FIELDS:
        result[field] = data.get(field, None)

    return result

def save_metadata(metadata, output_dir):
    """
    Saves the extracted metadata into a JSON file in the specified output directory.
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Define the output JSON file path
    output_file = output_dir / "extracted_metadata.json"

    try:
        with open(output_file, "w") as f:
            json.dump(metadata, f, indent=4)
        print(f"Metadata saved to {output_file}")
    except Exception as e:
        print(f"Error: Could not save metadata to {output_file}: {e}")

# Example usage
if __name__ == "__main__":
    # Paths to the NIfTI and JSON files (for testing)
    nii_path = "example_image.nii"
    json_path = "example_image.json"
    output_dir = "output_metadata"

    # Extract metadata and save it
    metadata = extract_metadata(nii_path, json_path)
    save_metadata(metadata, output_dir)