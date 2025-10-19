# SmartAI Chatbot for Frappe/ERPNext

SmartAI Chatbot is a custom Frappe/ERPNext app that brings AI-powered chatbot functionality into your ERP system. It supports multiple AI providers (OpenRouter, Groq, Hugging Face, Google Gemini, etc.) and enables smart conversations inside Frappe.

---

## Features
-  Multi-provider AI support  
-  Real-time chat sessions  
-  AI API Configuration management  
-  Chat history storage  
-  Easy-to-extend architecture  

---

##  Installation

### 1. Clone the repository
```bash
cd ~/frappe-bench/apps
bench get-app  https://github.com/Musab1khan/smartai_chatbot.git
```

### 2. Install the app
```bash
bench --site yoursite.local install-app smartai_chatbot
```

### 3. Migrate & Clear Cache
```bash
bench --site yoursite.local migrate
bench --site yoursite.local clear-cache
```

---

##  Modules & DocTypes

| DocType Name             | Purpose                                      |
|--------------------------|----------------------------------------------|
| AI API Configuration     | Manage AI provider keys & endpoints          |
| Chat Session             | Store user chat sessions                     |
| Chat Message             | Store individual messages in a session       |

---

##  Configuration

1. Open **AI API Configuration**:
   ```
   Desk > AI API Configuration > New
   ```

2. Select a provider (e.g. OpenRouter, Groq, Hugging Face)

3. Enter your **API key** and **model name**

4. Save

---

##  Usage

1. Create a new **Chat Session**
2. Type your message
3. AI response will appear automatically

---

##  Tech Stack

- **Framework**: Frappe/ERPNext  
- **Language**: Python, JavaScript  
- **AI Providers**: OpenRouter, Groq, Hugging Face, Google Gemini, etc.

---
**GitHub**: [Musab1khan](https://github.com/Musab1khan)

---
