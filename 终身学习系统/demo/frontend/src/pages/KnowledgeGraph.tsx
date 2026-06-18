import React, { useEffect, useState, useRef, useCallback } from 'react';
import {
  Card,
  Select,
  Spin,
  Empty,
  Typography,
  message,
  Input,
  List,
  Tag,
  Row,
  Col,
  Statistic,
} from 'antd';
import {
  SearchOutlined,
  ApiOutlined,
} from '@ant-design/icons';
import ForceGraph2D from 'react-force-graph-2d';
import { knowledgeApi, documentApi } from '../services/api';
import { VisualizationGraph, GraphNode, Document } from '../types';

const { Title, Text } = Typography;
const { Search } = Input;

const KnowledgeGraph: React.FC = () => {
  const graphRef = useRef<any>(null);
  const [loading, setLoading] = useState(false);
  const [graphData, setGraphData] = useState<VisualizationGraph>({ nodes: [], edges: [] });
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | undefined>();
  const [stats, setStats] = useState({ total_nodes: 0, total_relations: 0, nodes_by_type: {} });
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [hoverNode, setHoverNode] = useState<GraphNode | null>(null);

  useEffect(() => {
    fetchDocuments();
    fetchStats();
    fetchGraph();
  }, []);

  useEffect(() => {
    fetchGraph(selectedDocumentId);
  }, [selectedDocumentId]);

  const fetchDocuments = async () => {
    try {
      const data = await documentApi.list();
      setDocuments(data);
    } catch (error) {
      console.error('获取文档列表失败:', error);
    }
  };

  const fetchStats = async () => {
    try {
      const data = await knowledgeApi.getStats();
      setStats(data);
    } catch (error) {
      console.error('获取统计信息失败:', error);
    }
  };

  const fetchGraph = async (documentId?: string) => {
    try {
      setLoading(true);
      const data = await knowledgeApi.getVisualization(documentId);
      setGraphData(data);
    } catch (error) {
      message.error('获取知识图谱失败');
    } finally {
      setLoading(false);
    }
  };

  const handleSearch = async (query: string) => {
    if (!query.trim()) {
      setSearchResults([]);
      return;
    }
    try {
      const data = await knowledgeApi.search(query);
      setSearchResults(data.results);
    } catch (error) {
      message.error('搜索失败');
    }
  };

  // 节点颜色映射
  const getNodeColor = (type: string) => {
    const colors: Record<string, string> = {
      concept: '#1890ff',
      entity: '#52c41a',
      topic: '#fa8c16',
      method: '#722ed1',
      tool: '#eb2f96',
    };
    return colors[type] || '#666';
  };

  // 绘制节点
  const paintNode = useCallback(
    (node: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const size = 8 + (node.importance || 0.5) * 8;
      const fontSize = 12 / globalScale;
      const color = getNodeColor(node.type);

      // 绘制节点
      ctx.beginPath();
      ctx.arc(node.x, node.y, size, 0, 2 * Math.PI);
      ctx.fillStyle = color;
      ctx.fill();
      ctx.strokeStyle = hoverNode?.id === node.id ? '#000' : '#fff';
      ctx.lineWidth = 2;
      ctx.stroke();

      // 绘制标签
      if (globalScale >= 0.5) {
        ctx.font = `${fontSize}px Sans-Serif`;
        ctx.textAlign = 'center';
        ctx.textBaseline = 'top';
        ctx.fillStyle = '#333';
        ctx.fillText(node.label, node.x, node.y + size + 4);
      }
    },
    [hoverNode]
  );

  // 绘制边
  const paintLink = useCallback(
    (link: any, ctx: CanvasRenderingContext2D, globalScale: number) => {
      const source = link.source as { x: number; y: number };
      const target = link.target as { x: number; y: number };

      ctx.beginPath();
      ctx.moveTo(source.x, source.y);
      ctx.lineTo(target.x, target.y);
      ctx.strokeStyle = `rgba(0, 0, 0, ${0.2 + (link.weight || 0.5) * 0.3})`;
      ctx.lineWidth = 1 + (link.weight || 0.5);
      ctx.stroke();
    },
    []
  );

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        知识图谱
      </Title>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginBottom: '24px' }}>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="知识节点"
              value={stats.total_nodes}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="知识关系"
              value={stats.total_relations}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col xs={24} sm={8}>
          <Card>
            <Statistic
              title="文档来源"
              value={documents.length}
              prefix={<ApiOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 筛选和搜索 */}
      <Card style={{ marginBottom: '24px' }}>
        <Row gutter={[16, 16]} align="middle">
          <Col xs={24} sm={8}>
            <Select
              style={{ width: '100%' }}
              placeholder="选择文档筛选"
              allowClear
              onChange={(value) => setSelectedDocumentId(value)}
            >
              {documents.map((doc) => (
                <Select.Option key={doc.id} value={doc.id}>
                  {doc.title}
                </Select.Option>
              ))}
            </Select>
          </Col>
          <Col xs={24} sm={8}>
            <Search
              placeholder="搜索知识概念"
              onSearch={handleSearch}
              enterButton={<SearchOutlined />}
            />
          </Col>
        </Row>

        {/* 搜索结果 */}
        {searchResults.length > 0 && (
          <div style={{ marginTop: '16px' }}>
            <Text strong>搜索结果:</Text>
            <List
              size="small"
              dataSource={searchResults}
              renderItem={(item) => (
                <List.Item>
                  <Tag color={getNodeColor(item.type)}>{item.type}</Tag>
                  <Text>{item.name}</Text>
                  {item.description && (
                    <Text type="secondary" style={{ marginLeft: '8px' }}>
                      - {item.description}
                    </Text>
                  )}
                </List.Item>
              )}
            />
          </div>
        )}
      </Card>

      {/* 知识图谱可视化 */}
      <Card>
        {loading ? (
          <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '500px' }}>
            <Spin size="large" />
          </div>
        ) : graphData.nodes.length === 0 ? (
          <Empty description="暂无知识图谱数据，请先上传文档" style={{ padding: '100px 0' }} />
        ) : (
          <div className="graph-container">
            <ForceGraph2D
              ref={graphRef}
              graphData={{
                nodes: graphData.nodes.map((n) => ({ ...n })),
                links: graphData.edges.map((e) => ({ ...e, source: e.source, target: e.target })),
              }}
              nodeCanvasObject={paintNode}
              linkCanvasObject={paintLink}
              nodeRelSize={8}
              linkDirectionalParticles={2}
              linkDirectionalParticleWidth={2}
              d3AlphaDecay={0.02}
              d3VelocityDecay={0.3}
              onNodeHover={(node: any) => setHoverNode(node)}
              onNodeClick={(node: any) => {
                if (node) {
                  message.info(`节点: ${node.label} (${node.type})`);
                }
              }}
              cooldownTicks={100}
              onEngineStop={() => graphRef.current?.zoomToFit(400)}
            />
          </div>
        )}

        {/* 图例 */}
        {graphData.nodes.length > 0 && (
          <div style={{ marginTop: '16px', display: 'flex', gap: '16px', flexWrap: 'wrap' }}>
            <Text>图例:</Text>
            {['concept', 'entity', 'topic', 'method', 'tool'].map((type) => (
              <Tag key={type} color={getNodeColor(type)}>
                {type === 'concept' && '概念'}
                {type === 'entity' && '实体'}
                {type === 'topic' && '主题'}
                {type === 'method' && '方法'}
                {type === 'tool' && '工具'}
              </Tag>
            ))}
          </div>
        )}
      </Card>
    </div>
  );
};

export default KnowledgeGraph;
