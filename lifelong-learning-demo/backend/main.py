from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import shutil
import os
import uuid
from typing import List, Optional
import logging
from datetime import datetime

from models import (
    User, Document, DocumentChunk, KnowledgeQuery, KnowledgeResponse,
    UploadDocumentRequest, UploadDocumentResponse, SearchRequest, SearchResponse,
    ChatRequest, ChatResponse
)
from document_parser import document_parser, document_chunker
from vector_store import vector_store, knowledge_retriever
from ai_service import ai_service

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 创建FastAPI应用
app = FastAPI(
    title="个人终身学习数字读书系统 - API",
    description="基于大模型Agent的个人知识操作系统",
    version="0.1.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境应该限制
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 存储目录
UPLOAD_DIR = "./uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 内存中的文档存储（生产环境应该用数据库）
documents_db = {}
users_db = {}
chat_sessions_db = {}


# 依赖项
def get_current_user() -> User:
    """获取当前用户（简化版）"""
    # 这里应该从token验证用户
    user_id = uuid.uuid4()
    if user_id not in users_db:
        users_db[user_id] = User(
            id=user_id,
            email="demo@example.com",
            username="demo_user"
        )
    return users_db[user_id]


# API端点
@app.get("/")
async def root():
    """根端点"""
    return {
        "message": "个人终身学习数字读书系统 API",
        "version": "0.1.0",
        "status": "运行中"
    }


@app.get("/health")
async def health_check():
    """健康检查"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/api/v1/documents/upload", response_model=UploadDocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    request: UploadDocumentRequest = Depends(),
    current_user: User = Depends(get_current_user),
    background_tasks: BackgroundTasks = None
):
    """上传文档"""
    try:
        # 生成唯一文件名
        file_ext = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = os.path.join(UPLOAD_DIR, unique_filename)
        
        # 保存文件
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        # 检测文档类型
        doc_type = document_parser.detect_type(file.filename)
        
        # 创建文档记录
        document = Document(
            user_id=current_user.id,
            title=request.title or file.filename,
            original_filename=file.filename,
            file_size=os.path.getsize(file_path),
            mime_type=file.content_type,
            document_type=doc_type,
            storage_path=file_path,
            status="uploaded"
        )
        
        # 保存到内存数据库
        documents_db[document.id] = document
        
        # 如果是后台任务，异步处理
        if background_tasks:
            background_tasks.add_task(process_document_async, document.id)
            message = "文档已上传，正在后台处理"
        else:
            # 同步处理
            process_document_async(document.id)
            message = "文档已上传并处理完成"
        
        return UploadDocumentResponse(
            document_id=document.id,
            status="success",
            message=message
        )
        
    except Exception as e:
        logger.error(f"文档上传失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档上传失败: {str(e)}")


def process_document_async(document_id: uuid.UUID):
    """异步处理文档"""
    try:
        document = documents_db.get(document_id)
        if not document:
            logger.error(f"文档不存在: {document_id}")
            return
        
        # 更新状态
        document.status = "parsing"
        documents_db[document_id] = document
        
        # 解析文档
        parsed_content = document_parser.parse(
            document.storage_path,
            document.document_type
        )
        
        # 提取元数据
        metadata = document_parser.extract_metadata(
            document.storage_path,
            document.document_type
        )
        
        # 更新文档
        document.parsed_content = parsed_content
        document.metadata = metadata
        document.status = "parsed"
        document.updated_at = datetime.now()
        documents_db[document_id] = document
        
        # 分块
        chunks_text = document_chunker.chunk_text(parsed_content)
        
        # 创建分块对象
        chunks = []
        for i, chunk_text in enumerate(chunks_text):
            chunk = DocumentChunk(
                document_id=document_id,
                chunk_index=i,
                chunk_text=chunk_text
            )
            chunks.append(chunk)
        
        # 添加到向量数据库
        if chunks:
            vector_store.add_document_chunks(str(document_id), chunks)
            logger.info(f"文档 {document_id} 处理完成，生成 {len(chunks)} 个分块")
        else:
            logger.warning(f"文档 {document_id} 没有生成分块")
        
    except Exception as e:
        logger.error(f"文档处理失败: {e}")
        if document_id in documents_db:
            documents_db[document_id].status = "error"


@app.get("/api/v1/documents")
async def list_documents(
    current_user: User = Depends(get_current_user)
):
    """列出用户的所有文档"""
    user_documents = []
    for doc_id, doc in documents_db.items():
        if doc.user_id == current_user.id:
            user_documents.append({
                "id": doc.id,
                "title": doc.title,
                "document_type": doc.document_type,
                "status": doc.status,
                "created_at": doc.created_at,
                "file_size": doc.file_size
            })
    
    return {
        "documents": user_documents,
        "total": len(user_documents)
    }


@app.get("/api/v1/documents/{document_id}")
async def get_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    """获取文档详情"""
    document = documents_db.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权访问此文档")
    
    return {
        "id": document.id,
        "title": document.title,
        "document_type": document.document_type,
        "status": document.status,
        "parsed_content": document.parsed_content[:1000] if document.parsed_content else None,  # 只返回部分内容
        "metadata": document.metadata,
        "created_at": document.created_at,
        "updated_at": document.updated_at
    }


@app.post("/api/v1/search", response_model=SearchResponse)
async def search_documents(
    request: SearchRequest,
    current_user: User = Depends(get_current_user)
):
    """搜索文档"""
    try:
        # 获取用户的所有文档ID
        user_document_ids = []
        for doc_id, doc in documents_db.items():
            if doc.user_id == current_user.id:
                user_document_ids.append(str(doc_id))
        
        # 搜索向量数据库
        results = vector_store.search_similar(
            query=request.query,
            limit=request.limit,
            document_ids=user_document_ids
        )
        
        return SearchResponse(
            results=results,
            total=len(results)
        )
        
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        raise HTTPException(status_code=500, detail=f"搜索失败: {str(e)}")


@app.post("/api/v1/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: User = Depends(get_current_user)
):
    """聊天对话"""
    try:
        start_time = datetime.now()
        
        # 使用RAG生成回答
        rag_result = ai_service.rag_answer(
            question=request.message,
            max_context_chunks=3
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        # 生成session_id（如果未提供）
        session_id = request.session_id or uuid.uuid4()
        
        return ChatResponse(
            response=rag_result["answer"],
            session_id=session_id,
            sources=rag_result["sources"],
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"聊天失败: {e}")
        raise HTTPException(status_code=500, detail=f"聊天失败: {str(e)}")


@app.post("/api/v1/knowledge/query", response_model=KnowledgeResponse)
async def query_knowledge(
    query: KnowledgeQuery,
    current_user: User = Depends(get_current_user)
):
    """知识查询"""
    try:
        start_time = datetime.now()
        
        # 验证文档权限
        valid_document_ids = []
        if query.document_ids:
            for doc_id in query.document_ids:
                doc = documents_db.get(doc_id)
                if doc and doc.user_id == current_user.id:
                    valid_document_ids.append(str(doc_id))
        
        # 搜索
        results = vector_store.search_similar(
            query=query.query,
            limit=query.limit,
            document_ids=valid_document_ids if valid_document_ids else None
        )
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return KnowledgeResponse(
            query=query.query,
            results=results,
            total=len(results),
            processing_time=processing_time
        )
        
    except Exception as e:
        logger.error(f"知识查询失败: {e}")
        raise HTTPException(status_code=500, detail=f"知识查询失败: {str(e)}")


@app.get("/api/v1/system/stats")
async def get_system_stats():
    """获取系统统计信息"""
    vector_stats = vector_store.get_collection_stats()
    
    return {
        "documents_total": len(documents_db),
        "users_total": len(users_db),
        "vector_store": vector_stats,
        "upload_dir": UPLOAD_DIR,
        "timestamp": datetime.now().isoformat()
    }


@app.delete("/api/v1/documents/{document_id}")
async def delete_document(
    document_id: uuid.UUID,
    current_user: User = Depends(get_current_user)
):
    """删除文档"""
    document = documents_db.get(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")
    
    if document.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="无权删除此文档")
    
    try:
        # 从向量数据库删除分块
        deleted_count = vector_store.delete_document_chunks(str(document_id))
        
        # 删除文件
        if os.path.exists(document.storage_path):
            os.remove(document.storage_path)
        
        # 从内存数据库删除
        del documents_db[document_id]
        
        return {
            "message": "文档删除成功",
            "deleted_chunks": deleted_count,
            "document_id": document_id
        }
        
    except Exception as e:
        logger.error(f"文档删除失败: {e}")
        raise HTTPException(status_code=500, detail=f"文档删除失败: {str(e)}")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)