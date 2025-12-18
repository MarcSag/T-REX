import os
import subprocess


def run_hd_bet(input_nii, output_prefix):
    """
    Runs HD-BET to generate a brain mask.
    Returns the path to the generated mask.
    """
    output_path = output_prefix
    subprocess.run([
        "hd-bet",
        "-i", input_nii,
        "-o", output_path,
        "-tta", "0",  # Disable test-time augmentation for speed
        "-mode", "fast"  # Use fast mode for brain extraction
    ], check=True)

    mask_path = f"{output_path}_mask.nii.gz"
    if not os.path.exists(mask_path):
        raise FileNotFoundError(f"HD-BET did not generate the mask: {mask_path}")

    return mask_path


def perform_brain_extraction(input_nii, output_dir):
    """
    Public function for the T-REX pipeline.
    - This function runs HD-BET on the input NIfTI file to generate a brain mask.
    - Saves the mask in the specified output directory.

    Args:
    - input_nii: Path to the input NIfTI image.
    - output_dir: Directory where the brain mask will be saved.

    Returns:
    - mask_path: Path to the generated brain mask.
    """
    if not os.path.exists(input_nii):
        raise FileNotFoundError(f"Input NIfTI file does not exist: {input_nii}")

    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)

    # Prefix for the output files (mask will be named after input_nii)
    filename = os.path.basename(input_nii).replace(".nii.gz", "").replace(".nii", "")
    output_prefix = os.path.join(output_dir, filename + "_bet")

    # Run HD-BET
    mask_path = run_hd_bet(input_nii, output_prefix)
    print(f"Brain mask saved at: {mask_path}")

    return mask_path

# Example usage
if __name__ == "__main__":
    input_nii = "example_image.nii.gz"  # Replace with your NIfTI file path
    output_dir = "bet_output"  # Replace with your output directory
    mask = perform_brain_extraction(input_nii, output_dir)
    print(f"Generated brain mask: {mask}")