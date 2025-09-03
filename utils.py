import json
import ast
import re

# --- Helper Functions ---
def robust_format_json_string(text):
    """
    安全地将一个看起来像字典/列表的字符串格式化为美观的JSON字符串。
    使用 ast.literal_eval 来处理Python风格的字符串（例如，包含单引号）。
    """
    if not isinstance(text, str) or not text.strip():
        return ''
    
    text = text.strip()
    try:
        # ast.literal_eval 可以安全地评估包含Python字面量的字符串
        obj = ast.literal_eval(text)
        # 然后将Python对象转换为格式正确的JSON字符串
        return json.dumps(obj, ensure_ascii=False, indent=2)
    except (ValueError, SyntaxError, MemoryError, TypeError):
        # 如果失败，说明它可能不是字典/列表字符串，按原样返回
        # 同时尝试标准JSON解析作为备用
        try:
            obj = json.loads(text)
            return json.dumps(obj, ensure_ascii=False, indent=2)
        except Exception:
            #print("JSON解析失败，使用原始文本。")
            return text

def split_output(text):
    """根据自定义标签将文本分割为 'think' 和 'output' 部分。"""
    if not isinstance(text, str):
        return '', ''
    think = ''
    output = text
    m = re.search(r'<seed:think>(.*?)(?:<\\/seed:think>|<\/seed:think>)', text, re.DOTALL)
    if m:
        think = m.group(1).strip()
        output = text[m.end():].strip()
    return think, output

def safe_json_loads(text):
    if not text or not isinstance(text, str) or not text.strip():
        return None
    try:
        return json.loads(text)
    except Exception:
        try:
            return ast.literal_eval(text)
        except Exception:
            return None
        
def extract_instruction_blocks(text):
    pattern = re.compile(r'<([a-zA-Z0-9_]+)>[\s\S]*?</\1>', re.MULTILINE)
    blocks = []
    last_end = 0
    matches = list(pattern.finditer(text))
    # 提取前置说明文字：取 instruction 中“#### 输入数据”前的所有文字
    pre_text = ''
    if text:
        split_marker = '#### 输入数据'
        idx = text.find(split_marker)
        if idx != -1:
            pre_text = text[:idx].strip()
        else:
            # 如果没有该标记，回退到原有逻辑，取第一个块前的内容
            if matches:
                first_start = matches[0].start()
                pre_text = text[:first_start].strip()
            else:
                pre_text = text.strip()
    if pre_text:
        blocks.append(pre_text)
        
    data_json={}
    # 依次提取每个块
    for m in matches:
        tag = re.search(r'<([a-zA-Z0-9_]+)>', m.group(0)).group(1)
        content = re.search(rf'<{tag}>([\s\S]*?)</{tag}>', m.group(0)).group(1).strip()
        # 尝试解析为json
        obj = safe_json_loads(content)
        data_json[tag] = obj
    # print(data_json)
    # data_json_str = robust_format_json_string(data_json)
    data_json_str = json.dumps(data_json, ensure_ascii=False, indent=2)
    #print("================")
    blocks.append(data_json_str)
    return blocks
