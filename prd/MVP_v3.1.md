# SkyOne Shuge v3.1 - 生态扩展

**版本**: v3.1
**日期**: 2026-02-03

## 新增功能

### 1. API 市场

```python
# services/marketplace.py

class Marketplace:
    async def browse_apis(self, category: str = None):
        """浏览 API"""
        pass
    
    async def install_integration(self, integration_id: str):
        """安装集成"""
        pass
```

### 2. 插件市场

```python
# services/plugin_market.py

class PluginMarket:
    async def browse_plugins(self, category: str = None):
        """浏览插件"""
        pass
    
    async def install_plugin(self, plugin_id: str):
        """安装插件"""
        pass
```

### 3. 第三方集成

```python
# integrations/notion.py
# integrations/obsidian.py
# integrations/zotero.py
# integrations/dropbox.py
# integrations/google_drive.py
```

---

**版本**: v3.1
