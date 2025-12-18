# T-REX: Template-based Radiomics Extraction Pipeline

**T-REX** (The Radiomics Extractor) est un pipeline Python modulable pour automatiser l'extraction de caractéristiques radiomiques à partir d'images médicales. Ce pipeline inclut les étapes suivantes :
- Conversion des images DICOM au format NIfTI.
- Extraction des métadonnées provenant des fichiers convertis.
- Génération de masques cérébraux avec **HD-BET**.
- Recalage et enregistrement d'atlas sur des images avec ou sans cerveau.
- Extraction de caractéristiques radiomiques basées sur des ROI personnalisées, masques cérébraux ou régions d'atlas.

---

## Fonctionnalités principales

- Automatisation complète des pipelines combinant DICOM vers NIfTI, recalage, et extraction radiomique.
- Prise en charge de multiples types de sources : DICOM ou NIfTI.
- Extraction des métadonnées des images d'entrée et enregistrement sous format `.json`.
- Segmentation cérébrale spécifique via **HD-BET** pour permettre des analyses ciblées.
- Compatibilité avec des atlas anatomiques pour délimiter des régions (e.g., lobe occipital, ventricules) et extraire automatiquement des caractéristiques radiomiques.
- Enregistrement des résultats sous format CSV contenant toutes les caractéristiques radiomiques.

---

## Prérequis

### Logiciels
- **Python ≥ 3.7**
- Logiciels externes :
  - `dcm2niix` : Conversion DICOM → NIfTI, avec extraction des métadonnées.
  - `hd-bet` : Génération de masques cérébraux.
  - [FSL FLIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FLIRT) : Outils de recalage.
  - [ANTs Registration](http://stnava.github.io/ANTs/) : Enregistrement des atlas/templates.

### Librairies Python
Assurez-vous de disposer des bibliothèques suivantes (ou installez-les via `requirements.txt`) :
- pandas
- numpy
- nibabel
- SimpleITK
- pyradiomics
- nipype
- antspyx

---

## Installation

1. Clonez ce dépôt GitHub :
   ```bash
   git clone https://github.com/votre-utilisateur/T-REX.git
   cd T-REX
   ```

2. Installez les dépendances Python :
   ```bash
   pip install -r requirements.txt
   ```

3. Assurez-vous que `dcm2niix`, `hd-bet`, et les autres logiciels nécessaires (ANTs, FSL) sont installés et accessibles via le PATH de votre système.

---

## Utilisation

### Pour exécuter le pipeline sur une image unique :

```bash
python trex.py --input <chemin_image> --output <dossier_sortie> [options]
```

#### Arguments requis :
- `<chemin_image>` : Chemin vers une image DICOM ou NIfTI.
- `<dossier_sortie>` : Répertoire où les résultats seront enregistrés.

#### Arguments optionnels (processus) :
- `--metadata` : Active l'extraction des métadonnées des images. Génère un fichier `.json`.
- `--bet` : Effectue la segmentation cérébrale via HD-BET.
- `--register` : Recalage d'un atlas/template. Nécessite `--bet`.
- `--radiomics` : Extraction de caractéristiques radiomiques (atlas, ROI, etc.).
- `--roi` : Spécifiez un ou plusieurs masques personnalisés pour des ROIs au format NIfTI.

---

### Comportement par défaut :
Si aucun argument autre que `--input` et `--output` n'est fourni, le pipeline exécutera toutes les étapes disponibles.

#### Exemple :
```bash
python trex.py --input image.dcm --output results/
```

Ce processus effectue :
1. Conversion DICOM → NIfTI.
2. Extraction des métadonnées.
3. Génération d'un masque cérébral.
4. Recalage Template/Atlas.
5. Extraction des caractéristiques radiomiques.

---

## Structure de sortie

### Organisation des fichiers de sortie

Les résultats sont enregistrés de manière structurée dans le dossier spécifié (`--output`), en fonction des étapes exécutées.

| Étape                     | Fichiers générés                                                              |
|---------------------------|------------------------------------------------------------------------------|
| **Conversion**            | `image.nii.gz` : Fichier NIfTI converti.                                     |
| **Métadonnées**           | `image.json` : Métadonnées extraites au format JSON.                        |
| **Segmentation cérébrale** | `image_bet_mask.nii.gz` : Masque cérébral généré par HD-BET.                 |
| **Recalage**              | `image_registered_atlas.nii.gz` : Atlas recalé.                              |
| **Radiomics**             | `image_radiomics_features.csv` : Caractéristiques radiomiques par région (Atlas/ROI). |

---

## Exemple de structure du CSV de sortie

Les fichiers CSV de sortie contiennent les colonnes suivantes selon les étapes effectuées :

| **Colonne**           | **Description**                                           |
|-----------------------|-----------------------------------------------------------|
| `Image`               | Nom de l'image d'entrée.                                  |
| `Source`              | Source des caractéristiques (`brain_mask`, `atlas`, `input_roi`). |
| `region_name`         | Nom de la région ou du masque utilisé.                    |
| **Caractéristiques**  | `original_shape_VoxelVolume`, `original_glcm_Correlation`, etc. |

#### Exemple :
```csv
Image,Source,region_name,atlas_region_label,original_firstorder_Mean,original_shape_VoxelVolume
image1,brain_mask,Brain Mask,,12.3,152000
image1,atlas,Frontal Lobe,1,15.7,134000
image1,input_roi,Custom_ROI_1,,20.4,50000
```

---

## Développement

### Pour les auteurs et collaborateurs :
- **Code principal** : `trex.py` (logique de pipeline).
- **Modules** :
  - `dicom_nii_converter.py` : Conversion DICOM vers NIfTI.
  - `metadata_extractor.py` : Extraction des metadonnées DICOM.
  - `radiomics_extractor.py` : Extraction des caractéristiques radiomiques.
  - `brain_extractor.py` : Génération de masques cérébraux.
  - `atlas_register.py` : Recalage des atlas/templates.

---

## Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

---

## Auteurs

- **Marc Saghiah**
- **Benjamin Lemasson**

Pour toute question ou suggestion, n'hésitez pas à nous contacter.

---