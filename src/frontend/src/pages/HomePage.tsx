// Home Page
//首页

import React, { useEffect } from 'react';
import { Row, Col, Card, Statistic, List, Tag, Spin } from 'antd';
import {
  FileTextOutlined,
  ClockCircleOutlined,
  TagOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { useDocumentStore } from '../stores/documentStore';
import { useNavigate } from 'react-router-dom';
import './pages.css';

export function HomePage() {
  const navigate = useNavigate();
  const {
    documents,
    statistics,
    loading,
    fetchDocuments,
    fetchStatistics,
  } = useDocumentStore();

  useEffect(() => {
    fetchStatistics();
    fetchDocuments({ limit: 5 });
  }, []);

  const recentDocuments = documents.slice(0, 5);

  return (
    <div className="home-page">
      <h1>📚 文档库</h1>
      
      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/documents')}>
            <Statistic
              title="文档总数"
              value={statistics.total}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1A73E8' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/documents?status=pending')}>
            <Statistic
              title="待分类"
              value={statistics.pending}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#FBBC05' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card hoverable onClick={() => navigate('/documents?status=classified')}>
            <Statistic
              title="已分类"
              value={statistics.classified}
              prefix={<TagOutlined />}
              valueStyle={{ color: '#34A853' }}
            />
          </Card>
        </Col>
      </Row>
      
      {/* 快速操作 */}
      <Row gutter={[16, 16]} style={{ marginBottom: 24 }}>
        <Col>
          <Card
            hoverable
            style={{ textAlign: 'center', minWidth: 150 }}
            onClick={() => navigate('/documents')}
          >
            <PlusOutlined style={{ fontSize: 24, marginBottom: 8 }} />
            <div>扫描文档</div>
          </Card>
        </Col>
      </Row>
      
      {/* 最近添加 */}
      <Card title="最近添加" extra={<a onClick={() => navigate('/documents')}>查看全部</a>}>
        {loading ? (
          <Spin />
        ) : (
          <List
            itemLayout="horizontal"
            dataSource={recentDocuments}
            renderItem={(doc) => (
              <List.Item
                actions={[
                  <a key="view" onClick={() => navigate(`/documents/${doc.id}`)}>
                    查看
                  </a>
                ]}
              >
                <List.Item.Meta
                  avatar={<FileTextOutlined style={{ fontSize: 24, color: '#1A73E8' }} />}
                  title={doc.title || doc.file_name}
                  description={
                    <>
                      <Tag>{doc.status}</Tag>
                      {doc.category_path && (
                        <Tag color="blue">{doc.category_path}</Tag>
                      )}
                      <span style={{ color: '#999' }}>
                        {new Date(doc.updated_at).toLocaleDateString()}
                      </span>
                    </>
                  }
                />
              </List.Item>
            )}
          />
        )}
      </Card>
    </div>
  );
}
