import React, { useEffect, useState } from 'react';
import { Card, Row, Col, Statistic, Typography, List, Button, Space, Spin } from 'antd';
import {
  FileTextOutlined,
  ApiOutlined,
  MessageOutlined,
  BookOutlined,
  ArrowRightOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { documentApi, knowledgeApi, chatApi, learningApi } from '../services/api';
import { Document, ChatSession, LearningPath } from '../types';

const { Title, Text } = Typography;

const Dashboard: React.FC = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    documents: 0,
    knowledgeNodes: 0,
    knowledgeRelations: 0,
    chatSessions: 0,
    learningPaths: 0,
  });
  const [recentDocuments, setRecentDocuments] = useState<Document[]>([]);
  const [recentSessions, setRecentSessions] = useState<ChatSession[]>([]);
  const [recentPaths, setRecentPaths] = useState<LearningPath[]>([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);

      // 并行获取所有数据
      const [documents, knowledgeStats, sessions, paths] = await Promise.all([
        documentApi.list(0, 5),
        knowledgeApi.getStats(),
        chatApi.listSessions(),
        learningApi.listPaths(),
      ]);

      setRecentDocuments(documents);
      setStats((prev) => ({
        ...prev,
        documents: documents.length,
        knowledgeNodes: knowledgeStats.total_nodes,
        knowledgeRelations: knowledgeStats.total_relations,
        chatSessions: sessions.length,
        learningPaths: paths.length,
      }));
      setRecentSessions(sessions.slice(0, 5));
      setRecentPaths(paths.slice(0, 5));
    } catch (error) {
      console.error('获取仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        仪表盘
      </Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="文档数量"
              value={stats.documents}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="知识节点"
              value={stats.knowledgeNodes}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="对话会话"
              value={stats.chatSessions}
              prefix={<MessageOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="学习路径"
              value={stats.learningPaths}
              prefix={<BookOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Col>
        </Col>
      </Row>

      {/* 快捷操作 */}
      <Card style={{ marginTop: '24px' }}>
        <Title level={4} style={{ marginBottom: '16px' }}>
          快捷操作
        </Title>
        <Space wrap>
          <Button type="primary" icon={<FileTextOutlined />} onClick={() => navigate('/documents')}>
            上传文档
          </Button>
          <Button icon={<MessageOutlined />} onClick={() => navigate('/chat')}>
            开始对话
          </Button>
          <Button icon={<BookOutlined />} onClick={() => navigate('/learning')}>
            创建学习路径
          </Button>
          <Button icon={<ApiOutlined />} onClick={() => navigate('/knowledge')}>
            查看知识图谱
          </Button>
        </Space>
      </Card>

      {/* 最近内容 */}
      <Row gutter={[16, 16]} style={{ marginTop: '24px' }}>
        <Col xs={24} lg={12}>
          <Card
            title="最近文档"
            extra={
              <Button type="link" onClick={() => navigate('/documents')}>
                查看全部 <ArrowRightOutlined />
              </Button>
            }
          >
            <List
              dataSource={recentDocuments}
              renderItem={(doc) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<FileTextOutlined style={{ fontSize: '24px', color: '#1890ff' }} />}
                    title={doc.title}
                    description={`${doc.word_count} 字 · ${new Date(doc.created_at).toLocaleDateString()}`}
                  />
                </List.Item>
              )}
              locale={{ emptyText: '暂无文档' }}
            />
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card
            title="学习进度"
            extra={
              <Button type="link" onClick={() => navigate('/learning')}>
                查看全部 <ArrowRightOutlined />
              </Button>
            }
          >
            <List
              dataSource={recentPaths}
              renderItem={(path) => (
                <List.Item>
                  <List.Item.Meta
                    avatar={<BookOutlined style={{ fontSize: '24px', color: '#fa8c16' }} />}
                    title={path.title}
                    description={`进度: ${Math.round(path.progress * 100)}%`}
                  />
                </List.Item>
              )}
              locale={{ emptyText: '暂无学习路径' }}
            />
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Dashboard;
