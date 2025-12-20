# FILE: streamlit_app.py
"""
KEITH Manufacturing Team Member Handbook AI Assistant
=====================================================
Agentic RAG chatbot specifically for the KEITH Employee Handbook.
No upload required - handbook is pre-indexed.
"""

import streamlit as st
import os

from rag.agent import AgenticRAG
from rag.indexer import check_index_exists, index_handbook

# Page configuration
st.set_page_config(
    page_title="KEITH Handbook Assistant",
    page_icon="📘",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Custom CSS for KEITH branding
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        font-weight: bold;
        margin-bottom: 0.5rem;
        color: #1a5276;
    }
    .sub-header {
        font-size: 1rem;
        color: #666;
        margin-bottom: 1rem;
    }
    .source-item {
        padding: 0.5rem;
        margin: 0.25rem 0;
        background-color: #f0f2f6;
        border-radius: 0.25rem;
        font-size: 0.85rem;
        border-left: 3px solid #1a5276;
        color: #1a1a1a !important;
    }
    .source-item b {
        color: #1a5276 !important;
    }
    .source-item small {
        color: #666 !important;
    }
    .reasoning-step {
        padding: 0.25rem 0.5rem;
        margin: 0.1rem 0;
        border-left: 3px solid #2ecc71;
        font-size: 0.85rem;
    }
    .keith-banner {
        background: linear-gradient(90deg, #1a5276 0%, #2980b9 100%);
        color: white;
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .status-ready {
        color: #27ae60;
        font-weight: bold;
    }
    .status-processing {
        color: #f39c12;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Constants
PINECONE_NAMESPACE = "keith-handbook-jan2025"


def init_session_state():
    """Initialize session state variables."""
    defaults = {
        "messages": [],
        "indexed": False,
        "agent": None,
        "sources_used": [],
        "reasoning_steps": [],
        "status": "",
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def check_secrets() -> tuple[bool, list[str]]:
    """Check if all required secrets are configured."""
    required = ["OPENAI_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME"]
    missing = []
    for secret in required:
        if secret not in st.secrets:
            missing.append(secret)
    return len(missing) == 0, missing


def update_status(message: str):
    """Update status in session state."""
    st.session_state.status = message


def initialize_system():
    """Initialize the RAG system - check/create index and agent."""
    if st.session_state.agent is not None:
        return True
    
    try:
        # Check if handbook is already indexed
        update_status("🔍 Checking index status...")
        
        is_indexed = check_index_exists(
            api_key=st.secrets["PINECONE_API_KEY"],
            index_name=st.secrets["PINECONE_INDEX_NAME"],
            namespace=PINECONE_NAMESPACE
        )
        
        if not is_indexed:
            update_status("📚 First-time setup: Indexing KEITH Handbook...")
            index_handbook(
                openai_api_key=st.secrets["OPENAI_API_KEY"],
                pinecone_api_key=st.secrets["PINECONE_API_KEY"],
                index_name=st.secrets["PINECONE_INDEX_NAME"],
                namespace=PINECONE_NAMESPACE
            )
        
        # Initialize agent
        update_status("🤖 Initializing AI assistant...")
        st.session_state.agent = AgenticRAG(
            openai_api_key=st.secrets["OPENAI_API_KEY"],
            pinecone_api_key=st.secrets["PINECONE_API_KEY"],
            index_name=st.secrets["PINECONE_INDEX_NAME"],
            namespace=PINECONE_NAMESPACE,
            status_callback=update_status
        )
        
        st.session_state.indexed = True
        update_status("")
        return True
        
    except Exception as e:
        update_status(f"❌ Error: {str(e)}")
        st.error(f"Failed to initialize: {str(e)}")
        return False


def reset_chat():
    """Reset chat history."""
    st.session_state.messages = []
    st.session_state.sources_used = []
    st.session_state.reasoning_steps = []


def main():
    """Main application entry point."""
    init_session_state()
    
    # Header with KEITH branding
    st.markdown("""
    <div class="keith-banner">
        <h1 style="margin:0; font-size:1.8rem;">📘 KEITH Manufacturing</h1>
        <p style="margin:0; opacity:0.9;">Team Member Handbook AI Assistant</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check secrets
    secrets_ok, missing_secrets = check_secrets()
    if not secrets_ok:
        st.error(f"⚠️ Missing required secrets: {', '.join(missing_secrets)}")
        st.info("""
        Please configure the following secrets in your Streamlit app settings:
        ```toml
        OPENAI_API_KEY = "sk-..."
        PINECONE_API_KEY = "..."
        PINECONE_INDEX_NAME = "keith-handbook"
        ```
        """)
        return
    
    # Initialize system
    if not st.session_state.indexed:
        with st.spinner("Setting up KEITH Handbook Assistant..."):
            if not initialize_system():
                return
        st.rerun()
    
    # Status bar
    col_status, col_reset = st.columns([4, 1])
    with col_status:
        if st.session_state.status:
            st.info(st.session_state.status)
        else:
            st.markdown('<span class="status-ready">✅ Ready - Ask me anything about the KEITH Employee Handbook!</span>', unsafe_allow_html=True)
    
    with col_reset:
        if st.button("🔄 New Chat", use_container_width=True):
            reset_chat()
            st.rerun()
    
    st.markdown("---")
    
    # Main content area: Chat + Sources
    chat_col, info_col = st.columns([2, 1])
    
    with chat_col:
        st.markdown("### 💬 Chat")
        
        # Chat container
        chat_container = st.container(height=450)
        
        with chat_container:
            # Welcome message if no messages
            if not st.session_state.messages:
                st.markdown("""
                👋 **Welcome to the KEITH Handbook Assistant!**
                
                I can help you find information about:
                - 🏖️ **Time-off** - Vacation, sick pay, personal time
                - 💰 **Benefits** - Health insurance, 401(k), etc.
                - 📋 **Policies** - Dress code, cell phones, safety
                - 📅 **Leave** - FMLA, OFLA, Paid Leave Oregon
                - 🔧 **Procedures** - Internal transfers, termination
                
                *Ask me a question to get started!*
                """)
            
            # Display chat history
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask a question about the KEITH Employee Handbook..."):
            # Add user message
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Process with agent
            if st.session_state.agent:
                with st.spinner("Thinking..."):
                    try:
                        result = st.session_state.agent.answer(prompt)
                        
                        # Store results
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": result["answer"]
                        })
                        st.session_state.sources_used = result.get("sources", [])
                        st.session_state.reasoning_steps = result.get("reasoning_steps", [])
                        
                    except Exception as e:
                        error_msg = f"Sorry, I encountered an error: {str(e)}. Please try again."
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": error_msg
                        })
            
            st.rerun()
    
    with info_col:
        # Sources Used
        st.markdown("### 📎 Sources Used")
        sources_container = st.container(height=200)
        with sources_container:
            if st.session_state.sources_used:
                for source in st.session_state.sources_used[:5]:
                    page = source.get("page_number", "?")
                    title = source.get("section_title", "Unknown Section")
                    score = source.get("score", 0)
                    st.markdown(
                        f'<div class="source-item">📄 <b>Page {page}</b> — {title}<br><small>Relevance: {score:.0%}</small></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("*Sources will appear here after you ask a question.*")
        
        # Agent Reasoning
        st.markdown("### 🧠 Agent Reasoning")
        reasoning_container = st.container(height=200)
        with reasoning_container:
            if st.session_state.reasoning_steps:
                for step in st.session_state.reasoning_steps:
                    icon = {
                        "planning": "📋",
                        "plan-created": "✅",
                        "searching": "🔍",
                        "results": "📊",
                        "evaluating": "⚖️",
                        "evaluation": "📈",
                        "re-searching": "🔄",
                        "generating": "✍️",
                        "self-critique": "🔎",
                        "critique-result": "✅",
                        "revision": "📝",
                        "complete": "🎯",
                        "error": "❌"
                    }.get(step.get("type", ""), "▶️")
                    desc = step.get("description", step.get("step", ""))
                    st.markdown(
                        f'<div class="reasoning-step">{icon} {desc}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown("*Reasoning steps will appear here during Q&A.*")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <small>
    📞 <b>HR Contact:</b> 541-475-3802 | 📍 401 NW Adler St, Madras, OR 97741<br>
    <i>Handbook Revision: January 2025 | For complex situations, please contact Human Resources directly.</i>
    </small>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
