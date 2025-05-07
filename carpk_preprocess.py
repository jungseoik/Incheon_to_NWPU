import os
import zipfile
from datasets import load_dataset
import shutil

# 기본 디렉토리 설정
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
CARPK_DATASETS_DIR = os.path.join(BASE_DIR, "carpk_datasets")
CARPK_DIR = os.path.join(BASE_DIR, "CARPK")

# 레포지토리 정보
REPO_ID = "backseollgi/carpk_custom"

def main():
    # 1. carpk_datasets 폴더 생성
    if not os.path.exists(CARPK_DATASETS_DIR):
        os.makedirs(CARPK_DATASETS_DIR)
        print(f"📁 carpk_datasets 폴더 생성 완료")
    else:
        print(f"📁 carpk_datasets 폴더가 이미 존재합니다")
    
    # 2. 데이터셋 다운로드
    try:
        print(f"🔄 {REPO_ID} 데이터셋 다운로드 중...")
        dataset = load_dataset(REPO_ID, cache_dir=CARPK_DATASETS_DIR)
        print(f"✅ 데이터셋 다운로드 완료!")
        
        # 데이터셋 정보 출력
        print(f"📊 데이터셋 정보: {dataset}")
        
        # 다운로드된 파일 찾기
        cache_path = os.path.join(CARPK_DATASETS_DIR, "downloads")
        zip_files = []
        
        # 다운로드 폴더 내의 모든 .zip 파일 찾기
        if os.path.exists(cache_path):
            for root, _, files in os.walk(cache_path):
                for file in files:
                    if file.endswith(".zip"):
                        zip_files.append(os.path.join(root, file))
        
        if not zip_files:
            print("⚠️ .zip 파일을 찾을 수 없습니다. 다른 방법으로 시도합니다.")
            # datasets.zip 파일 생성하기 (데이터셋의 내용을 직접 압축)
            dataset_path = os.path.join(CARPK_DATASETS_DIR, "datasets.zip")
            if os.path.exists(dataset_path):
                print(f"✅ datasets.zip 파일이 이미 존재합니다: {dataset_path}")
            else:
                try:
                    # 파일들을 임시 폴더에 저장
                    temp_dir = os.path.join(CARPK_DATASETS_DIR, "temp")
                    if not os.path.exists(temp_dir):
                        os.makedirs(temp_dir)
                    
                    # 데이터셋의 각 항목을 파일로 저장
                    for split in dataset:
                        for idx, item in enumerate(dataset[split]):
                            if 'file_path' in item:
                                src_path = item['file_path']
                                if os.path.exists(src_path):
                                    # 파일 복사
                                    filename = os.path.basename(src_path)
                                    dst_path = os.path.join(temp_dir, filename)
                                    shutil.copy(src_path, dst_path)
                    
                    # 임시 폴더를 압축
                    with zipfile.ZipFile(dataset_path, 'w') as zipf:
                        for root, _, files in os.walk(temp_dir):
                            for file in files:
                                zipf.write(
                                    os.path.join(root, file),
                                    os.path.relpath(os.path.join(root, file), temp_dir)
                                )
                    
                    # 임시 폴더 삭제
                    shutil.rmtree(temp_dir)
                    print(f"✅ datasets.zip 파일 생성 완료: {dataset_path}")
                    zip_files = [dataset_path]
                except Exception as e:
                    print(f"❌ datasets.zip 파일 생성 중 오류 발생: {e}")
        
        # .zip 파일이 있는 경우 처리
        if zip_files:
            dataset_path = zip_files[0]  # 첫 번째 zip 파일 사용
            print(f"✅ 압축 파일을 찾았습니다: {dataset_path}")
            
            # 3. CARPK 폴더 생성
            if not os.path.exists(CARPK_DIR):
                os.makedirs(CARPK_DIR)
                print(f"📁 CARPK 폴더 생성 완료")
            else:
                print(f"📁 CARPK 폴더가 이미 존재합니다")
            
            # 4. 압축 해제
            try:
                with zipfile.ZipFile(dataset_path, 'r') as zip_ref:
                    print(f"📂 CARPK 폴더에 데이터셋 압축 해제 중...")
                    zip_ref.extractall(CARPK_DIR)
                    print(f"✅ 압축 해제 완료!")
            except Exception as e:
                print(f"❌ 압축 해제 중 오류 발생: {e}")
                return
        else:
            # 압축 파일이 없으면 데이터셋 파일을 직접 복사
            print("⚠️ 압축 파일을 찾을 수 없어 데이터셋 파일을 직접 복사합니다.")
            
            # CARPK 폴더 생성
            if not os.path.exists(CARPK_DIR):
                os.makedirs(CARPK_DIR)
                print(f"📁 CARPK 폴더 생성 완료")
            else:
                print(f"📁 CARPK 폴더가 이미 존재합니다")
            
            # 데이터셋의 각 항목을 CARPK 폴더로 복사
            files_copied = 0
            for split in dataset:
                for idx, item in enumerate(dataset[split]):
                    if 'file_path' in item:
                        src_path = item['file_path']
                        if os.path.exists(src_path):
                            # 파일 복사
                            filename = os.path.basename(src_path)
                            dst_path = os.path.join(CARPK_DIR, filename)
                            shutil.copy(src_path, dst_path)
                            files_copied += 1
            
            print(f"✅ {files_copied}개 파일을 CARPK 폴더로 복사했습니다.")
    
    except Exception as e:
        print(f"❌ 데이터셋 다운로드 중 오류 발생: {e}")
        return
        
    print("🎉 모든 작업이 완료되었습니다!")

if __name__ == "__main__":
    main()