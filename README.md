# 🎓 AI Scholarship Assistant PRO

An AI-powered Scholarship Analysis and Recommendation System built using Streamlit, RAG (Retrieval-Augmented Generation), FAISS, Sentence Transformers, and OpenAI LLM integration.

The system helps students analyze scholarship documents, extract important information, evaluate eligibility, calculate scholarship match scores, and interact with uploaded scholarship PDFs using an intelligent AI chatbot.

---

## 🚀 Features

### 📄 Scholarship PDF Analysis
- Upload scholarship PDF documents
- Extract text automatically
- Preview document content
- Process large scholarship files

### 🧠 AI-Powered RAG Chatbot
- Ask questions directly from uploaded PDFs
- Context-aware retrieval using FAISS
- Semantic search using Sentence Transformers
- OpenAI GPT integration
- Hallucination reduction with RAG architecture

### 📌 Scholarship Insights
Automatically extracts:

- Scholarship Type
- Scholarship Amount
- Application Deadline
- Eligibility Criteria
- Important Requirements

### 📊 Scholarship Match Score
Calculates scholarship suitability using:

- Family Income
- CGPA
- Category
- Course

Provides a percentage-based match score.

### 🔍 Smart Search
- Keyword search inside uploaded PDF
- Semantic document retrieval
- Fast information discovery

### 💬 Interactive Chat Experience
- Chat history
- Suggested questions
- Message timestamps
- Export chat
- Clear chat
- Modern UI

### 📤 Report Export
Generate:

- Scholarship Summary
- Eligibility Report
- AI Analysis Report

---

## 🏗️ System Architecture

```text
PDF Upload
    │
    ▼
PDF Text Extraction
    │
    ▼
Text Chunking
    │
    ▼
Sentence Embeddings
(all-MiniLM-L6-v2)
    │
    ▼
FAISS Vector Database
    │
    ▼
Semantic Search
    │
    ▼
Relevant Context Retrieval
    │
    ▼
OpenAI GPT
    │
    ▼
AI Scholarship Answer
```

---

## 🛠️ Technologies Used

### Frontend
- Streamlit

### AI & NLP
- OpenAI GPT
- Sentence Transformers
- Transformers

### Vector Database
- FAISS

### PDF Processing
- PyPDF

### Data Processing
- NumPy
- Pandas

### Backend
- Python

---

## 📂 Project Structure

```text
Scholarship_Assistant/
│
├── app.py
├── granite_ai.py
├── rag_pipeline.py
├── pdf_loader.py
├── report_generator.py
├── database.py
├── login.py
├── admin.py
│
├── scholarship_data/
│
├── reports/
│
├── requirements.txt
│
└── README.md
```

---

## ⚙️ Installation

### Clone Repository

```bash
git clone https://github.com/yourusername/AI-Scholarship-Assistant.git

cd AI-Scholarship-Assistant
```

### Create Virtual Environment

```bash
python -m venv venv
```

### Activate Environment

Windows

```bash
venv\Scripts\activate
```

Linux/Mac

```bash
source venv/bin/activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 OpenAI Configuration

Create a `.env` file

```env
OPENAI_API_KEY=your_api_key_here
```

Or configure directly inside the project settings.

---

## ▶️ Run Application

```bash
streamlit run app.py
```

Application will start at:

```text
http://localhost:8501
```

---

## 📊 Workflow

### Step 1
Upload Scholarship PDF

### Step 2
System extracts document content

### Step 3
FAISS vector database is created

### Step 4
AI generates:

- Summary
- Eligibility
- Deadline
- Scholarship Amount
- Category

### Step 5
Student enters profile details

### Step 6
System calculates Match Score

### Step 7
Ask questions using AI Chatbot

---

## 🎯 Example Questions

```text
What is the scholarship amount?

Who is eligible for this scholarship?

What documents are required?

What is the application deadline?

How can I apply?

Is there any income limit?

What is the selection process?

What benefits are provided?
```

---

## 🔒 Future Enhancements

- Multi-PDF Analysis
- Scholarship Recommendation Engine
- OCR Support for Scanned PDFs
- Email Notifications
- Admin Dashboard
- Student Login Portal
- Scholarship Database Integration
- Application Tracking System
- Resume Analysis
- Voice Chat Assistant
- Multilingual Support

---

## 📈 Academic Project Highlights

This project demonstrates:

- Artificial Intelligence
- Retrieval Augmented Generation (RAG)
- Natural Language Processing
- Semantic Search
- Vector Databases
- Large Language Models
- Document Intelligence
- Information Retrieval
- Streamlit Application Development

---

## 👩‍💻 Author

**Bhavatharani**

AI Scholarship Assistant PRO

Built for Academic Project Submission using AI, RAG, FAISS, OpenAI GPT, and Streamlit.

---

## 📜 License

This project is licensed under the MIT License.

Feel free to use, modify, and distribute for educational purposes.
