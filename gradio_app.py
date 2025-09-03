import gradio as gr
import django
import os
from utils import *
from gradio_tab_function import *

# --- Django Setup ---
# 说明：请确保您的Django项目路径在Python的搜索路径中，
# 并且'data_labelling.settings'是您项目的正确设置模块。
# 例如: sys.path.append('/path/to/your/django_project_folder')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_labelling.settings')
try:
    django.setup()
    from label.models import SFTData, Score
    from django.contrib.auth.models import User
    DJANGO_AVAILABLE = True
    print("Django setup successful. Running in database mode.")
except Exception as e:
    print(f"Django setup failed: {e}")
    print("Running in offline mode. Database features will be disabled.")
    # 定义模拟类，以便在没有Django的情况下UI仍然可以构建
    SFTData, Score, User = None, None, None
    DJANGO_AVAILABLE = False


# --- CSS for JSON Word Wrapping ---
# 这段CSS将应用于所有 gr.Code 组件，使其能自动换行
css_code = """
.gradio-container .gradio-code pre > code {
    white-space: pre-wrap !important;
    word-break: break-all !important;
}
.gradio-container .custom-fixed-height-code {
    height: 400px !important;
    overflow-y: hidden !important;
    min-height: 400px !important;
    max-height: 400px !important;
}
.gradio-container .custom-fixed-height-markdown {
    height: 400px !important;
    overflow-y: auto !important;
    min-height: 400px !important;
    max-height: 400px !important;
}
"""




# --- Gradio UI ---
with gr.Blocks(title="SFT数据标注与评估平台", css=css_code) as demo:
    gr.Markdown("# SFT数据标注与评估平台\n---")
    
    with gr.Tab("单条评分"):
        username_single = gr.Textbox(label="用户名", value="testuser")
        idx_single = gr.Number(label="数据索引", value=0, precision=0)
        md_single = gr.Markdown()
        score_dd_single = gr.Dropdown(label="评分", choices=score_options)
        json_code_single = gr.Code(label="Answer JSON", language="json", lines=15, interactive=False)
        submit_btn_single = gr.Button("提交评分")
        
        status_single = gr.Markdown()

        demo.load(show_single, [idx_single], [md_single, score_dd_single, json_code_single])
        idx_single.change(show_single, [idx_single], [md_single, score_dd_single, json_code_single])
        submit_btn_single.click(submit_score, [idx_single, username_single, score_dd_single], outputs=status_single)
        
    with gr.Tab("两两对比"):
        with gr.Row():
            shared_info_box = gr.Textbox(
                label="共享的 System Prompt 和 Instruction",
                lines=15,
                interactive=False,
                show_copy_button=True
            )
            data_json = gr.Code(label="Data JSON", language='json', lines=15, interactive=False, elem_classes=["custom-fixed-height-code"])
        with gr.Row():
                thought_gt = gr.JSON(label="Ground_truth - Thought Process",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
                json_gt = gr.JSON(label="Ground_truth - Answer",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
        with gr.Row():
            with gr.Column(scale=1):
                gr.Markdown("## A (Output 1)")
                #thought_a = gr.Code(label="A - Thought Process", language='markdown', lines=12, interactive=False, elem_classes=["custom-fixed-height"])
                #json_a = gr.Code(label="A - Answer", language='markdown', lines=18, interactive=False, elem_classes=["custom-fixed-height"])
                thought_a = gr.Markdown(label="A - Thought Process",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
                json_a = gr.Markdown(label="A - Answer",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
            with gr.Column(scale=1):
                gr.Markdown("## B (Output 2)")
                # thought_b = gr.Code(label="B - Thought Process", language='json', lines=12, interactive=False, elem_classes=["custom-fixed-height-code"])
                # json_b = gr.Code(label="B - Answer", language='json', lines=18, interactive=False, elem_classes=["custom-fixed-height-code"])
                thought_b = gr.JSON(label="B - Thought Process",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
                json_b = gr.JSON(label="B - Answer",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])

        with gr.Row(equal_height=True):
            username_compare = gr.Textbox(label="用户名", value="testuser", scale=1)
            compare_dd = gr.Dropdown(label="选择更优", choices=['A更好', 'B更好', '一样好'], scale=2)
            get_btn_compare = gr.Button("获取新对比", variant="secondary", scale=1)
            submit_btn_compare = gr.Button("提交对比", variant="primary", scale=1)
        
        status_compare = gr.Markdown()

        idx_a = gr.State()
        idx_b = gr.State()
        
        get_btn_compare.click(
            fn=get_compare_pair, 
            inputs=[username_compare], 
            outputs=[shared_info_box, data_json, thought_a, json_a, thought_b, json_b, thought_gt, json_gt,compare_dd, idx_a, idx_b]
        )
        submit_btn_compare.click(
            submit_compare, 
            [username_compare, compare_dd, idx_a], 
            outputs=status_compare
        )

    with gr.Tab("进度"):
        username_progress = gr.Textbox(label="用户名", value="testuser")
        progress_md = gr.Markdown()
        get_progress_btn = gr.Button("刷新进度")
        get_progress_btn.click(get_progress, [username_progress], progress_md)

if __name__ == "__main__":
    demo.launch()