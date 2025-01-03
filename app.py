import os
import gradio as gr

from api.audio import STTManager, TTSManager
from api.llm import LLMManager
from utils.config import Config
from resources.prompts import prompts
from ui.coding import get_problem_solving_ui
from utils.params import default_audio_params


def initialize_services():
    """
    Initialize configuration, LLM, TTS, and STT services.

    Returns:
        tuple: Containing Config, LLMManager, TTSManager, and STTManager instances.
    """
    config = Config()
    llm = LLMManager(config, prompts)
    tts = TTSManager(config)
    stt = STTManager(config)

    # Update default audio parameters with STT streaming setting
    default_audio_params["streaming"] = stt.streaming
    print(stt.streaming)

    # Disable TTS in silent mode
    if os.getenv("SILENT", False):
        tts.read_last_message = lambda x: None

    return config, llm, tts, stt


def create_interface(llm, tts, stt, audio_params):
    """
    Create and configure the Gradio interface.

    Args:
        llm (LLMManager): Language model manager instance.
        tts (TTSManager): Text-to-speech manager instance.
        stt (STTManager): Speech-to-text manager instance.
        audio_params (dict): Audio parameters for the interface.

    Returns:
        gr.Blocks: Configured Gradio interface.
    """
    # 使用Blocks API创建应用
    with gr.Blocks(title="AI Interviewer", theme=gr.themes.Default()) as demo:
        audio_output=gr.Audio(sources="microphone", type="numpy", label="Play audio", autoplay=True, visible=os.environ.get("DEBUG", False), streaming=tts.streaming)

        # Render problem-solving and instructions UI components
        print("function create_interface")
        print("audio_params:")
        print(audio_params)
        
        get_problem_solving_ui(llm, tts, stt, audio_params, audio_output).render()

    return demo


def main():
    """
    Main function to initialize services and launch the Gradio interface.
    """
    config, llm, tts, stt = initialize_services()
    demo = create_interface(llm, tts, stt, default_audio_params)

    # Launch the Gradio interface
    demo.launch(show_api=False, share=True, debug=True)


if __name__ == "__main__":
    main()
