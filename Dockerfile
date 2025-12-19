# Base image from Miniforge for Conda - preconfigured for multi-language scientific stacks
FROM condaforge/miniforge3:latest

LABEL maintainer="Your Name <your.email@example.com>"

# Set the FSL conda channel
ENV FSL_CONDA_CHANNEL="https://fsl.fmrib.ox.ac.uk/fsldownloads/fslconda/public/"
# Set the FSLDIR environment
ENV FSLDIR="/opt/conda"
ENV PATH=$FSLDIR/bin:$PATH

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y libxt6 git-lfs g++ build-essential && \
    git lfs install && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Update Conda and downgrade Python to a compatible version
RUN conda update -n base -c defaults conda -y
RUN conda install python=3.10 -y

# Install Tini and clean up Conda temporary files
RUN conda install --solver=libmamba -n base -c conda-forge tini && conda clean -a -y

# Install FSL tools (e.g., flirt) from FSL's Conda public channel
RUN conda install --solver=libmamba -n base -c $FSL_CONDA_CHANNEL fsl-flirt -c conda-forge -y && conda clean -a -y

# Preinstall required dependencies for Python libraries
RUN pip install --no-cache-dir numpy==1.23.5 Cython
RUN pip install --no-cache-dir --upgrade pip setuptools wheel

# Install PyRadiomics without isolation
RUN pip install --no-cache-dir --no-build-isolation PyRadiomics==3.0.1

# Install the remaining dependencies from requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --no-deps

# Install HD-BET
RUN pip install --no-cache-dir hd-bet

# Install T-REX pipeline tools directly from GitHub
RUN pip install git+https://github.com/MarcSag/T-REX.git@v1.0

# Copy app source files into container
COPY . .

# Application entrypoint configuration
ENTRYPOINT ["python", "/app/trex.py"]
CMD ["--help"]