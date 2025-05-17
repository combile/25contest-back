from typing import Any, Callable
from openai import OpenAI
from pathlib import Path
from dotenv import load_dotenv
from tqdm import tqdm
import json, time, os, re


load_dotenv()

client = OpenAI(api_key=os.getenv("gpt_api"))
using_model = "gpt-4o"


#MARK: - 템플릿 임포트
with open(Path("../config/template/summary_template.json"), "r", encoding="utf-8") as f:
    summary_template = json.load(f)
    
with open(Path("../config/template/word_template.json"), "r", encoding="utf-8") as f:
    word_template = json.load(f)
    
with open(Path("../config/template/comment_template.json"), "r", encoding="utf-8") as f:
    comment_template = json.load(f)




#util: 추적용 래퍼 함수
def log_and_catch(task_name: str):
    def decorator(func: Callable):
        def wrapper(file_path: Path, *args, **kwargs):
            print(f"START : {task_name} : {file_path.name}")
            try:
                #내부에서 메인 로직 함수 실행
                result = func(file_path, *args, **kwargs)
            except Exception as e:
                print(f"FATAL : {file_path.name} - message : {e}")
            
            return
        return wrapper
    return decorator


#util: 저장
def save_output_json(output_json: Any, output_domain: str, id: int, type: str, level: str):
    
    save_dir = Path(f"../../data/generate_data/{output_domain}")
    if not save_dir.exists() : save_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = f"OutputJson_{type}_{level}_{id}.json"
    save_path = save_dir / file_name
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)
        
    return
    

#util : 생성 함수
def generate_content(
    data_path: Path,
    type: str = "",
    level: str = "",
    cnt: int = 0
):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    user_level = level
    summary_prompt = f"""
    당신은 텍스트 요약 전문 AI 어시스턴트입니다. 우리는 {data["content"]}를 바탕으로 요약문을 생성하여야합니다. 해당 본문의 주요한 단어는 {data["feature"]}입니다.
    아래의 규칙을 따라주세요.

    [본문]
    {data["content"]}

    [주요 단어]
    {data["feature"]}


    [규칙]
    1. 요약문은 정확히 70-span으로 생성해주세요.
    2. 주어진 {data["content"]}와 {data["feature"]}의 내용을 충분히 반영하도록 합니다.
    3. 편향이란 부정적, 긍정적, 정치적 등 한 쪽으로 의견이 쏠린 현상을 의미합니다. 요약문이 앞서 정의한 편향 현상이 일어나지 않게 객관적인 요약을 생성합니다.
    4. {level}이 "Low"일 경우 해당 요약을 읽을 사용자는 낮은 어휘력을 갖고 있습니다. 추상 요약을 진행하세요. 어려운 단어는 쉬운 단어로 변경하여 생성합니다.
    5. {level}이 "High"일 경우 해당 요약을 읽을 사용자는 높은 어휘력을 갖고 있습니다. 추출 요약을 진행하세요. 도메인 전문 단어만 이해할 수 있도록 변경하여 요약합니다.
    6. output은 {summary_template}형식에 맞게 json으로 제공합니다.
    """
    comment_prompt = f"""
    당신은 텍스트 전문 AI 어시스턴트입니다. 당신은 주어진 텍스트에 대하여 긍적적인 입장, 부정적인 입장을 제공하여 사용자의 객관적인 인식을 심어주는 역할을 수행합니다.
    우리는 {data["content"]}를 바탕으로 2종류의 코멘트를 생성하여야합니다. 해당 본문의 주요한 단어는 {data["feature"]}입니다.
    아래의 규칙을 따라주세요.

    1. 주어진 {data["content"]}에 대한 긍적적인 코멘트, 부적적인 코멘트 총 2종류의 코멘트를 생성합니다
    2. 코멘트는 정확히 50-span으로 작성해주세요.
    3. output은 {comment_template}형식에 맞게 json으로 제공합니다.

    """
    word_prompt =  f"""
    당신은 텍스트 전문 AI 어시스턴트입니다. 당신은 주어진 텍스트에 대하여 사용자의 어휘력 수준에 따라서 특정 단어 사전적 정의와 예문을 제시하여야합니다.
    우리는 {data["content"]}에서 3개의 단어를 추출합니다. 아래의 규칙을 따라주세요.

    1. {level}이 "Low"일 경우 어휘 난이도가 높은 순으로 추출합니다.
    2. {level}이 "High"일 경우 도메인적 지식이 높은 순으로 추출합니다.
    3. output은 {word_template}형식에 맞게 json으로 제공합니다.
    """
    
    
        
    response = client.chat.completions.create (
        model = using_model,
        messages = [
            {"role": "user",
            "content" : summary_prompt if type == "summary" 
                        else comment_prompt if type == "comment"
                        else word_prompt
            }
        ]
    )
    
    print(f"응답: {repr(response.choices[0].message.content)}")
    output_json = response.choices[0].message.content.strip()
    
    # ✅ 코드블럭 내부만 추출 (```json ... ```)
    match = re.search(r"```json\n(.*?)\n```", output_json, re.DOTALL)
    if match: json_str = match.group(1).strip()
    
    # if output_json.startswith("```"):
    #     #정규식으로 코드블록 표시 제거
    #     #^ : 문자열 시작 ~ \n:줄넘김
    #     output_json = re.sub(r"^```[a-zA-Z]*\n","",output_json)
        
    #     #\n:줄넘김으로 시작하고 $ : 문자열 끝을 의미
    #     output_json = re.sub(r"\n```$","", output_json) 
        
    #json 형식으로 구성된 문자열을 json으로 로드 / eval 사용 X
    output_json = json.loads(json_str)
        
    
    output_json["newsId"] = data["news_id"]
    if type == "comment":
        output_json["pnEvaluationId"] = f"PNC-20250517-{cnt}"
        
    elif type == "summary":
        output_json["level"] = level
        output_json["summary_id"] = f"SM-20250517-{cnt}"
        
    else:
        output_json["level"] = level
        output_json["wordDefinitionId"] = f"WD-20250517-{cnt}"
    
    
    

    #output_domain: 경제,국제,... etc
    save_output_json(output_json=output_json, output_domain=data_path.parent.name, id=cnt, type=type, level=level)

@log_and_catch("Generate Summarization")
def generate_summary(og_data_path: Path, template: Path = Path("../config/template/summary_template.json"), level: str = "", cnt: int = 0) -> Any:
    return generate_content(data_path = og_data_path, type="summary", level=level, cnt=cnt)

@log_and_catch("Generate Comment")
def generate_comment(og_data_path: Path, template: Path = Path("../config/template/comment_template.json"), cnt: int = 0)-> Any:
    return generate_content(data_path = og_data_path,  type="comment",  cnt=cnt)


@log_and_catch("Generate word")
def generate_word(og_data_path: Path, template: Path = Path("../config/template/word_template.json"), level: str = "", cnt: int = 0)-> Any:
    return generate_content(data_path=og_data_path, type="word", level=level, cnt=cnt)



def generate():
    root = Path("../../data/output")
    cnt = 1
    
    
    all_files = []
    for domain in root.iterdir():
        if domain.name == ".DS_Store": continue
        for file in domain.glob("*.json"):
            all_files.append(file)
            
    
    
    for file in tqdm(all_files, desc="Generating Data"):
        generate_summary(file, template = summary_template, level = "Low", cnt = cnt)
        generate_summary(file, template = summary_template, level = "High", cnt = cnt)
        
        generate_comment(file, template = comment_template, cnt = cnt)
        
        generate_word(file, template = word_template, level = "Low", cnt = cnt )
        generate_word(file, template = word_template, level = "High", cnt = cnt)
        
        cnt += 1
        
    



if __name__ == "__main__" :
    generate()