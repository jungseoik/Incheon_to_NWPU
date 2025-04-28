from custom.custom_rename_split import process_dataset
from custom.custom_json_to_mat import convert_json_to_mat

IMAGE_FOLDER_PATH = "sample/sample_images_part1"
LABEL_FOLDER_PATH = "sample/jsons"
OUTPUT_PATH = "sample/"
SPLIT_RATIO = [0.9, 0.1, 0.0]


if __name__ == "__main__":
    process_dataset(
        image_folder=IMAGE_FOLDER_PATH,
        label_folder=LABEL_FOLDER_PATH,
        output_path= OUTPUT_PATH,
        split_ratio= SPLIT_RATIO
    )
    convert_json_to_mat(LABEL_FOLDER_PATH, OUTPUT_PATH)
    