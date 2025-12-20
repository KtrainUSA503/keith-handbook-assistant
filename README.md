# 📘 KEITH Manufacturing Handbook AI Assistant

An **Agentic RAG** chatbot specifically built for the KEITH Manufacturing Team Member Handbook (January 2025 Edition).

**No upload required** - the handbook is pre-indexed and ready to use!

## ✨ Features

- **Pre-Loaded Handbook**: January 2025 Team Member Handbook is embedded - no uploading needed
- **Agentic RAG**: Multi-step reasoning with planning, search, evaluation, and self-critique
- **KEITH-Specific**: Understands vacation caps, accrual rates, FMLA/OFLA, and all company policies
- **Accurate Calculations**: Properly handles policy limits like the 150% vacation cap
- **Source Citations**: Shows exactly which handbook pages were used
- **Transparent Reasoning**: Watch the AI's thinking process in real-time

## 🚀 Deploy to Streamlit Cloud

### Step 1: Push to GitHub

```bash
git init
git add .
git commit -m "KEITH Handbook AI Assistant"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/keith-handbook-assistant.git
git push -u origin main
```

### Step 2: Deploy on Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click **"New app"**
3. Select your repository
4. Set Main file path: `streamlit_app.py`
5. Click **Deploy**

### Step 3: Add Secrets

In your deployed app settings, add these secrets:

```toml
OPENAI_API_KEY = "sk-your-openai-key"
PINECONE_API_KEY = "your-pinecone-key"
PINECONE_INDEX_NAME = "keith-handbook"
```

## 💡 Example Questions

- "How much vacation do I accrue per pay period in my 3rd year?"
- "What's the vacation cap and what happens if I hit it?"
- "What are the 6 paid holidays?"
- "How do I request time off?"
- "What's the difference between FMLA and OFLA?"
- "What's the dress code?"
- "How does the tardy policy work?"
- "Who is on the Leadership Team?"

## 📋 Handbook Coverage

The AI can answer questions about:
- Time-Off Program (Vacation, Sick, Personal Unpaid)
- Benefits (Health, Dental, Vision, 401k)
- Leave policies (FMLA, OFLA, Paid Leave Oregon)
- Workplace policies (Dress code, Cell phones, Safety)
- Attendance and Tardiness
- Employment categories and onboarding
- And more...

## 🔧 Technical Details

- **Model**: GPT-4o for high-quality reasoning
- **Embeddings**: text-embedding-3-small (1536 dimensions)
- **Vector DB**: Pinecone Serverless
- **Framework**: Streamlit

## 📞 Contact

For complex HR situations, contact KEITH Manufacturing HR directly:
- **Phone**: 541-475-3802
- **Hours**: Monday-Friday, 6:00 AM - 4:30 PM

---

*Handbook Revision: January 2025*
