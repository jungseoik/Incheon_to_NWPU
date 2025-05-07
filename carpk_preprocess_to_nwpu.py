import os
from huggingface_hub import hf_hub_download

# Repository information
repo_id = "backseollgi/carpk_custom"
filename = "datasets.zip"
repo_type = "dataset"  # Specify that this is a dataset repository

# Download the file
file_path = hf_hub_download(
    repo_id=repo_id,
    filename=filename,
    repo_type=repo_type
)

print(f"File downloaded successfully to: {file_path}")