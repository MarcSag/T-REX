import os
from pathlib import Path
import ants
from nipype.interfaces import fsl

def register_atlas(nifti_file, bet_file, output_dir):
    """
    Registers the template and atlas to the given BET image (brain-extracted).
    Saves the registered template and atlas in the specified output directory.

    Parameters:
    - nifti_file: Path to the original NIfTI image (input image file).
    - bet_file: Path to the BET (brain-extracted) image, used as the reference.
    - output_dir: Directory where the registered outputs (template and atlas) will be saved.

    Returns:
    - tuple(template_out, atlas_out): Paths to the registered template and atlas.
    """
    # Define paths for the atlas and template
    atlas_dir = Path(__file__).resolve().parent.parent / "atlas"
    atlas_path = atlas_dir / "atlas_anat.nii.gz"
    template_path = atlas_dir / "flair_template_miplab-ncct_sym.nii.gz"

    # Validate necessary files
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")
    if not atlas_path.exists():
        raise FileNotFoundError(f"Atlas file not found: {atlas_path}")
    if not Path(bet_file).exists():
        raise FileNotFoundError(f"BET file not found: {bet_file}")

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[INFO] Performing registration for {nifti_file}...")

    # Temporary folder for intermediate files
    tmp_folder = output_dir / "tmp"
    tmp_folder.mkdir(exist_ok=True)

    # Get the base name of the NIfTI file without extensions (.nii.gz or .gz)
    base_name = Path(nifti_file).with_suffix("").with_suffix("").name

    # Step 1: FLIRT registration (template -> BET)
    flirt = fsl.FLIRT()
    flirt.inputs.in_file = str(template_path)
    flirt.inputs.reference = str(bet_file)
    flirt.inputs.out_file = str(tmp_folder / "flirt_template.nii.gz")
    flirt.inputs.out_matrix_file = str(tmp_folder / "flirt_template.mat")
    flirt.inputs.dof = 7
    flirt.inputs.bins = 256
    flirt.inputs.cost_func = "normcorr"
    flirt.inputs.searchr_x = [-180, 180]
    flirt.inputs.searchr_y = [-180, 180]
    flirt.inputs.searchr_z = [-180, 180]
    flirt.inputs.interp = "nearestneighbour"
    flirt.inputs.output_type = "NIFTI_GZ"  # Explicit output type
    flirt.run()

    # Step 2: ANTs registration (template -> BET)
    fixed = ants.image_read(str(bet_file))
    moving = ants.image_read(str(tmp_folder / "flirt_template.nii.gz"))
    reg = ants.registration(
        fixed=fixed,
        moving=moving,
        type_of_transform="SyN",
        outprefix=str(tmp_folder / "ants_")
    )
    template_out = output_dir / f"{base_name}_registered_template.nii.gz"
    reg['warpedmovout'].to_file(str(template_out))
    mytx = reg['fwdtransforms']

    # Step 3: FLIRT registration (atlas -> BET)
    applyxfm = fsl.ApplyXFM()
    applyxfm.inputs.in_file = str(atlas_path)
    applyxfm.inputs.reference = str(bet_file)
    applyxfm.inputs.in_matrix_file = str(tmp_folder / "flirt_template.mat")
    applyxfm.inputs.apply_xfm = True
    applyxfm.inputs.out_file = str(tmp_folder / "flirt_atlas.nii.gz")
    applyxfm.inputs.output_type = "NIFTI_GZ"  # Explicit output type
    applyxfm.inputs.interp = "nearestneighbour"
    applyxfm.run()

    # Step 4: ANTs registration (atlas -> BET)
    atlas_warped = ants.image_read(str(tmp_folder / "flirt_atlas.nii.gz"))
    atlas_transformed = ants.apply_transforms(
        fixed=fixed,
        moving=atlas_warped,
        transformlist=mytx,
        interpolator="nearestNeighbor"
    )
    atlas_out = output_dir / f"{base_name}_registered_atlas.nii.gz"
    atlas_transformed.to_file(str(atlas_out))

    # Clean temporary files, leaving only matrix files
    for f in tmp_folder.glob("*"):
        if not f.name.endswith(".mat"):
            f.unlink()

    print(f"[INFO] Registration completed. Results saved in {output_dir}")
    return template_out, atlas_out

# Example usage
if __name__ == "__main__":
    nifti_file = "example_image.nii.gz"
    bet_file = "example_image_bet.nii.gz"
    output_dir = "registration_output"

    template_path, atlas_path = register_atlas(nifti_file, bet_file, output_dir)
    print(f"Template registered: {template_path}")
    print(f"Atlas registered: {atlas_path}")