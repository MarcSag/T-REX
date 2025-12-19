import argparse
from pathlib import Path
import shutil

# Import necessary modules for pipeline steps
from modules.dicom_nii_converter import convert_dicom_to_nifti
from modules.metadata_extractor import extract_metadata, save_metadata
from modules.brain_extractor import perform_brain_extraction
from modules.atlas_register import register_atlas
from modules.radiomics_extractor import process_radiomics, atlas_based_radiomics

def parse_bool_option(option):
    if option.lower() == "no":
        return False
    elif option.lower() == "yes":
        return True
    else:
        raise ValueError(f"[ERROR] Invalid option '{option}': must be 'yes' or 'no'.")

def validate_and_adjust_args(args):
    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"[ERROR] The input file '{args.input}' does not exist.")
    if [suffix.lower() for suffix in input_path.suffixes] not in [['.nii'], ['.nii', '.gz'], ['.dcm']]:
        raise ValueError("[ERROR] Input must be a NIfTI (.nii or .nii.gz) or DICOM (.dcm) file.")

    if not args.bet and args.register:
        print("[WARNING] --register has been automatically disabled because --bet is set to no.")
        args.register = False

    if args.roi != "no":
        if not isinstance(args.roi, list):
            raise ValueError("[ERROR] --roi must be a list of NIfTI mask paths or 'no'.")
        for roi in args.roi:
            roi_path = Path(roi)
            if not roi_path.exists():
                raise FileNotFoundError(f"[ERROR] ROI file '{roi}' not found.")
            if roi_path.suffix not in ['.nii', '.nii.gz']:
                raise ValueError(f"[ERROR] ROI file '{roi}' must be a valid NIfTI file.")

def check_dependency(cmd, name):
    if not shutil.which(cmd):
        raise EnvironmentError(f"[ERROR] Dependency '{name}' is missing. Install it first.")

def merge_radiomics_outputs(output_dir, output_csv, metadata_json):
    """
    Combines multiple radiomics CSV files into one final CSV, assigns explicit `Source` labels,
    and integrates metadata. Columns are reordered.

    Args:
        output_dir: Directory containing intermediate CSV files (e.g., brain_radiomics.csv, atlas CSV, etc.).
        output_csv: Path to the final combined output CSV.
        metadata_json: Path to the JSON file containing metadata to add.

    Returns:
        None: Saves the combined CSV to `output_csv`.
    """
    import pandas as pd

    # Define mappings for source column
    SOURCE_MAP = {
        "brain_radiomics": "brain_mask",
        "radiomics_features": "atlas",
    }

    csv_files = list(output_dir.glob("*.csv"))
    combined_data = pd.concat(
        pd.read_csv(csv_file).assign(Source=SOURCE_MAP.get(csv_file.stem, "input_roi"))  # Default is `input_roi`
        for csv_file in csv_files
    )

    # Add Image column with the image name
    image_name = Path(output_csv).stem.replace("_results", "")  # Get image name without `_results`
    combined_data["Image"] = image_name

    # Check and reset indices to ensure uniqueness
    combined_data = combined_data.reset_index(drop=True)

    # Load metadata
    metadata = pd.read_json(metadata_json, orient="index").T  # Transpose metadata into DataFrame rows
    metadata = pd.concat([metadata] * len(combined_data), ignore_index=True)  # Repeat metadata for each row
    metadata = metadata.reset_index(drop=True)

    # Concatenate combined data and metadata
    combined_data = pd.concat([combined_data, metadata], axis=1)

    # Reorganize columns
    cols = ["Image", "Source", "region_name"]  # Mandatory columns
    metadata_cols = [col for col in metadata.columns if col not in cols]  # Metadata columns
    radiomics_cols = [col for col in combined_data.columns if col.startswith("original")]
    final_col_order = cols + metadata_cols + radiomics_cols

    # Reorder dataframe
    combined_data = combined_data[final_col_order]

    # Save combined data
    combined_data.to_csv(output_csv, index=False)
    print(f"[INFO] Combined radiomics features (with metadata) saved to {output_csv}")

def main():
    check_dependency("flirt", "FSL FLIRT")
    check_dependency("antsRegistration", "ANTs tools")

    parser = argparse.ArgumentParser(description="T-REX: The Radiomics Extractor")
    parser.add_argument("--input", type=str, required=True)
    parser.add_argument("--output", type=str, required=True)
    parser.add_argument("--roi", nargs="*", default="no")
    parser.add_argument("--metadata", type=str, default="yes")
    parser.add_argument("--bet", type=str, default="yes")
    parser.add_argument("--register", type=str, default="yes")
    parser.add_argument("--radiomics", type=str, default="yes")

    args = parser.parse_args()

    args.metadata = parse_bool_option(args.metadata)
    args.bet = parse_bool_option(args.bet)
    args.register = parse_bool_option(args.register)
    args.radiomics = parse_bool_option(args.radiomics)

    validate_and_adjust_args(args)

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)

    nifti_image = None
    json_path = None
    
    if args.input.endswith('.dcm'):
        nifti_image, json_path = convert_dicom_to_nifti(args.input, output_dir)
    else:
        nifti_image = Path(args.input)
        json_path = nifti_image.with_suffix("").with_suffix(".json")
        # print(f"[DEBUG] Generated JSON path: {json_path}")  # Debug
    
    # Check if JSON metadata file exists
    # print(f"[DEBUG] Checking for JSON metadata file at path: {json_path}")
    if not json_path.exists():
        print(f"[WARNING] JSON metadata file not found for {args.input}. Expected path: {json_path}")
    else:
        print("[INFO] JSON metadata file found.")

    if args.metadata:
        metadata = extract_metadata(nifti_image, json_path)
        save_metadata(metadata, output_dir)

    brain_mask = None
    if args.bet:
        brain_mask = perform_brain_extraction(nifti_image, output_dir)

    registered_template, registered_atlas = None, None
    if args.register:
        registered_template, registered_atlas = register_atlas(nifti_image, brain_mask, output_dir)

    if args.radiomics:
        output_csv = output_dir / "radiomics_features.csv"

        # 1. Process brain mask separately
        if brain_mask:
            process_radiomics(
                nifti_image, 
                [brain_mask],  # Single-item list for this mask
                output_dir / "brain_radiomics.csv"  # Save these features in a separate file
            )

        # 2. Process atlas regions if registration is active
        rois = []
        if args.roi != "no":
            rois.extend(args.roi)

        if args.register and registered_atlas:
            atlas_based_radiomics(
                nifti_image,
                registered_atlas,
                labels_path="atlas/atlas_anat_labels.csv",
                output_csv=output_csv
            )
        elif rois:
            process_radiomics(nifti_image, rois, output_csv)
        else:
            raise ValueError("[ERROR] No suitable ROIs found for radiomics extraction.")

        # 3. Combine results and include metadata
        image_name = Path(args.input).with_suffix("").with_suffix("").stem
        metadata_json = output_dir / "extracted_metadata.json"
        final_csv = output_dir / f"{image_name}_results.csv"
        merge_radiomics_outputs(output_dir, final_csv, metadata_json)

        # Optional: Clean up temporary files
        for tmp_file in output_dir.glob("*.csv"):
            if tmp_file.stem != f"{image_name}_results":
                tmp_file.unlink()  # Delete intermediate files

    print(f"[INFO] Pipeline completed successfully. Results saved to {final_csv}")

if __name__ == "__main__":
    main()