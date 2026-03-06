# 🧠 ClariCode – AI Powered Code Learning Platform

<div align="center">

ClariCode is an **AI-powered educational coding platform** designed for students and beginners who want to **understand their code**, not just run it.  

**Paste your code → Get AI analysis → Learn what went wrong → Fix it instantly.**

</div>

---

## 📋 How ClariCode Works


┌───────────────────────────────────────────────────────────────┐
│ │
│ 📋 PASTE CODE ──▶ 🤖 AI ANALYSIS ──▶ 💡 UNDERSTAND FIX │
│ │
│ 💬 ASK AI ──▶ 📚 GET CONCEPT ──▶ ✅ LEARN & GROW │
│ │
│ ⚡ COMPILE ──▶ 📤 SEE OUTPUT ──▶ 🔄 ITERATE FAST │
│ │
└───────────────────────────────────────────────────────────────┘


---

## ✨ Features

| Feature | Description |
|--------|-------------|
| 🔍 **AI Code Analysis** | Paste code and get concept explanation, error detection, fixed code, and explanation |
| 💬 **Ask AI** | Chat with AI mentor to learn programming concepts |
| ⚡ **Online Compiler** | Run code directly in browser (40+ languages) |
| 🔄 **Code Converter** | Convert code from one language to another |
| 🧪 **Dual Code Slots** | Run two programs side-by-side |
| 📍 **Line-level Errors** | AI detects exact line where bug exists |
| 🎨 **Clean Output UI** | W3Schools style output panel |

---

## 🏗️ Tech Stack


┌──────────────────────────────────────┐
│ FRONTEND │
│ HTML5 · CSS3 · Vanilla JavaScript │
│ Custom UI · Dark Cyber Theme │
└───────────────┬──────────────────────┘
│
┌───────────────▼──────────────────────┐
│ BACKEND │
│ Python 3.10+ · Flask · Blueprints │
│ python-dotenv · requests │
└───────────────┬──────────────────────┘
│
┌────────┴────────┐
│ │
┌──────▼──────┐ ┌──────▼─────────┐
│ GROQ AI │ │ Code Execution │
│ LLaMA 3.1 │ │ Judge0 / │
│ AI Analysis │ │ OneCompiler │
└─────────────┘ └───────────────┘


---

## 📁 Project Structure


ClariCode-AI/

backend/
│
├── app.py
├── llm_engine.py
├── compiler_engine.py
├── onecompiler_integration.py
├── error_analyzer.py
├── code_converter.py
├── validator.py
├── formatter.py
├── config.py
├── requirements.txt
├── .env

routes/
├── analyze_code.py
├── compiler.py
├── chat.py
└── submit_practice.py

templates/
└── index.html

static/
├── style.css
├── compiler.js
└── script.js

README.md


---

## 🚀 Getting Started

### 1️⃣ Clone Repository


git clone https://github.com/yourusername/ClariCode-AI.git
cd ClariCode-AI
2️⃣ Install Dependencies
cd backend
pip install -r requirements.txt
3️⃣ Configure API Keys

Create file:

backend/.env

Add your API keys:

GROQ_API_KEY=your_groq_key_here
ONECOMPILER_API_KEY=your_onecompiler_key_here
SECRET_KEY=your_secret_key
FLASK_DEBUG=True
4️⃣ Run Application
cd backend
python app.py

Open browser:

http://localhost:5000
🔍 Code Analysis Flow
User Pastes Code
       │
       ▼
POST /analyze
       │
       ▼
Groq LLaMA 3.1 AI
       │
       ▼
AI returns structured analysis:

✔ Concept
✔ Explanation
✔ Error Type
✔ Error Line
✔ Error Description
✔ Fixed Code
✔ Fix Explanation
⚡ Compiler Flow
User Writes Code
       │
       ▼
POST /compiler/run
       │
       ▼
OneCompiler API Executes Code
       │
       ▼
Output or Error
       │
       ▼
AI gives explanation
📸 Screenshots
Code Analysis	Compiler	AI Feedback
Screenshot	Screenshot	Screenshot
🛣️ Future Roadmap

User login system

Code history saving

Coding challenges

Leaderboard

VS Code extension

Mobile App

🤝 Contributing
git checkout -b feature/newFeature
git commit -m "Added new feature"
git push origin feature/newFeature

Create a Pull Request.

⚠️ Important

Never upload .env file to GitHub

Your API keys must remain private


<div align="center">

Built with ❤️ by ClariCode Team

⭐ Star this repository if you like the project ⭐

</div> 
