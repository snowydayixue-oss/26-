import streamlit as st
from zhipuai import ZhipuAI
from PyPDF2 import PdfReader
from docx import Document
import tempfile
import os
import docx2txt

API_KEY = "e0f24eeeefd74220b7f0a265d7b69b86.yAY5Uy7wBOIkxW5u"
client = ZhipuAI(api_key=API_KEY)

st.set_page_config(page_title="智能文档问答系统", page_icon="📄", layout="wide")

st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
}
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
}
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label,
[data-testid="stSidebar"] div,
[data-testid="stSidebar"] small {
    color: white !important;
}
[data-testid="stSidebar"] .stButton button {
    background: rgba(233,69,96,0.8);
    border: none !important;
    color: white !important;
    border-radius: 10px;
}
[data-testid="stSidebar"] .stButton button:hover {
    background: #e94560 !important;
}
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.08) !important;
    border: 2px dashed rgba(255,255,255,0.4) !important;
    border-radius: 12px !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] div[data-testid="stMarkdownContainer"] p {
    visibility: hidden;
    position: relative;
}
[data-testid="stFileUploaderDropzoneInstructions"] div[data-testid="stMarkdownContainer"] p::after {
    visibility: visible;
    position: absolute;
    left: 0;
    content: "拖拽文件到此处";
    color: white !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] small {
    visibility: hidden;
    position: relative;
}
[data-testid="stFileUploaderDropzoneInstructions"] small::after {
    visibility: visible;
    position: absolute;
    left: 0;
    content: "支持PDF、DOCX、DOC、TXT";
    color: rgba(255,255,255,0.7) !important;
    white-space: nowrap;
}
[data-testid="stBaseButton-secondary"] {
    background: rgba(233,69,96,0.8) !important;
    border: none !important;
    color: white !important;
    border-radius: 8px !important;
}
[data-testid="stBaseButton-secondary"]:hover {
    background: #e94560 !important;
}
.main-title {
    background: linear-gradient(90deg, #1a1a2e, #0f3460, #e94560);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-size: 2.8em;
    font-weight: 900;
}
.feature-card {
    background: white;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    border-top: 4px solid;
    height: 170px;
}
.card-blue { border-color: #4361ee; }
.card-purple { border-color: #7209b7; }
.card-pink { border-color: #e94560; }
.card-icon { font-size: 2em; margin-bottom: 8px; }
.card-title { font-weight: 700; font-size: 1.1em; color: #1a1a2e; margin-bottom: 6px; }
.card-desc { color: #666; font-size: 0.9em; }
.welcome-banner {
    background: linear-gradient(135deg, #1a1a2e 0%, #0f3460 100%);
    border-radius: 20px;
    padding: 40px;
    text-align: center;
    margin: 20px 0;
    box-shadow: 0 8px 32px rgba(15,52,96,0.3);
}
.welcome-banner h2 { color: white !important; font-size: 1.8em; margin-bottom: 10px; }
.welcome-banner p { color: rgba(255,255,255,0.85) !important; font-size: 1.1em; }
.chat-header {
    background: white;
    border-radius: 16px;
    padding: 16px 24px;
    margin-bottom: 16px;
    box-shadow: 0 2px 12px rgba(0,0,0,0.06);
    border-left: 5px solid #4361ee;
    color: #1a1a2e;
}
.step-item {
    display: flex;
    align-items: center;
    gap: 10px;
    background: rgba(255,255,255,0.08);
    border-radius: 10px;
    padding: 10px 14px;
    margin: 6px 0;
    color: white;
    font-size: 0.9em;
}
.step-num {
    background: #e94560;
    color: white;
    border-radius: 50%;
    width: 22px;
    height: 22px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.8em;
    font-weight: bold;
    flex-shrink: 0;
}
.sidebar-title { color: white !important; font-size: 1.3em; font-weight: 700; }
.sidebar-sub { color: rgba(255,255,255,0.6) !important; font-size: 0.85em; }
.sidebar-section { color: white !important; font-size: 1em; font-weight: 600; margin: 12px 0 6px 0; }
.success-toast {
    background: #4CAF50;
    color: white;
    padding: 10px 20px;
    border-radius: 10px;
    text-align: center;
    font-weight: bold;
    margin: 8px 0;
}
</style>
""", unsafe_allow_html=True)

def read_file(uploaded_file):
    text = ""
    if uploaded_file.name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        for page in reader.pages:
            text += page.extract_text() or ""
    elif uploaded_file.name.endswith(".docx"):
        doc = Document(uploaded_file)
        for para in doc.paragraphs:
            text += para.text + "\n"
    elif uploaded_file.name.endswith(".doc"):
        with tempfile.NamedTemporaryFile(delete=False, suffix=".doc") as tmp:
            tmp.write(uploaded_file.read())
            tmp_path = tmp.name
        try:
            text = docx2txt.process(tmp_path)
        except Exception as e:
            text = f"读取失败：{str(e)}"
        finally:
            try:
                os.unlink(tmp_path)
            except:
                pass
    elif uploaded_file.name.endswith(".txt"):
        text = uploaded_file.read().decode("utf-8")
    return text

# 初始化状态
if "messages" not in st.session_state:
    st.session_state.messages = []
if "doc_text" not in st.session_state:
    st.session_state.doc_text = ""
if "show_uploader" not in st.session_state:
    st.session_state.show_uploader = True

# ===== 侧边栏 =====
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-title'>📄 智能文档问答</div>", unsafe_allow_html=True)
    st.markdown("<div class='sidebar-sub'>基于大语言模型 · 吕婷欣</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("<div class='sidebar-section'>📂 上传文档</div>", unsafe_allow_html=True)

    uploaded_file = st.file_uploader("上传文档", type=["pdf","docx","doc","txt"], label_visibility="collapsed")

    if uploaded_file:
        st.success(f"✅ {uploaded_file.name}")
        doc_text = read_file(uploaded_file)
        st.session_state.doc_text = doc_text
        st.info(f"📝 读取了 {len(doc_text)} 个字符")

    st.markdown("---")

    # 清除对话按钮
    if st.button("🗑️ 清除对话记录", use_container_width=True):
        st.session_state.messages = []
        st.toast("✅ 对话记录已清除！", icon="🗑️")
        st.rerun()

    # 重新上传按钮
    if st.button("📤 重新上传文档", use_container_width=True):
        st.session_state.messages = []
        st.session_state.doc_text = ""
        st.toast("✅ 请重新上传文档！", icon="📤")
        st.rerun()

    st.markdown("---")
    st.markdown("<div class='sidebar-section'>💡 使用步骤</div>", unsafe_allow_html=True)
    st.markdown("<div class='step-item'><div class='step-num'>1</div><span>上传你的文档文件</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='step-item'><div class='step-num'>2</div><span>等待文档读取完成</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='step-item'><div class='step-num'>3</div><span>在右侧输入你的问题</span></div>", unsafe_allow_html=True)
    st.markdown("<div class='step-item'><div class='step-num'>4</div><span>AI基于文档内容回答</span></div>", unsafe_allow_html=True)

# ===== 主界面 =====
if not st.session_state.doc_text:
    st.markdown("<h1 class='main-title'>📄 智能文档问答系统</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color:#666;font-size:1.1em;margin-bottom:30px;'>基于大语言模型 · 让文档会说话</p>", unsafe_allow_html=True)
    st.markdown("""
    <div class='welcome-banner'>
        <h2>🎉 欢迎使用智能文档问答系统</h2>
        <p>上传你的文档，用自然语言提问，AI将为你精准解读文档内容</p>
        <br>
        <p style='font-size:1.3em;'>👈 请先在左侧上传文档</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class='feature-card card-blue'>
            <div class='card-icon'>📑</div>
            <div class='card-title'>支持多种格式</div>
            <div class='card-desc'>PDF、Word(.doc/.docx)、TXT 文档均可上传解析</div>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class='feature-card card-purple'>
            <div class='card-icon'>🤖</div>
            <div class='card-title'>大模型驱动</div>
            <div class='card-desc'>接入智谱GLM大语言模型，精准理解文档语义内容</div>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class='feature-card card-pink'>
            <div class='card-icon'>💬</div>
            <div class='card-title'>自然语言交互</div>
            <div class='card-desc'>用中文自然提问，像聊天一样快速获取文档信息</div>
        </div>""", unsafe_allow_html=True)

else:
    st.markdown("<h1 class='main-title'>📄 智能文档问答系统</h1>", unsafe_allow_html=True)
    st.markdown(f"""
    <div class='chat-header'>
        ✅ 文档已加载，共读取 <b>{len(st.session_state.doc_text)}</b> 个字符 &nbsp;|&nbsp; 🤖 AI已就绪，请开始提问
    </div>""", unsafe_allow_html=True)

    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.write(msg["content"])

    user_input = st.chat_input("💬 请输入你的问题，我将根据文档内容为你解答...")

    if user_input:
        with st.chat_message("user"):
            st.write(user_input)
        prompt = f"请根据以下文档内容回答问题。如果文档中没有相关信息，请如实告知。\n\n文档内容：\n{st.session_state.doc_text[:3000]}\n\n用户问题：{user_input}"
        with st.chat_message("assistant"):
            with st.spinner("🤔 思考中..."):
                response = client.chat.completions.create(
                    model="glm-4-flash",
                    messages=[{"role": "user", "content": prompt}]
                )
                answer = response.choices[0].message.content
                st.write(answer)
        st.session_state.messages.append({"role": "user", "content": user_input})
        st.session_state.messages.append({"role": "assistant", "content": answer})