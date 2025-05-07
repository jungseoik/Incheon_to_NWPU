import os
import json
import shutil
import numpy as np
import scipy.io as sio
from tqdm import tqdm

def convert_carpk_to_nwpu_format(
    source_root="/home/dev/jungseoik/CLIP-EBC/CARPK/datasets/CARPK_ebc_setting/carpk",
    output_root="CARPK_to_NWPU",
    part_size=1000
):
    os.makedirs(output_root , exist_ok=True)
    image_dir = os.path.join(source_root, "images")
    annotation_dir = os.path.join(source_root, "annotations")
    imagesets_dir = os.path.join(source_root, "imagesets")

    # 출력 디렉토리 구성
    json_output_dir = os.path.join(output_root, "jsons")
    mat_output_dir = os.path.join(output_root, "mats")
    os.makedirs(json_output_dir, exist_ok=True)
    os.makedirs(mat_output_dir, exist_ok=True)

    # 이미지 및 어노테이션 정렬
    image_files = sorted([f for f in os.listdir(image_dir) if f.endswith(".png")])
    id_mapping = {}

    # 이미지 분할 및 이름 재설정
    for idx, img_file in enumerate(tqdm(image_files, desc="이미지 및 JSON 처리")):
        old_img_path = os.path.join(image_dir, img_file)
        new_img_name = f"{idx+1:04d}.jpg"
        new_img_path = os.path.join(output_root, f"images_part{(idx // part_size) + 1}")
        os.makedirs(new_img_path, exist_ok=True)
        final_img_path = os.path.join(new_img_path, new_img_name)

        # 이미지 복사 + 확장자 변경
        shutil.copy(old_img_path, final_img_path)
        id_mapping[os.path.splitext(img_file)[0]] = os.path.splitext(new_img_name)[0]  # old_id: new_id

        # 어노테이션 처리
        ann_file = os.path.join(annotation_dir, os.path.splitext(img_file)[0] + ".json")
        with open(ann_file, "r") as f:
            ann_data = json.load(f)

        # 이름, 포맷 수정 후 json 저장
        ann_data["img_id"] = new_img_name
        ann_data["human_num"] = ann_data["car_num"]
        del ann_data["car_num"]

        with open(os.path.join(json_output_dir, f"{id_mapping[os.path.splitext(img_file)[0]]}.json"), "w") as jf:
            json.dump(ann_data, jf, indent=4)

        # mat 파일 저장
        points = np.array(ann_data["points"], dtype=np.float32)
        sio.savemat(os.path.join(mat_output_dir, f"{id_mapping[os.path.splitext(img_file)[0]]}.mat"), {"annPoints": points})

    print("✅ 이미지, JSON, MAT 저장 완료")


    split_mapping = {
        "train.txt": "train.txt",
        "test.txt": "val.txt",    # carpk의 test → nwpu의 val
        "val.txt": "test.txt"     # nwpu의 test는 빈 파일로 대체
    }

    # split 파일 생성
    for carpk_split, nwpu_split in split_mapping.items():
        src_path = os.path.join(imagesets_dir, carpk_split)
        dst_path = os.path.join(output_root, nwpu_split)

        new_lines = []
        if carpk_split == "val.txt":
            # 빈 파일로 생성
            open(dst_path, "w").close()
            print(f"✅ {nwpu_split} 파일 (비어있음) 생성 완료")
            continue

        with open(src_path, "r") as sf:
            for line in sf:
                old_id = line.strip()
                new_id = id_mapping.get(old_id)
                if new_id:
                    new_lines.append(new_id + "\n")
                else:
                    print(f"⚠️ ID 누락: {old_id}")

        with open(dst_path, "w") as df:
            df.writelines(new_lines)
        print(f"✅ {nwpu_split} 파일 저장 완료 ({len(new_lines)}개)")

    print("✅ split 파일(train/val/test) 변환 완료")

# 실행
convert_carpk_to_nwpu_format()
