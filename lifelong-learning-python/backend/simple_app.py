                self.save_documents()
                
                return {
                    "message": "文档删除成功",
                    "document_id": doc_id
                }
                
            except Exception as e:
                logger.error(f"删除失败: {e}")
                raise HTTPException(status_code=500, detail=f"删除失败: {str(e)}")
        
        @self.app.get("/api/documents/{doc_id}")
        async def get_document(doc_id: str):
            """获取文档详情"""
            if doc_id not in self.documents:
                raise HTTPException(status_code=404, detail="文档不存在")
            
            doc = self.documents[doc_id]
            return {
                "id": doc.id,
                "title": doc.title,
                "type": doc.doc_type,
                "status": doc.status,
                "content_preview": doc.content[:500] + "..." if doc.content else "",
                "chunks_count": len(doc.chunks),
                "created_at": doc.created_at
            }

# ==================== 启动应用 ====================

def main():
    """主函数"""
    app = LifelongLearningApp()
    
    print("=" * 60)
    print("个人终身学习数字读书系统 - Python简化版")
    print("=" * 60)
    print()
    print("📊 系统信息:")
    print(f"  • 文档数量: {len(app.documents)}")
    print(f"  • 上传目录: {app.upload_dir}")
    print(f"  • 数据目录: {app.data_dir}")
    print()
    print("🚀 启动服务...")
    print(f"  • API地址: http://localhost:8000")
    print(f"  • API文档: http://localhost:8000/docs")
    print()
    print("📝 使用说明:")
    print("  1. 上传文档: POST /api/upload")
    print("  2. 列出文档: GET /api/documents")
    print("  3. 搜索文档: POST /api/search")
    print("  4. AI对话: POST /api/chat")
    print("  5. 系统统计: GET /api/stats")
    print()
    print("=" * 60)
    
    # 启动服务器
    uvicorn.run(app.app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()