import os
import cv2
from typing import List

def extract_frames(video_path: str, output_dir: str, interval_seconds: int = 30):
    """
    비디오에서 지정된 시간 간격으로 프레임을 추출합니다.
    
    Args:
        video_path (str): 비디오 파일 경로
        output_dir (str): 추출된 프레임을 저장할 디렉토리
        interval_seconds (int): 프레임을 추출할 시간 간격(초)
    """
    video_name = os.path.splitext(os.path.basename(video_path))[0]
    cap = cv2.VideoCapture(video_path)
    
    if not cap.isOpened():
        print(f"Error: 비디오 파일을 열 수 없습니다: {video_path}")
        return
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    frame_interval = int(fps * interval_seconds)
    
    print(f"Processing {video_path} - FPS: {fps}, Total frames: {total_frames}")
    print(f"Extracting frames every {interval_seconds} seconds ({frame_interval} frames)")
    
    os.makedirs(output_dir, exist_ok=True)
    
    frame_count = 0
    saved_count = 0
    
    while True:
        ret, frame = cap.read()
        
        if not ret:
            break
        
        if frame_count % frame_interval == 0:
            output_path = os.path.join(output_dir, f"{video_name}_frame{frame_count}.jpg")
            cv2.imwrite(output_path, frame)
            saved_count += 1
            print(f"Saved frame {frame_count} to {output_path}")
        
        frame_count += 1
    
    cap.release()
    print(f"Completed extracting {saved_count} frames from {video_path}")


def extract_incheon_airport_annotation_images(input_dir: str, output_dir: str = "annotations", interval_seconds: int = 30):
    """
    인천공항 비디오 데이터에서 어노테이션을 위한 프레임 이미지를 추출하는 함수
    
    Args:
        input_dir (str): TEST001~TEST010 폴더가 있는 입력 디렉토리 경로
        output_dir (str): 어노테이션용 이미지를 저장할 출력 디렉토리 경로
        interval_seconds (int): 프레임을 추출할 시간 간격(초), 기본값 30초
    """
    os.makedirs(output_dir, exist_ok=True)
    
    # TEST001부터 TEST010까지 순회
    for i in range(1, 11):
        test_folder = f"TEST{str(i).zfill(3)}"
        test_dir_path = os.path.join(input_dir, test_folder)
        
        # 해당 TEST 폴더가 존재하는지 확인
        if not os.path.exists(test_dir_path) or not os.path.isdir(test_dir_path):
            print(f"Warning: {test_dir_path} not found or not a directory, skipping...")
            continue
            
        print(f"\nProcessing {test_folder}...")
        
        # 각 TEST 폴더별 출력 디렉토리 생성
        test_output_dir = os.path.join(output_dir, test_folder)
        os.makedirs(test_output_dir, exist_ok=True)
        
        # 폴더 내의 모든 MP4 파일 처리
        for file_name in os.listdir(test_dir_path):
            if file_name.lower().endswith('.mp4'):
                video_path = os.path.join(test_dir_path, file_name)
                extract_frames(video_path, test_output_dir, interval_seconds)