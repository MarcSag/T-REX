from setuptools import setup, find_packages

# Chargement du fichier README.md comme description longue (facultatif si README existe dans votre projet)
long_description = ""
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "T-REX: A powerful neuroimaging toolkit."

setup(
    name="T-REX",  # Le nom du projet
    version="1.0.0",  # Version de votre projet
    author="MarcSag",  # Ajoutez votre nom ou pseudo
    author_email="your.email@example.com",  # Facultatif
    description="A neuroimaging processing tool to streamline pipelines for T-REX.",  # Description courte
    long_description=long_description,  # Description longue
    long_description_content_type="text/markdown",  # Type (Markdown si README.md est utilisé)
    url="https://github.com/MarcSag/T-REX",  # URL de votre projet (dépôt GitHub par exemple)
    packages=find_packages(),  # Recherche automatiquement les sous-modules dans le projet
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",  # Version Python minimale requise pour T-REX
    install_requires=[
        "numpy==1.23.5",
        "pandas==1.5.3",
        "nibabel==5.0.0",
        "PyRadiomics==3.0.1",
        "SimpleITK==2.2.1",
        "hd-bet",
    ],  # Dépendances que vous avez indiquées dans requirements.txt
    entry_points={
        "console_scripts": [
            "trex=trex:main",  # Commande CLI 'trex', exécute la fonction main() dans le fichier trex.py
        ]
    },
    include_package_data=True,  # Inclure d'autres fichiers comme les fichiers .json, .csv, si présents dans MANIFEST.in
)