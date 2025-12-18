import os
import subprocess
import tempfile
import shutil
from pathlib import Path

def run_dcm2niix(input_path, output_dir):
    """
    Run dcm2niix on the provided DICOM path.
    Returns the paths of the generated .nii.gz and .json files.
    """
    command = [
        "dcm2niix",
        "-z", "y",            # Compress the NIfTI file into .nii.gz
        "-o", output_dir,     # Output folder
        "-f", "%p_%s",        # Output file name pattern: Protocol_SeriesNumber
        input_path            # Input DICOM folder or file
    ]

    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(result.stdout.decode())  # Display output for debugging if needed
    except FileNotFoundError:
        raise RuntimeError(
            "dcm2niix is not installed or not found in PATH. "
            "Install it using: sudo apt install dcm2niix OR conda install -c conda-forge dcm2niix."
        )
    except subprocess.CalledProcessError as e:
        raise RuntimeError(f"dcm2niix failed to run: {e.stderr.decode()}")

    # Search for generated files in the output directory
    nii_file = json_file = None
    for f in os.listdir(output_dir):
        full_path = os.path.join(output_dir, f)
        if f.endswith(".nii") or f.endswith(".nii.gz"):
            nii_file = full_path
        elif f.endswith(".json"):
            json_file = full_path

    if nii_file is None:
        raise RuntimeError("dcm2niix did not produce a NIfTI file. Check your DICOM input.")

    return nii_file, json_file


def convert_dicom_to_nifti(input_path, output_dir=None):
    """
    Converts a DICOM series (directory or single file) to NIfTI format.
    If no `output_dir` is provided, a temporary directory is used.
    Returns: Tuple of paths (nii_path, json_path).
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"The provided DICOM input path does not exist: {input_path}")

    # If the input is a single DICOM file, copy it to a temporary directory
    cleanup_temp = False
    dicom_folder = input_path

    if os.path.isfile(input_path):
        temp_dir = tempfile.mkdtemp(prefix="dicom_")
        shutil.copy(input_path, os.path.join(temp_dir, os.path.basename(input_path)))
        dicom_folder = temp_dir
        cleanup_temp = True

    # Create an output directory if not provided
    if output_dir is None:
        output_dir = tempfile.mkdtemp(prefix="dcm2niix_output_")
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    try:
        nii_path, json_path = run_dcm2niix(dicom_folder, str(output_dir))
        print(f"Conversion successful!\nNIfTI file: {nii_path}\nJSON file: {json_path}")
        return nii_path, json_path
    finally:
        # Clean up temporary folder if the input was a single DICOM file
        if cleanup_temp:
            shutil.rmtree(dicom_folder, ignore_errors=True)