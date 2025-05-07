import os
import json
import shutil

def get_center(x1, y1, x2, y2):
    return [(x1 + x2) / 2, (y1 + y2) / 2]

def process_devkit(devkit_name, output_name):
    # 경로 설정
    BASE_ROOT = f"/home/dev/jungseoik/CLIP-EBC/CARPK/datasets/{devkit_name}/data"
    IMAGE_DIR = os.path.join(BASE_ROOT, "Images")
    ANNOTATION_DIR = os.path.join(BASE_ROOT, "Annotations")
    IMAGESETS_DIR = os.path.join(BASE_ROOT, "ImageSets")

    OUTPUT_ROOT = f"/home/dev/jungseoik/CLIP-EBC/CARPK/datasets/CARPK_ebc_setting/{output_name}"
    OUTPUT_IMAGE_DIR = os.path.join(OUTPUT_ROOT, "images")
    OUTPUT_ANN_DIR = os.path.join(OUTPUT_ROOT, "annotations")
    OUTPUT_IMAGESETS_DIR = os.path.join(OUTPUT_ROOT, "imagesets")

    os.makedirs(OUTPUT_IMAGE_DIR, exist_ok=True)
    os.makedirs(OUTPUT_ANN_DIR, exist_ok=True)
    os.makedirs(OUTPUT_IMAGESETS_DIR, exist_ok=True)

    # ImageSets 복사
    for imagesets_file in os.listdir(IMAGESETS_DIR):
        if imagesets_file.endswith(".txt"):
            shutil.copy(
                os.path.join(IMAGESETS_DIR, imagesets_file),
                os.path.join(OUTPUT_IMAGESETS_DIR, imagesets_file)
            )
    
    print(f"✅ {output_name.upper()} ImageSets 복사 완료 - {len(os.listdir(OUTPUT_IMAGESETS_DIR))}개 파일 복사됨")

    # 처리 시작
    for ann_file in os.listdir(ANNOTATION_DIR):
        if not ann_file.endswith(".txt"):
            continue

        img_id = os.path.splitext(ann_file)[0]
        ann_path = os.path.join(ANNOTATION_DIR, ann_file)

        image_path_jpg = os.path.join(IMAGE_DIR, f"{img_id}.jpg")
        image_path_png = os.path.join(IMAGE_DIR, f"{img_id}.png")

        if os.path.exists(image_path_jpg):
            image_path = image_path_jpg
        elif os.path.exists(image_path_png):
            image_path = image_path_png
        else:
            print(f"🚫 이미지 누락: {img_id}")
            continue

        # 이미지 복사
        shutil.copy(image_path, os.path.join(OUTPUT_IMAGE_DIR, os.path.basename(image_path)))

        # 어노테이션 처리
        points = []
        boxes = []
        with open(ann_path, "r") as f:
            for line in f:
                x1, y1, x2, y2, _ = map(float, line.strip().split())
                boxes.append([x1, y1, x2, y2])
                points.append(get_center(x1, y1, x2, y2))

        json_data = {
            "img_id": os.path.basename(image_path),
            "car_num": len(points),
            "points": points,
            "boxes": boxes
        }

        json_path = os.path.join(OUTPUT_ANN_DIR, f"{img_id}.json")
        with open(json_path, "w") as jf:
            json.dump(json_data, jf, indent=4)

    print(f"✅ {output_name.upper()} 전처리 완료 - {len(os.listdir(OUTPUT_ANN_DIR))}개 JSON 저장됨")

# CARPK 처리
process_devkit("CARPK_devkit", "carpk")

# PUCPR+ 처리
process_devkit("PUCPR+_devkit", "pucpr")