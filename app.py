import gradio as gr
from ui.gradio_ui import launch_ui
from logger import get_logger

logger = get_logger("app")

if __name__ == "__main__":
    logger.info("Launching UI")
    launch_ui()