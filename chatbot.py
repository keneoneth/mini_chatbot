import re
import json
from pathlib import Path
from logger import get_logger
from llama_cpp import Llama   # make sure llama-cpp-python is installed

logger = get_logger("chatbot")

HISTORY_DIR = Path("history")
HISTORY_DIR.mkdir(exist_ok=True)

CHAT_MODELS_DIR = Path("chat_models")

# Keys are what you show in the dropdown, values are local GGUF paths
MODEL_CANDIDATES = {
    "TinyLlama": CHAT_MODELS_DIR / "tinyllama-1.1b-chat-v1.0.Q8_0.gguf",
    "Mistral":   CHAT_MODELS_DIR / "mistral-7b-instruct-v0.1.Q2_K.gguf",
    "Qwen":      CHAT_MODELS_DIR / "DeepSeek-R1-0528-Qwen3-8B-UD-Q4_K_XL.gguf",
}

SYSTEM_PROMPT = """
You are a concise chatbot. Answer the user directly.
"""
def messages_to_txt_helper(messages):
    if not messages:
        return ""

    lines = []
    for m in messages:
        role = m.get("role", "unknown")
        content = m.get("content", "")
        lines.append(f"<{role}>: {content}")

    return "\n".join(lines)


class Session:
    def __init__(self, model_id: str, prev_messages=None):
        """
        model_id: one of MODEL_CANDIDATES.keys() (e.g. 'TinyLlama', 'Mistral', 'Qwen')
        messages: list of messages in [{'role':..., 'content':...}] format.
        """
        if model_id not in MODEL_CANDIDATES:
            raise Exception(f"Failed: unknown model_id {model_id}")

        self.model_id = model_id
        self.model_path = MODEL_CANDIDATES[model_id]
        self.messages = prev_messages if prev_messages is not None else []
        self.message_token_counts = []

        self.max_ctx_tokens = 500

        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")

        logger.info(f"Loading model '{self.model_id}' from {self.model_path}")
        
        self.model = Llama(
            model_path=str(self.model_path),
            n_ctx=4096,
            n_threads=8,
            logits_all=False,
            embedding=False
        )

        for m in self.messages:
            self.message_token_counts.append(
                self._count_tokens_single(m["content"])
            )

    def _count_tokens_single(self, text: str) -> int:
        if self.model is None:
            logger.warning(f"Token is counted before model is defined")
            return 0
        toks = self.model.tokenize(text.encode("utf-8"), add_bos=False)
        return len(toks)

    def _build_limited_context(self, new_user_msg: str):
        """
        Return the slice of messages we should send to the model,
        keeping only the last messages that fit the max token window.
        """

        new_msg_tokens = self._count_tokens_single(new_user_msg["content"])
        max_hist_tokens = self.max_ctx_tokens

        running = new_msg_tokens

        prev_i = len(self.message_token_counts)   # start from end
        for i in range(len(self.message_token_counts) - 1, -1, -1):
            t = self.message_token_counts[i]
            if running + t > max_hist_tokens:
                break
            running += t
            prev_i = i

        return [{"role": "system", "content": SYSTEM_PROMPT}] + self.messages[prev_i:] + [new_user_msg]


    def send_prompt(self, prompt: str) -> str:
        new_msg = {"role": "user", "content": prompt}

        ctx_messages = self._build_limited_context(new_msg)
        logger.info(f"Received and created prompt: {ctx_messages}")

        try:
            result = self.model.create_chat_completion(
                messages=ctx_messages,
                temperature=0.3,
                top_p=0.9,
            )
            reply = result["choices"][0]["message"]["content"]

            regex_pattern = r'<think>[\s\S]*?<\/think>'
            reply = re.sub(regex_pattern, '', reply)
            reply = reply.lstrip()

            logger.info(f"Chatbot replied: {reply}")

        except Exception as e:
            logger.error(f"LLM call failed: {e}")
            reply = "Sorry, something went wrong."

        self.messages.append(new_msg)
        self.message_token_counts.append(self._count_tokens_single(prompt))

        self.messages.append({"role": "assistant", "content": reply})
        self.message_token_counts.append(self._count_tokens_single(reply))

        return reply


    def save_history(self, filename):
        try:
            path = HISTORY_DIR / filename
            path.parent.mkdir(exist_ok=True)

            with path.open("w", encoding="utf-8") as f:
                for msg in self.messages:
                    json.dump(msg, f, ensure_ascii=False)
                    f.write("\n")

            download_info = f"✅ Chat history is downloaded to {path}"
            logger.info(download_info)
            return download_info

        except Exception as e:
            download_info = "❌ Chat history download failed."
            logger.error(download_info + f" with exception {e}")
            return download_info

    def load_history(self, filename):
        try:
            # clear old history
            self.messages = []
            self.message_token_counts = []
            with open(filename, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        logger.warning(f"Skipping invalid JSON line: {line}")
                        continue

                    if "role" in entry and "content" in entry:
                        self.messages.append({
                            "role": entry["role"],
                            "content": entry["content"],
                        })
                        self.message_token_counts.append(
                            self._count_tokens_single(entry["content"])
                        )
                    else:
                        logger.warning(f"Skipping line missing role/content: {entry}")
            load_info = f"✅ Chat history is loaded from {filename}"
            logger.info(load_info)
            return load_info
        except Exception as e:
            load_info = "❌ Chat history loading failed."
            logger.error(load_info + f" with exception {e}")
            return load_info


def new_session(model_id: str, prev_messages=None):
    try:
        sess = Session(model_id, prev_messages)
        return sess
    except Exception as e:
        logger.error(f"Failed to create session with {model_id}: {e}")
        return None
