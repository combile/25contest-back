from pathlib import Path
from typing import *
import json
import pandas as pd


def createJson(file: str, save_dir: str) -> None :
    excel_file = pd.ExcelFile(file)
    save_path = Path(save_dir)
    sheet_names = excel_file.sheet_names

    print(sheet_names)
    for sheet_name in sheet_names:
        df = pd.read_excel(excel_file, sheet_name= sheet_name)
        validate_path = save_path/sheet_name ; cnt = 1
        

        #카테고리별 디렉토리 생성 -> 없으면 생성
        if not validate_path.exists() :
            validate_path.mkdir(parents=True, exist_ok=True)
            
        #한 행씩 접근
        for _, row in df.iterrows():
            #json 템플릿
            json_template = {
                "news_id": "식별자",
                "creatAt":"",
                "title": "제목",
                "author" : "작성자",
                "imageUrl": "",
                "feature": "",
                "content" : "본문 텍스트"
            }
            
            #데이터 입력
            json_template["news_id"] = f"N-{cnt}_" + str(row.get("뉴스 식별자","") or "")
            json_template["creatAt"] = str(row.get("일자","") or "")
            json_template["title"] = str(row.get("제목","") or "")
            json_template["author"] = str(row.get("기고자","")or "") #좌항 값이 Falsy(None, NaN etc)일때 우항 바인딩
            json_template["imageUrl"] = str(row.get("이미지","") or "")
            json_template["feature"] = row["특성추출(가중치순 상위 50개)"].split(",")
            json_template["content"] = row["본문"]

            #저장 파일명
            file_name = f"output_{cnt}.json"
            
            #저장
            with open(validate_path/file_name, "w", encoding="utf-8") as f:
                json.dump(json_template, f, ensure_ascii=False, indent=4)
                
            cnt += 1
            
        print("시트 처리 완료")    

    print("success")
    
    return
        
            
