# Mini Local Chatbot (llama.cpp + Gradio)

This project is a lightweight local chatbot built using **llama.cpp** with a **Gradio** web interface.  
It supports multiple open-source language models, allows switching between them instantly, and includes full chat-history management — all running **fully offline** on your own machine.

## 🚀 Features

### 🧠 Multiple Local Models (via llama.cpp)

- **TinyLlama-1.1B-Chat (Q8_0)** — ultra-fast and lightweight  
- **Mistral-7B-Instruct (Q2_K)** — stronger reasoning with low memory usage  
- **DeepSeek-R1-Qwen3-8B (Q4_K_XL)** — deeper answers with slower speed  

### 🌐 Gradio Web UI

- Clean, responsive browser interface  
- One-click model switching  
- Smooth message display  

### 💾 Chat History Management

- Download current conversation as JSON  
- Upload & load past chat histories  
- All files saved inside the `history/` directory  

### 🔒 100% Local Execution

- No API calls, no network dependency  
- Ideal for private, offline, or on-device use  
- No API calls, no network dependency
- Ideal for private, offline, or on-device use

## 🎥 Demo GIFs
### 💬 Ask the Chatbot
![ask_chatbot](https://github.com/user-attachments/assets/0d1ebf6d-80b8-4359-9efa-7df206973a95)

### 📥 Download Chat History
![download_history](https://github.com/user-attachments/assets/d52c3b94-c83f-4050-a15c-bb89a3fa928e)

### 📤 Upload Chat History
![upload_history](https://github.com/user-attachments/assets/0d442daf-d37e-4933-99af-9553138bcc0e)

### 🔀 Switch Models
![switch_model](https://github.com/user-attachments/assets/50ce08fa-87bf-4fd4-9742-e49aa9cd5333)

## 📁 Repository Structure
mini_chatbot/
├── app.py                 # Main launcher for the Gradio UI  
├── chatbot.py             # Backend logic + llama.cpp wrapper  
├── download.sh            # Downloads all model files  
├── requirements.txt       # Python dependencies  
├── history/               # Stored chat histories (JSON)  
└── ui/                    # UI helper components  

## 🛠 Installation
1. Clone the repository
`git clone https://github.com/your-username/mini_chatbot.git`
`cd mini_chatbot`

2. (Optional) Create a virtual environment

`python -m venv .venv
source .venv/bin/activate`

3. Install dependencies
`pip install -r requirements.txt`

4. Download models
Use the included script:

`chmod +x download.sh
./download.sh`


This fetches all required GGUF model files into the proper folders.  

## ▶️ Running the Chatbot
Start the Gradio UI:
`python app.py`

Then open:
`http://127.0.0.1:7860`


You can now:
✔ Select a model  
✔ Chat normally  
✔ Save / load chat history  
✔ Switch models mid-session  

## 📝 Usage Notes

- TinyLlama is best for speed and quick replies.

- Mistral < Qwen are better for quality and depth, but will take more processing time, especially on CPU.

- History files are standard JSONL format and editable.

- All computation is local — suitable for private or offline applications.
