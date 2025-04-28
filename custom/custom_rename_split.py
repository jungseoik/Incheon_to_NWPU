import os
import glob
import random
import shutil
from PIL import Image
import json
from pathlib import Path
from utils.logger import custom_logger

logger = custom_logger(__name__)
def process_dataset(
    image_folder,
    label_folder,
    output_path,
    split_ratio=[0.9, 0.1, 0.0]
):
    """
    이미지 폴더와 라벨 폴더를 처리하고 train/val/test 분할을 수행합니다.
    
    Args:
        image_folder (str): 이미지 파일이 있는 폴더 경로
        label_folder (str): 라벨(JSON) 파일이 있는 폴더 경로
        output_path (str): 분할 결과 파일을 저장할 경로
        split_ratio (list): train, val, test 비율 (기본값: [0.8, 0.2, 0.0])
        
    Returns:
        dict: 처리 결과 및 통계 정보
    """
    # 1. 폴더 존재 확인
    if not os.path.exists(image_folder):
        logger.error(f"이미지 폴더가 존재하지 않습니다: {image_folder}")
        return {"error": f"이미지 폴더가 존재하지 않습니다: {image_folder}"}
    
    if not os.path.exists(label_folder):
        logger.error(f"라벨 폴더가 존재하지 않습니다: {label_folder}")
        return {"error": f"라벨 폴더가 존재하지 않습니다: {label_folder}"}
    
    os.makedirs(output_path, exist_ok=True)
    
    # 2. 분할 비율 확인
    if len(split_ratio) != 3 or sum(split_ratio) != 1.0:
        logger.error(f"분할 비율이 잘못되었습니다. 세 값의 합이 1.0이어야 합니다: {split_ratio}")
        return {"error": f"분할 비율이 잘못되었습니다. 세 값의 합이 1.0이어야 합니다: {split_ratio}"}
    
    if split_ratio[0] <= 0.0 or split_ratio[1] <= 0.0:
        logger.error("train과 val 비율은 0보다 커야 합니다.")
        return {"error": "train과 val 비율은 0보다 커야 합니다."}
    
    # 3. 이미지 파일 확인 및 변환
    logger.info("이미지 파일 확인 및 JPG 변환 중...")
    image_files = []
    converted_count = 0
    
    for file in os.listdir(image_folder):
        file_path = os.path.join(image_folder, file)
        
        if os.path.isdir(file_path):
            continue
            
        try:
            img = Image.open(file_path)
            
            # 확장자가 jpg가 아니라면 변환
            if not file.lower().endswith(('.jpg')):
                name, _ = os.path.splitext(file)
                new_path = os.path.join(image_folder, f"{name}.jpg")
                img = img.convert('RGB')  
                img.save(new_path, 'JPEG')
                os.remove(file_path)  
                file_path = new_path
                file = f"{name}.jpg"
                converted_count += 1
                
            image_files.append(file)
            
        except Exception as e:
            logger.warning(f"경고: {file}는 이미지 파일이 아니거나 손상되었습니다. 건너뜁니다. 오류: {e}")
    
    logger.info(f"이미지 파일 {len(image_files)}개 확인 완료, {converted_count}개 JPG로 변환됨")
    
    logger.info("라벨 파일과 이미지 파일 일치 확인 중...")
    label_files = [f for f in os.listdir(label_folder) if f.endswith('.json')]
    
    # 이미지와 라벨 파일 이름 맞추기 (확장자 제외)
    image_names = set([os.path.splitext(f)[0] for f in image_files])
    label_names = set([os.path.splitext(f)[0] for f in label_files])
    
    # 일치하지 않는 경우 확인
    images_without_labels = image_names - label_names
    labels_without_images = label_names - image_names
    
    if images_without_labels:
        logger.warning(f"경고: {len(images_without_labels)}개 이미지에 대응하는 라벨 파일이 없습니다.")
        
    if labels_without_images:
        logger.warning(f"경고: {len(labels_without_images)}개 라벨에 대응하는 이미지 파일이 없습니다.")
    
    common_names = image_names.intersection(label_names)
    if not common_names:
        logger.error("이미지와 라벨 파일이 일치하는 것이 없습니다.")
        return {"error": "이미지와 라벨 파일이 일치하는 것이 없습니다."}
    
    logger.info(f"이미지-라벨 쌍 {len(common_names)}개 발견됨")
    
    # 5. 파일 이름 변경 (0001.jpg, 0001.json 형식)
    logger.info("파일 이름 순차적으로 변경 중...")
    name_mapping = {}  # 원래 이름 -> 새 이름 매핑
    
    # 정렬된 공통 이름 목록
    common_names_list = sorted(list(common_names))
    
    for i, name in enumerate(common_names_list, 1):
        new_name = f"{i:04d}"  # 0001, 0002, ... 형식
        
        old_img_path = os.path.join(image_folder, f"{name}.jpg")
        if os.path.exists(old_img_path):
            new_img_path = os.path.join(image_folder, f"{new_name}.jpg")
            os.rename(old_img_path, new_img_path)
        
        old_label_path = os.path.join(label_folder, f"{name}.json")
        if os.path.exists(old_label_path):
            new_label_path = os.path.join(label_folder, f"{new_name}.json")
            os.rename(old_label_path, new_label_path)
        
        name_mapping[name] = new_name
    
    logger.info(f"총 {len(name_mapping)}개 파일 이름 변경됨")
    
    logger.info("데이터셋 분할 중...")
    
    all_indices = list(range(1, len(common_names) + 1))
    random.shuffle(all_indices)  
    
    train_count = int(len(all_indices) * split_ratio[0])
    val_count = int(len(all_indices) * split_ratio[1])
    
    train_indices = all_indices[:train_count]
    val_indices = all_indices[train_count:train_count + val_count]
    test_indices = all_indices[train_count + val_count:]
    
    splits = {
        "train": train_indices,
        "val": val_indices,
        "test": test_indices
    }
    
    for split_name, indices in splits.items():
        if not indices: 
            continue
            
        # nwpu 형식으로 저장: "0001 0 0" 형식
        with open(os.path.join(output_path, f"{split_name}.txt"), "w") as f:
            for idx in sorted(indices):  # 정렬된 순서로 저장
                f.write(f"{idx:04d} 0 0\n")
    
    logger.info("처리 완료!")
    logger.info(f"Train: {len(train_indices)}개, Val: {len(val_indices)}개, Test: {len(test_indices)}개")
    
    return True

