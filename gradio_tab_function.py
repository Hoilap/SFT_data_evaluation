# --- Gradio Tab Functions ---

from utils import *
import gradio as gr
# 单条评分Tab
score_options = [1, 2, 3, 4, 5]
def show_single(idx):
    ...
    
'''    data = sft_item.get('data_json', {}) if isinstance(sft_item, dict) else sft_item.data_json
    
    question = data.get('question', '')
    md = f"**问题：** {question}"
    
    answer = data.get('answer', '')
    answer_str = robust_format_json_string(answer)
    
    return md, score_options, answer_str'''

def submit_score(idx, username, score):
    ...
'''    if not DJANGO_AVAILABLE:
        return f"提交成功（模拟模式）：用户 {username} 对索引 {idx} 评分为 {score}"
    if not sft_list:
        return "无可评分数据"
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return f"用户 {username} 不存在，请先注册或输入正确用户名。"
    try:
        sft = sft_list[int(idx) % len(sft_list)]
        Score.objects.update_or_create(user=user, sft=sft, defaults={'score': score})
        return f"已提交评分：{score}"
    except Exception as e:
        return f"提交失败: {e}"'''




# 两两对比Tab
def get_compare_pair(username):
    try:
        from label.models import EvaluationData #用Django ORM操作 evaluation_data 表
        # 随机获取一条SFTData
        row = EvaluationData.objects.order_by('?').first()
        print(row)
        if not row:
            return ('数据库无对比数据', '', '', '', '', gr.Dropdown(choices=[]), None, None)
        # 假设SFTData模型有如下字段：id, system_prompt, instruction, output_1, output_2
        row_id = row.id
        system_prompt = getattr(row, 'system_prompt', '')
        full_instruction = getattr(row, 'instruction', '')
        output_1 = getattr(row, 'output_1', '')
        output_2 = getattr(row, 'output_2', '')
        ground_truth = getattr(row, 'ground_truth', '')

        blocks = extract_instruction_blocks(full_instruction)
        instruction = blocks[0] if blocks else ''
        data_json = blocks[1] if len(blocks) > 1 else {}
        shared_context = (
            f"___\n**SYSTEM PROMPT**\n___\n{system_prompt}\n\n"
            f"___\n**INSTRUCTION**\n___\n{instruction}"
        )

        think_a, out_a = split_output(output_1)
        think_b, out_b = split_output(output_2)
        think_gt, out_gt = split_output(ground_truth)

        return (
            shared_context, data_json,
            think_a, out_a, # a是纯markdown, 只需要原样输出；#有robust_format_json_string可用
            safe_json_loads(think_b), safe_json_loads(out_b), # b和ground_truth是json格式
            safe_json_loads(think_gt), safe_json_loads(out_gt),
            gr.Dropdown(choices=['A更好', 'B更好', '一样好'], value=None),
            row_id, row_id
        )
    except Exception as e:
        return (f'数据库查询异常: {e}', '', '', '', '', '', gr.Dropdown(choices=[]), None, None)


def submit_compare(username, result, idx_a):
    ...
'''    if not result:
        return "请先选择一个对比结果再提交。"
    if not DJANGO_AVAILABLE:
        return f"提交成功（模拟模式）：用户 {username} 认为 {result} (ID: {idx_a})"
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return f"用户 {username} 不存在，请先注册或输入正确用户名。"
    try:
        # 假设您的Score模型可以记录这种对比
        # Score.objects.create(user=user, evaluation_id=idx_a, compare_result=result)
        return f"对比结果已提交：{result} (ID: {idx_a})"
    except Exception as e:
        return f"提交失败: {e}"'''

# 进度Tab
def get_progress(username):
    ...
'''    try:
        user = User.objects.get(username=username)
        total = SFTData.objects.count()
        done = Score.objects.filter(user=user, score__isnull=False).count()
        compare_done = Score.objects.filter(user=user, compare_result__isnull=False).count()
        return f"单条评分进度：{done}/{total}\n两两对比进度：{compare_done}"
    except User.DoesNotExist:
        return f"用户 {username} 不存在。"
    except Exception as e:
        return f"获取进度失败: {e}"'''
