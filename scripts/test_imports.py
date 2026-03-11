
import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
sys.path.append(os.path.abspath("/root/.openclaw/workspace/skyone-shuge/src"))

async def test_imports():
    print("Testing imports...")
    try:
        from skyone_shuge.core.config import settings
        print(f"✅ Config loaded: {settings.APP_NAME} v{settings.APP_VERSION}")
        
        from skyone_shuge.core.database import Base, engine
        print("✅ Database module loaded")
        
        from skyone_shuge.models import Document, Folder, Tag, User
        print("✅ Models loaded")
        
        from skyone_shuge.schemas import Document as DocumentSchema
        print("✅ Schemas loaded")
        
        from skyone_shuge.agents import AgentRegistry, BaseAgent
        print("✅ Agents module loaded")
        
        from skyone_shuge.agents.document_processor import DocumentProcessorAgent
        print("✅ DocumentProcessorAgent loaded")
        
        # Test Agent Registry
        agent = AgentRegistry.get_agent("document_processor")
        if agent:
            print(f"✅ Agent registry working: Found {agent.name}")
        else:
            print("❌ Agent registry failed")
            
        print("\nAll imports successful!")
        return True
    except Exception as e:
        print(f"\n❌ Import failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    asyncio.run(test_imports())
