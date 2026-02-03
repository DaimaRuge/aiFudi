// Search Page
//搜索页面

import React, { useEffect } from 'react';
import { Input, Card, List, Tag, Empty, Spin } from 'antd';
import { useDocumentStore } from '../stores/documentStore';
import { useNavigate } from 'react-router-dom';
import './pages.css';

const { Search } = Input;

export function SearchPage() {
  const navigate = useNavigate();
  const {
    searchQuery,
    searchResults,
    loading,
    searchDocuments,
  } = useDocumentStore();

  useEffect(() => {
    if (searchQuery) {
      searchDocuments(searchQuery);
    }
  }, []);

  const handleSearch = (value: string) => {
    searchDocuments(value);
  };

  return (
    <div className="search-page">
      <h1>🔍 文档搜索</h1>
      
      <Search
        placeholder="输入关键词搜索..."
        defaultValue={searchQuery}
        onSearch={handleSearch}
        size="large"
        enterButton="搜索"
        style={{ maxWidth: 600, marginBottom: 24 }}
      />
      
      {loading ? (
        <div style={{ textAlign: 'center', padding: 48 }}>
          <Spin size="large" />
        </div>
      ) : searchResults.length > 0 ? (
        <List
          itemLayout="horizontal"
          dataSource={searchResults}
          renderItem={(item: any) => (
            <Card
              hoverable
              className="search-result-card"
              onClick={() => navigate(`/documents/${item.id}`)}
            >
              <List.Item.Meta
                title={
                  <span>
                    {item.title || item.file_name}
                    <Tag style={{ marginLeft: 8 }}>{item.category_path || '未分类'}</Tag>
                  </span>
                }
                description={
                  <>
                    <div style={{ marginBottom: 8 }}>
                      {item.abstract || '暂无摘要'}
                    </div>
                    <div style={{ color: '#999', fontSize: 12 }}>
                      {item.keywords?.map((k: string) => (
                        <Tag key={k} style={{ marginRight: 4 }}>
                          {k}
                        </Tag>
                      ))}
                    </div>
                  </>
                }
              />
            </Card>
          )}
        />
      ) : searchQuery ? (
        <Empty description="未找到相关文档" />
      ) : (
        <Empty description="输入关键词开始搜索" />
      )}
    </div>
  );
}
