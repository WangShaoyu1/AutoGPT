# 在forge/utils/log_execution_time.py文件中定义
import time
import os
import json


def log_execution_time(*args, **kwargs):
    start_time = time.time()
    end_time = time.time()
    execution_time = round(end_time - start_time, 3)

    task_id = kwargs.get("task_id", "Unknown Task ID")
    step_id = kwargs.get("step_id", 'Unknown Step ID')
    question = kwargs.get("question", "Unknown Question")
    answer = kwargs.get("answer", 'Unknown Answer')
    chat_completion_kwargs = kwargs.get("chat_completion_kwargs", "Unknown chat_completion_kwargs")
    log_file = kwargs.get("log_file", "/")

    log_entry = (
        f"-----Task ID: {task_id}----\n"
        f"Step ID: {step_id}\n"
        f"Question: {question}\n"
        f"Answer: {answer}\n"
        f"Chat Completion Kwargs: {format_value(chat_completion_kwargs)}\n"
        f"Execution Time: {execution_time} seconds\n"
        "------------------------\n"
    )

    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    with open(log_file, "a") as log_f:
        log_f.write(log_entry)


def format_value(value):
    """将类JSON格式的值转换为格式化的JSON字符串"""

    def remove_escape_characters(s):
        """移除字符串中的转义字符"""
        escape_characters = {
            '\\\\': '\\',  # 先处理双反斜杠
            '\\n': '\n',  # 换行符
            '\\t': '\t',  # 制表符
            '\\"': '"',  # 双引号
            "\\'": "'"  # 单引号
        }
        for escape_seq, char in escape_characters.items():
            s = s.replace(escape_seq, char)
        return s

    def parse_inner_json(s):
        """尝试解析内部JSON字符串"""
        try:
            parsed_json = json.loads(s)
            return json.dumps(parsed_json, ensure_ascii=False, indent=4)
        except (json.JSONDecodeError, TypeError):
            return s

    if isinstance(value, (dict, list)):
        return json.dumps(value, ensure_ascii=False, indent=4)
    if isinstance(value, str):
        value = remove_escape_characters(value)
        try:
            # 尝试解析为JSON
            parsed_json = json.loads(value)
            for key, val in parsed_json.items():
                if isinstance(val, str):
                    parsed_json[key] = parse_inner_json(remove_escape_characters(val))
                elif isinstance(val, (dict, list)):
                    parsed_json[key] = format_value(val)
            return json.dumps(parsed_json, ensure_ascii=False, indent=4)
        except (json.JSONDecodeError, TypeError):
            if '\n' in value:
                lines = value.split('\n')
                formatted_lines = []
                for line in lines:
                    formatted_lines.append(parse_inner_json(line))
                return '\n'.join(formatted_lines)
    return str(value)
