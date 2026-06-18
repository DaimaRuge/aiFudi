import streamlit as st
import requests
import pandas as pd
import json
from datetime import datetime
import time
import os

# 配置页面
st.set_page_config(
    page_title="个人终身学习数字读书系统",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 配置后端URL
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 2rem;
    }
    .sub-header {
        font-size: 1.5rem;
        color: #3B82F6;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }
    .success-box {
        background-color: #D1FAE5;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #10B981;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #DBEAFE;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 5px solid #3B82F6;
        margin: 1rem 0;
    }
    .chat-message-user {
        background-color: #E0F2FE;
        padding: 1rem;
        border-radius: 1rem 1rem 0 1rem;
        margin: 0.5rem 0;
        margin-left: 20%;
    }
    .chat-message-assistant {
        background-color: #F3F4F6;
        padding: 1rem;
        border-radius: 1rem 1rem 1rem 0;
        margin: 0.5rem 0;
        margin-right: 20%;
    }
</style>
""", unsafe_allow_html=True)

# 初始化session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "documents" not in st.session_state:
    st.session_state.documents = []
if "session_id" not in st.session_state:
    st.session_state.session_id = None

# 标题
st.markdown('<h1 class="main-header">📚 个人终身学习数字读书系统</h1>', unsafe_allow_html=True)
st.markdown("基于大模型Agent的个人知识操作系统 - MVP演示版")

# 侧边栏
with st.sidebar:
    st.image("https://img.icons8.com/color/96/000000/book-stack.png", width=80)
    st.markdown("### 🚀 系统状态")
    
    # 健康检查
    try:
        response = requests.get(f"{BACKEND_URL}/health")
        if response.status_code == 200:
            st.success("✅ 后端服务正常")
        else:
            st.error("❌ 后端服务异常")
    except:
        st.error("❌ 无法连接到后端服务")
    
    st.markdown("---")
    
    # 系统统计
    st.markdown("### 📊 系统统计")
    try:
        stats_response = requests.get(f"{BACKEND_URL}/api/v1/system/stats")
        if stats_response.status_code == 200:
            stats = stats_response.json()
            st.metric("文档数量", stats.get("documents_total", 0))
            st.metric("用户数量", stats.get("users_total", 0))
            st.metric("向量分块", stats.get("vector_store", {}).get("total_chunks", 0))
    except:
        st.write("无法获取统计信息")
    
    st.markdown("---")
    
    # 快速操作
    st.markdown("### ⚡ 快速操作")
    if st.button("🔄 刷新数据"):
        st.rerun()
    
    if st.button("🗑️ 清空聊天记录"):
        st.session_state.chat_history = []
        st.success("聊天记录已清空")
        st.rerun()

# 主界面 - 标签页
tab1, tab2, tab3, tab4 = st.tabs(["📁 文档管理", "🔍 知识检索", "💬 AI对话", "⚙️ 系统设置"])

# 标签页1: 文档管理
with tab1:
    st.markdown('<h2 class="sub-header">📁 文档管理</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 上传文档")
        
        # 文件上传
        uploaded_file = st.file_uploader(
            "选择文档文件",
            type=['pdf', 'docx', 'txt', 'md'],
            help="支持PDF、DOCX、TXT、MD格式"
        )
        
        if uploaded_file is not None:
            # 显示文件信息
            st.info(f"**文件**: {uploaded_file.name}")
            st.info(f"**大小**: {uploaded_file.size / 1024:.1f} KB")
            
            # 标题输入
            title = st.text_input("文档标题", value=uploaded_file.name)
            
            # 标签输入
            tags = st.text_input("标签（用逗号分隔）", value="")
            
            if st.button("📤 上传文档", type="primary"):
                with st.spinner("正在上传文档..."):
                    try:
                        # 准备上传数据
                        files = {"file": (uploaded_file.name, uploaded_file.getvalue())}
                        data = {"title": title, "tags": tags.split(",") if tags else []}
                        
                        # 发送请求
                        response = requests.post(
                            f"{BACKEND_URL}/api/v1/documents/upload",
                            files=files,
                            data=data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            st.success(f"✅ 文档上传成功！ID: {result['document_id']}")
                            st.markdown(f'<div class="success-box">{result["message"]}</div>', unsafe_allow_html=True)
                        else:
                            st.error(f"上传失败: {response.text}")
                    except Exception as e:
                        st.error(f"上传失败: {str(e)}")
    
    with col2:
        st.markdown("### 我的文档")
        
        # 刷新文档列表
        if st.button("🔄 刷新文档列表"):
            try:
                response = requests.get(f"{BACKEND_URL}/api/v1/documents")
                if response.status_code == 200:
                    st.session_state.documents = response.json().get("documents", [])
            except:
                st.error("无法获取文档列表")
        
        # 显示文档列表
        if st.session_state.documents:
            df = pd.DataFrame(st.session_state.documents)
            
            # 格式化显示
            df_display = df[['title', 'document_type', 'status', 'created_at', 'file_size']].copy()
            df_display['created_at'] = pd.to_datetime(df_display['created_at']).dt.strftime('%Y-%m-%d %H:%M')
            df_display['file_size'] = df_display['file_size'].apply(lambda x: f"{x/1024:.1f} KB")
            
            st.dataframe(
                df_display,
                column_config={
                    "title": "标题",
                    "document_type": "类型",
                    "status": "状态",
                    "created_at": "上传时间",
                    "file_size": "文件大小"
                },
                use_container_width=True
            )
            
            # 文档操作
            selected_doc = st.selectbox(
                "选择文档进行操作",
                options=df['title'].tolist(),
                index=0
            )
            
            col_btn1, col_btn2 = st.columns(2)
            with col_btn1:
                if st.button("📄 查看详情"):
                    doc_id = df[df['title'] == selected_doc]['id'].iloc[0]
                    try:
                        response = requests.get(f"{BACKEND_URL}/api/v1/documents/{doc_id}")
                        if response.status_code == 200:
                            doc_detail = response.json()
                            st.markdown(f'<div class="info-box">'
                                      f'<strong>文档详情</strong><br>'
                                      f'ID: {doc_detail["id"]}<br>'
                                      f'类型: {doc_detail["document_type"]}<br>'
                                      f'状态: {doc_detail["status"]}<br>'
                                      f'内容预览: {doc_detail.get("parsed_content", "无")[:200]}...'
                                      f'</div>', unsafe_allow_html=True)
                    except:
                        st.error("无法获取文档详情")
            
            with col_btn2:
                if st.button("🗑️ 删除文档", type="secondary"):
                    doc_id = df[df['title'] == selected_doc]['id'].iloc[0]
                    try:
                        response = requests.delete(f"{BACKEND_URL}/api/v1/documents/{doc_id}")
                        if response.status_code == 200:
                            st.success("文档删除成功")
                            st.rerun()
                        else:
                            st.error("删除失败")
                    except:
                        st.error("删除失败")
        else:
            st.info("暂无文档，请先上传文档")

# 标签页2: 知识检索
with tab2:
    st.markdown('<h2 class="sub-header">🔍 知识检索</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        search_query = st.text_input(
            "搜索关键词",
            placeholder="输入您想搜索的内容...",
            help="基于文档内容的语义搜索"
        )
    
    with col2:
        search_limit = st.number_input("返回结果数", min_value=1, max_value=50, value=10)
    
    if st.button("🔍 开始搜索", type="primary"):
        if search_query:
            with st.spinner("正在搜索..."):
                try:
                    # 构建搜索请求
                    search_data = {
                        "query": search_query,
                        "limit": int(search_limit)
                    }
                    
                    response = requests.post(
                        f"{BACKEND_URL}/api/v1/search",
                        json=search_data
                    )
                    
                    if response.status_code == 200:
                        results = response.json()
                        
                        if results["total"] > 0:
                            st.success(f"找到 {results['total']} 个相关结果")
                            
                            # 显示结果
                            for i, result in enumerate(results["results"], 1):
                                with st.expander(f"结果 {i}: 相似度 {result['score']:.2%}"):
                                    st.write(f"**内容**: {result['text'][:500]}...")
                                    st.write(f"**来源**: 文档 {result['metadata'].get('document_id', '未知')}")
                                    st.write(f"**分块索引**: {result['metadata'].get('chunk_index', '未知')}")
                        else:
                            st.info("未找到相关结果")
                    else:
                        st.error(f"搜索失败: {response.text}")
                except Exception as e:
                    st.error(f"搜索失败: {str(e)}")
        else:
            st.warning("请输入搜索关键词")

# 标签页3: AI对话
with tab3:
    st.markdown('<h2 class="sub-header">💬 AI对话助手</h2>', unsafe_allow_html=True)
    
    # 聊天历史
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_history:
            if message["role"] == "user":
                st.markdown(f'<div class="chat-message-user">'
                          f'<strong>👤 您:</strong><br>{message["content"]}'
                          f'</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="chat-message-assistant">'
                          f'<strong>🤖 AI助手:</strong><br>{message["content"]}'
                          f'</div>', unsafe_allow_html=True)
    
    # 输入区域
    st.markdown("---")
    user_input = st.text_area(
        "输入您的问题",
        placeholder="基于您的文档内容提问...",
        height=100,
        key="user_input"
    )
    
    col_btn1, col_btn2 = st.columns([1, 1])
    
    with col_btn1:
        if st.button("📤 发送", type="primary", use_container_width=True):
            if user_input.strip():
                # 添加用户消息到历史
                st.session_state.chat_history.append({
                    "role": "user",
                    "content": user_input.strip()
                })
                
                with st.spinner("AI正在思考..."):
                    try:
                        # 发送聊天请求
                        chat_data = {
                            "message": user_input.strip(),
                            "session_id": str(st.session_state.session_id) if st.session_state.session_id else None
                        }
                        
                        response = requests.post(
                            f"{BACKEND_URL}/api/v1/chat",
                            json=chat_data
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            
                            # 更新session_id
                            if not st.session_state.session_id:
                                st.session_state.session_id = result["session_id"]
                            
                            # 添加AI回复到历史
                            st.session_state.chat_history.append({
                                "role": "assistant",
                                "content": result["response"]
                            })
                            
                            # 显示来源
                            if result.get("sources"):
                                with st.expander("📚 回答来源"):
                                    for i, source in enumerate(result["sources"][:3], 1):
                                        st.write(f"**来源 {i}** (相似度: {source.get('score', 0):.2%})")
                                        st.write(f"{source.get('text', '')[:300]}...")
                            
                            st.rerun()
                        else:
                            st.error(f"聊天失败: {response.text}")
                    except Exception as e:
                        st.error(f"聊天失败: {str(e)}")
            else:
                st.warning("请输入问题内容")
    
    with col_btn2:
        if st.button("🗑️ 清空对话", type="secondary", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.session_id = None
            st.rerun()

# 标签页4: 系统设置
with tab4:
    st.markdown('<h2 class="sub-header">⚙️ 系统设置</h2>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 后端配置")
        
        backend_url = st.text_input(
            "后端API地址",
            value=BACKEND_URL,
            help="后端服务的URL地址"
        )
        
        if backend_url != BACKEND_URL:
            st.info(f"新地址: {backend_url}")
            if st.button("应用配置"):
                os.environ["BACKEND_URL"] = backend_url
                st.success("配置已更新，请刷新页面")
        
        st.markdown("### AI配置")
        
        api_key = st.text_input(
            "DeepSeek API密钥",
            type="password",
            help="用于AI对话的API密钥"
        )
        
        if api_key:
            st.success("API密钥已设置")
    
    with col2:
        st.markdown("### 系统信息")
        
        try:
            response = requests.get(f"{BACKEND_URL}/api/v1/system/stats")
            if response.status_code == 200:
                stats = response.json()
                
                st.json(stats, expanded=False)
                
                # 系统状态
                st.markdown("#### 系统状态")
                status_items = [
                    ("后端服务", "✅ 正常" if stats.get("documents_total") is not None else "❌ 异常"),
                    ("向量存储", "✅ 正常" if stats.get("vector_store") else "❌ 异常"),
                    ("上传目录", "✅ 正常" if os.path.exists(stats.get("upload_dir", "")) else "❌ 异常")
                ]
                
                for item, status in status_items:
                    st.write(f"{item}: {status}")
            else:
                st.error("无法获取系统信息")
        except:
            st.error("无法连接到后端服务")
    
    st.markdown("---")
    st.markdown("### 系统操作")
    
    col_op1, col_op2 = st.columns(2)
    
    with col_op1:
        if st.button("🔄 重启后端服务", type="secondary"):
            st.info("重启功能需要Docker Compose支持")
    
    with col_op2:
        if st.button("🧹 清理临时文件", type="secondary"):
            st.info("清理功能待实现")

# 页脚
st.markdown("---")
st.markdown(
    """
    <div style="text-align: center; color: #6B7280; font-size: 0.9rem;">
        <p>个人终身学习数字读书系统 - MVP演示版 v0.1.0</p>
        <p>基于大模型Agent的个人知识操作系统</p>
    </div>
    """,
    unsafe_allow_html=True
)