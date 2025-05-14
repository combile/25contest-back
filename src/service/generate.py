from typing import Any, Callable
from openai import OpenAI
from pathlib import Path
import json, time


client = OpenAI()
using_model = ""

summary_prompt = ""
comment_prompt = ""
word_prompt = ""

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
def save_output_json(output_json: Any, output_domain: str):
    """_summary_

    Args:
        output_json (Any): _description_
        output_domain (str): _description_
        source_file (Path): _description_
    """
    save_dir = Path(f"../../data/generate_data/{output_domain}")
    if not save_dir.exists() : save_dir.mkdir(parents=True, exist_ok=True)
    
    file_name = ".json"
    save_path = save_dir / file_name
    
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(output_json, f, ensure_ascii=False, indent=4)
        
    return
    

#util : 생성 함수
def generate_content(
    data_path: Path,
    template: Path,
    prompt: str
):
    with open(data_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    response = client.responses.create (
        model = using_model,
        input = [
            {"role": "user",
            "content" : prompt
            }
        ]
    )
    
    output_json = response.output_text

    #output_domain: 경제,국제,... etc
    save_output_json(output_json=output_json, output_domain="")

@log_and_catch("Generate Summarization")
def generate_summary(og_data_path: Path, template: Path = Path("../config/template/summary_template.json")) -> Any:
    return generate_content(data_path = og_data_path, template=template, prompt=summary_prompt)

@log_and_catch("Generate Comment")
def generate_comment(og_data_path: Path, template: Path = Path("../config/template/comment_template.json"))-> Any:
    return generate_content(data_path = og_data_path, template=template, prompt=comment_prompt)


@log_and_catch("Generate word")
def generate_word(og_data_path: Path, template: Path = Path("../config/template/word_template.json"))-> Any:
    return generate_content(data_path=og_data_path, template=template, prompt=word_prompt)