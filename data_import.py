import os
import django
import json
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_labelling.settings')
django.setup()

from label.models import EvaluationData


def import_jsonl_to_db(file1_path, file2_path):
    if not file1_path or not file2_path:
        return "请上传两个文件！"
    try:
        with open(file1_path, 'r', encoding='utf-8') as f1:
            data1 = [json.loads(line) for line in f1 if line.strip()]
        with open(file2_path, 'r', encoding='utf-8') as f2:
            data2 = [json.loads(line) for line in f2 if line.strip()]
        if len(data1) != len(data2):
            return "两个文件行数不一致!"
        objs = []
        for d1, d2 in zip(data1, data2):
            if d1['system_prompt'] != d2['system_prompt'] or d1['instruction'] != d2['instruction']:
                return "system_prompt或instruction不一致!"
            objs.append(EvaluationData(
                system_prompt=d1['system_prompt'],
                instruction=d1['instruction'],
                output_1=d1['model_response'],
                output_2=d2['model_response'],
                ground_truth=d1.get('output', '')
            ))
        with transaction.atomic():
            #deleted_count, _ = EvaluationData.objects.all().delete()
            EvaluationData.objects.bulk_create(objs)
        return f"导入成功！共导入 {len(objs)} 条数据"
    except Exception as e:
        return f"导入失败: {e}"

def delete_data():
    # 删除所有数据
    deleted_count, _ = EvaluationData.objects.all().delete()
    return f"成功删除 {deleted_count} 条数据"

# 获取总数并初始化进度条最大值
def get_total_count():
    return EvaluationData.objects.count()

if __name__ == "__main__":
    file1 = './data/SeedOss-Output.jsonl'
    file2 = './data/SeedOss-SFT-Output.jsonl'

    # import_jsonl_to_db(file1, file2) #目前是直接在数据库后append
    delete_data()
    print(get_total_count())