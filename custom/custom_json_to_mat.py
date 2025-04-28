import os
import json
import numpy as np
from scipy.io import savemat
import glob
from utils.logger import custom_logger

logger = custom_logger(__name__)

def convert_json_to_mat(json_folder, output_base_path):
    """
    JSON 파일들을 MAT 파일로 변환합니다.
    
    Args:
        json_folder (str): JSON 파일들이 있는 폴더 경로
        output_base_path (str): MAT 파일들이 저장될 기본 경로
    
    Returns:
        None
    """
    mats_folder = os.path.join(output_base_path, 'mats')
    os.makedirs(mats_folder, exist_ok=True)
    
    json_files = glob.glob(os.path.join(json_folder, '*.json'))
    
    for json_file in json_files:
        filename = os.path.basename(json_file)
        basename = os.path.splitext(filename)[0]
        
        mat_file = os.path.join(mats_folder, f"{basename}.mat")
        
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            points = np.array(data['points'], dtype=np.float32)
            boxes = np.array(data['boxes'], dtype=np.float32) if 'boxes' in data else np.array([])
            
            savemat(mat_file, {
                'annPoints': points,
                'annBoxes': boxes
            })
            
            logger.info(f"변환 완료: {filename} -> {basename}.mat")
            
        except Exception as e:
            logger.error(f"오류 발생 ({filename}): {str(e)}")
    
    logger.info(f"총 {len(json_files)}개 파일 처리 완료. 결과는 {mats_folder}에 저장되었습니다.")
