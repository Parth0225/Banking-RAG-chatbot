import streamlit as st
from src import config
from src.ingest import ingest, get_collection
from src.rag import RAGChatbot

st.set_page_config(page_title="Banking & Finance RAG Chatbot", page_icon="🏦")
st.title("🏦 Banking & Finance Assistant")
st.caption("Answers grounded in your PDF knowledge base.")

with st.sidebar:
    st.header("Knowledge base")
    st.write(f"PDFs folder: `{config.PDF_DIR}`")
    try:
        st.metric("Indexed chunks", get_collection().count())
    except Exception:
        st.metric("Indexed chunks", 0)
    if st.button("Re-index PDFs"):
        with st.spinner("Indexing..."):
            ingest(reset=True, progress=lambda m: None)
        st.success("Indexing complete")
        st.rerun()
    if st.button("Clear chat"):
        st.session_state.messages = []
        st.rerun()

@st.cache_resource
def load_bot():
    return RAGChatbot()

try:
    bot = load_bot()
except Exception as e:
    st.error(str(e))
    st.stop()

st.session_state.setdefault("messages", [])
for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

if q := st.chat_input("Ask a banking or finance question..."):
    history = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]
    st.session_state.messages.append({"role": "user", "content": q})
    with st.chat_message("user"):
        st.markdown(q)
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            answer, hits = bot.ask(q, history)
        st.markdown(answer)
        with st.expander("Sources"):
            for h in hits:
                st.markdown(f"**{h['source']}** (p.{h['page']})")
                st.caption(h["text"][:300] + "...")
    st.session_state.messages.append({"role": "assistant", "content": answer})
