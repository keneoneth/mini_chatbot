import gradio as gr
from datetime import datetime
from chatbot import new_session, MODEL_CANDIDATES, messages_to_txt_helper
from logger import get_logger

logger = get_logger("UI")

CURRENT_MODEL_ID = "TinyLlama" # default is tiny llama model
sess = None

def init_session():
    """Ensure we have a session for the current model."""
    global sess
    if sess is None:
        model_id = CURRENT_MODEL_ID
        logger.info(f"[init_session] creating new session for model={model_id}")
        sess = new_session(model_id=model_id)

def check_health():
    if sess == None:
        mssg = "❌ Chat session init failed."
        logger.info(mssg)
        return mssg
    else:
        mssg = "✅ Chat session is ready."
        logger.info(mssg)
        return mssg

def chat_fn(chat, user_text):
    new_messages = []
    new_messages.append({"role" : "user","content" : user_text})
    reply = sess.send_prompt(user_text)
    new_messages.append({"role" : "assistant", "content" : reply})
    return chat + ("\n" if chat != "" else "") + messages_to_txt_helper(new_messages), ""

def switch_model(model_id: str):
    """
    Called when user clicks 'Switch model'.
    Creates a new session for the selected model and clears the visible chat.
    """
    global CURRENT_MODEL_ID, sess
    CURRENT_MODEL_ID = model_id

    model_id = CURRENT_MODEL_ID
    logger.info(f"[switch_model] switching to {model_id}")

    # create a fresh session for this model
    sess = new_session(model_id=model_id,prev_messages=sess.messages)

    status_text = f"✅ Switched to **{model_id}**"
    return status_text

def do_upload(file, original_chat):
    """
    Load a saved history file and replace sess.
    """
    global sess
    if file is None:
        return "❌ No file selected.", original_chat
    if not file.endswith(".jsonl"):
        return "❌ Invalid file format.", original_chat

    logger.info(f"Uploading chat history from {file}")
    load_info = sess.load_history(file.name)
    return load_info, messages_to_txt_helper(sess.messages)

def do_download():
    """
    Download current session history.
    """
    def make_filename(model_id: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        return f"{timestamp}_{model_id}.jsonl"
    logger.info("Downloading chat history")
    filename = make_filename(CURRENT_MODEL_ID)
    download_info = sess.save_history(filename)
    return download_info

def launch_ui():
    global sess

    # init the chat session at app launch
    init_session()

    # populate the UI here
    with gr.Blocks() as app:
        gr.Markdown("<Mini Chatbot>")

        status = gr.Markdown(label="Status", value=check_health())
        with gr.Row():
            model_dropdown = gr.Dropdown(
                choices=list(MODEL_CANDIDATES.keys()),
                value=CURRENT_MODEL_ID,
                label="Select model"
            )
            switch_btn = gr.Button("Switch model")
        chat = gr.Textbox(lines=12, label="Chat history", interactive=False)
        inp = gr.Textbox(lines=5, label="Your message")
        send = gr.Button("Send")

        with gr.Row():
            download = gr.Button("Download history")
            upload = gr.File(label="Upload history")
            loadbtn = gr.Button("Load history")

        inp.submit(
            chat_fn, 
            inputs=[chat, inp], 
            outputs=[chat,inp]
        )

        send.click(
            chat_fn,
            inputs=[chat, inp],
            outputs=[chat,inp],
        )

        switch_btn.click(
            switch_model,
            inputs=[model_dropdown],
            outputs=[status],
        )

        download.click(do_download, inputs=[], outputs=[status])
        loadbtn.click(do_upload, inputs=[upload,chat], outputs=[status, chat])


    app.launch()