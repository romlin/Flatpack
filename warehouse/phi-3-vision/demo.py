import gradio as gr
import numpy as np
import os
import re
import torch

from huggingface_hub import snapshot_download
from PIL import Image
from transformers import AutoModelForCausalLM, AutoProcessor

phi3_assistant = '<|assistant|>\n'
phi3_device = torch.device('mps')
phi3_model_name = "microsoft/Phi-3-vision-128k-instruct"
phi3_suffix = "<|end|>\n"
phi3_user = '<|user|>\n'

model_dir = snapshot_download(repo_id=phi3_model_name)
modeling_file_path = os.path.join(model_dir, "modeling_phi3_v.py")

with open(modeling_file_path, "r") as file:
    lines = file.readlines()

with open(modeling_file_path, "w") as file:
    for line in lines:
        if re.match(r"if is_flash_attn_2_available\(\):", line):
            file.write("# " + line)
        elif re.match(r"from flash_attn import flash_attn_func, flash_attn_varlen_func", line):
            file.write("# " + line)
        elif re.match(r"from flash_attn.bert_padding import index_first_axis, pad_input, unpad_input", line):
            file.write("# " + line)
        elif re.match(
                r'_flash_supports_window_size = "window_size" in list\(inspect.signature\(flash_attn_func\).parameters\)',
                line):
            file.write("# " + line)
        else:
            file.write(line)

phi3_processor = AutoProcessor.from_pretrained(
    model_dir,
    trust_remote_code=True
)

phi3_model = AutoModelForCausalLM.from_pretrained(
    model_dir,
    trust_remote_code=True,
    torch_dtype="auto",
    _attn_implementation="eager"
).to(phi3_device)


def inference(input_text, input_image):
    prompt = f"{phi3_user}\n{input_text}{phi3_suffix}{phi3_assistant}"

    images = [Image.fromarray(input_image)] if isinstance(input_image, np.ndarray) else [input_image] if isinstance(
        input_image, Image.Image) else None

    print(f"Prompt\n{prompt}")

    inputs = phi3_processor(prompt, images=images, return_tensors="pt").to(phi3_device)

    inference_ids = phi3_model.generate(
        **inputs,
        max_new_tokens=1000,
        eos_token_id=phi3_processor.tokenizer.eos_token_id
    )[:, inputs['input_ids'].shape[1]:]

    response = phi3_processor.batch_decode(
        inference_ids,
        skip_special_tokens=True,
        clean_up_tokenization_spaces=False
    )[0]

    print(f'Response\n{response}')
    return response


def main():
    with gr.Blocks() as page:
        gr.Interface(
            fn=inference,
            inputs=[gr.Textbox(), gr.Image(type="pil")],
            outputs=gr.TextArea(label="decoded text")
        )
    page.launch(inbrowser=True)


if __name__ == "__main__":
    main()