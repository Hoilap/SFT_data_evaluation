import os
import django
import json
from django.db import transaction

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_labelling.settings')
django.setup()

from label.models import EvaluationData

file1 = './data/SeedOss-Output.jsonl'
file2 = './data/SeedOss-SFT-Output.jsonl'

def read_jsonl_lines(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

data1 = list(read_jsonl_lines(file1))
data2 = list(read_jsonl_lines(file2))
assert len(data1) == len(data2), '两个文件行数不一致!'

objs = []
for d1, d2 in zip(data1, data2):
    assert d1['system_prompt'] == d2['system_prompt'] and d1['instruction'] == d2['instruction'], 'system_prompt或instruction不一致!'
    objs.append(EvaluationData(
        system_prompt=d1['system_prompt'],
        instruction=d1['instruction'],
        output_1=d1['model_response'],
        output_2=d2['model_response'],
        ground_truth=d1['output']
    ))

# 使用事务，确保清空与插入要么全部成功要么全部回滚
with transaction.atomic():
    deleted_count, _ = EvaluationData.objects.all().delete()
    print(f'已清空 EvaluationData 表，删除 {deleted_count} 条记录。')
    EvaluationData.objects.bulk_create(objs)
    print('数据插入完成!')