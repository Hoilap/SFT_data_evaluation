import gradio as gr
import django
import os
import sys
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_labelling.settings')
django.setup()
from label.models import SFTData, Score
from django.contrib.auth.models import User
from django.db.models import Count

# 这段CSS将应用于所有 gr.Code 组件，使其能自动换行
css_code = """
.gradio-container .gradio-code pre {
    white-space: pre-wrap !important;
    word-break: break-all !important;
}
"""

# 获取所有SFT数据
sft_list = list(SFTData.objects.all())

# 评分下拉选项
score_options = [1, 2, 3, 4, 5]

# 单条评分Tab
def show_single(idx, username):
    if not sft_list:
        return '暂无SFT数据', [], ''
    sft = sft_list[int(idx) % len(sft_list)]
    data = sft.data_json
    md = f"**问题：** {data.get('question', '')}"
    # 渲染answer字段为格式化JSON
    answer = data.get('answer', '')
    try:
        answer_json = json.loads(answer) if isinstance(answer, str) else answer
        answer_str = json.dumps(answer_json, ensure_ascii=False, indent=2)
    except Exception:
        answer_str = answer
    return md, score_options, answer_str

def submit_score(idx, username, score):
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
        return f"提交失败: {e}"



def get_compare_pair(username):
    import sqlite3
    db_path = 'db.sqlite3'
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    c.execute('SELECT id, system_prompt, instruction, output_1, output_2 FROM evaluation_data')
    rows = c.fetchall()
    conn.close()
    if not rows:
        return '数据库无数据', '', '', '', []
    from random import randint
    idx = randint(0, len(rows)-1)
    row = rows[idx]
    # 渲染四个部分
    system_prompt = row[1]
    instruction = row[2]
    output_1 = row[3]
    output_2 = row[4]
    md_left = f"**System Prompt：**\n{system_prompt}\n\n**Instruction：**\n{instruction}"
    md_right = md_left  # 左右都显示system_prompt和instruction
    def split_output(text):
        import re
        think = ''
        output = text
        m = re.search(r'<seed:think>(.*?)(<\\/seed:think>|<\/seed:think>)', text, re.DOTALL)
        if m:
            think = m.group(1).strip()
            output = text[m.end():].strip()
        return think, output

    def format_json(text):
        if not text:
            return ''
        try:
            obj = json.loads(text)
            return json.dumps(obj, ensure_ascii=False, indent=2)
        except Exception:
            return text

    think_1, out_1 = split_output(row[3])
    think_2, out_2 = split_output(row[4])

    # output_1左，output_2右
    index=["System Prompt", "User Instruction", "Thought Process", "Output"]
    return md_left, md_right, format_json(think_1), format_json(think_2), format_json(out_1), format_json(out_2), ['A更好','B更好','一样好'], index, index

def submit_compare(username, result, idx_a, idx_b):
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        return f"用户 {username} 不存在，请先注册或输入正确用户名。"
    try:
        a, b = sft_list[int(idx_a)], sft_list[int(idx_b)]
        Score.objects.create(user=user, sft=a, compare_id=b.id, compare_result=result)
        return f"对比结果已提交：{result}"
    except Exception as e:
        return f"提交失败: {e}"

# 进度Tab

def get_progress(username):
    user = User.objects.get(username=username)
    total = SFTData.objects.count()
    done = Score.objects.filter(user=user, score__isnull=False).count()
    compare_done = Score.objects.filter(user=user, compare_result__isnull=False).count()
    return f"单条评分进度：{done}/{total}\n两两对比进度：{compare_done}"

with gr.Blocks(title="SFT数据标注平台",css=css_code) as demo:
    gr.Markdown("# SFT数据标注与评估平台\n---")
    with gr.Tab("单条评分"):
        username = gr.Textbox(label="用户名", value="testuser")
        idx = gr.Number(label="数据索引", value=0, precision=0)
        md = gr.Markdown()
        score_dd = gr.Dropdown(label="评分", choices=score_options)
        json_code = gr.Code(label="原始JSON", language="json", lines=15, interactive=False)
        submit_btn = gr.Button("提交评分")
        idx.change(show_single, [idx, username], [md, score_dd, json_code])
        submit_btn.click(submit_score, [idx, username, score_dd], outputs=md)
    with gr.Tab("两两对比"):
        with gr.Column():
            with gr.Column(scale=8):
                # 左侧A内容
                gr.Markdown("#### A")
                md_a = gr.Markdown()
                thought_a = gr.Code(label="A thought", language='json', lines=8, interactive=False)
                json_a = gr.Code(label="A answer原始JSON", language='json', lines=18, interactive=False)
            with gr.Column(scale=8):
                # 右侧B内容
                gr.Markdown("#### B")
                md_b = gr.Markdown()
                thought_b = gr.Code(label="B thought", language='json', lines=8, interactive=False)
                json_b = gr.Code(label="B answer原始JSON", language='json', lines=18, interactive=False)
            with gr.Column(scale=2, min_width=180):
                # 右上角用户名和按钮
                username2 = gr.Textbox(label="用户名", value="testuser")
                get_btn = gr.Button("获取对比对")
        compare_dd = gr.Dropdown(label="选择更优", choices=['A更好','B更好','一样好'])
        idx_a = gr.State()
        idx_b = gr.State()
        submit_compare_btn = gr.Button("提交对比")
        get_btn.click(get_compare_pair, [username2], [md_a, md_b, thought_a, thought_b,json_a, json_b, compare_dd, idx_a, idx_b])
        submit_compare_btn.click(submit_compare, [username2, compare_dd, idx_a, idx_b], outputs=md_a)
    with gr.Tab("进度"):
        username3 = gr.Textbox(label="用户名", value="testuser")
        progress_md = gr.Markdown()
        get_progress_btn = gr.Button("刷新进度")
        get_progress_btn.click(get_progress, [username3], progress_md)

    demo.launch()
