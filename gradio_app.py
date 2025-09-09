import gradio as gr
import django
import os


# --- Django Setup ---
# 说明：请确保您的Django项目路径在Python的搜索路径中，
# 并且'data_labelling.settings'是您项目的正确设置模块。
# 例如: sys.path.append('/path/to/your/django_project_folder')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'data_labelling.settings')
django.setup()
DJANGO_AVAILABLE = True
print("Django setup successful. Running in database mode.")

from utils import *
from gradio_tab_function import *
from data_import import *


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

    # session state for memory data
    memory_data_state = gr.State([])

    with gr.Tab("数据导入"):
        gr.Markdown("## 导入 SeedOss-Output.jsonl 和 SeedOss-SFT-Output.jsonl")
        file1_upload = gr.File(label="SeedOss-Output.jsonl 文件", file_types=[".jsonl"])
        file2_upload = gr.File(label="SeedOss-SFT-Output.jsonl 文件", file_types=[".jsonl"])
        import_mode = gr.Radio(["数据库", "内存"], value="数据库", label="导入方式")
        import_status = gr.Markdown()
        import_btn = gr.Button("导入数据")


        def import_data(file1, file2, mode):
            if mode == "数据库":
                msg = import_jsonl_to_db(file1.name, file2.name)
                return gr.update(value=msg), []
            else:
                msg, memory_data = import_jsonl_to_session(file1, file2)
                return msg, memory_data

        import_btn.click(import_data, [file1_upload, file2_upload, import_mode], [import_status, memory_data_state])

    with gr.Tab("两两对比"):
        data_source = gr.Radio(["数据库", "内存"], value="数据库", label="数据来源")
        with gr.Row():
            progress_bar = gr.Slider(label="当前数据索引", minimum=0, maximum=get_total_count(), value=0, step=1)
            prev_btn = gr.Button("上一条")
            next_btn = gr.Button("下一条")
            total_count_md = gr.Markdown()

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
                thought_a = gr.Markdown(label="A - Thought Process",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
                json_a = gr.Markdown(label="A - Answer",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
            with gr.Column(scale=1):
                gr.Markdown("## B (Output 2)")
                thought_b = gr.JSON(label="B - Thought Process",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])
                json_b = gr.JSON(label="B - Answer",show_label=True, container=True, elem_classes=["custom-fixed-height-markdown"])

        def init_view(data_source_val, memory_data):
            idx = 0
            if data_source_val == "数据库":
                result = show_by_index(idx)
            else:
                result = show_by_index_memory(idx, memory_data)
            return result
        demo.load(init_view, [data_source, memory_data_state], [progress_bar, shared_info_box, data_json, thought_a, json_a, thought_b, json_b, thought_gt, json_gt, total_count_md])

        def prev_idx(idx):
            return max(1, int(idx)-1)
        def next_idx(idx, total):
            return min(int(total), int(idx)+1)

        def update_view(idx, total, data_source_val, memory_data):
            if data_source_val == "数据库":
                return show_by_index(prev_idx(idx))
            else:
                return show_by_index_memory(prev_idx(idx), memory_data)

        def update_view_next(idx, total, data_source_val, memory_data):
            if data_source_val == "数据库":
                return show_by_index(next_idx(idx, total))
            else:
                return show_by_index_memory(next_idx(idx, total), memory_data)

        prev_btn.click(update_view, [progress_bar, total_count_md, data_source, memory_data_state], [progress_bar, shared_info_box, data_json, thought_a, json_a, thought_b, json_b, thought_gt, json_gt, total_count_md])
        next_btn.click(update_view_next, [progress_bar, total_count_md, data_source, memory_data_state], [progress_bar, shared_info_box, data_json, thought_a, json_a, thought_b, json_b, thought_gt, json_gt, total_count_md])


if __name__ == "__main__":
    demo.launch()