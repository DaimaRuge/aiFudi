import React, { useEffect, useState } from 'react';
import {
  Card,
  Upload,
  Button,
  List,
  Modal,
  Typography,
  Tag,
  message,
  Popconfirm,
  Empty,
  Spin,
  Progress,
} from 'antd';
import {
  InboxOutlined,
  FileTextOutlined,
  DeleteOutlined,
  EyeOutlined,
  PdfOutlined,
  FileOutlined,
  FileWordOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { documentApi } from '../services/api';
import { Document, DocumentDetail } from '../types';

const { Dragger } = Upload;
const { Title, Text, Paragraph } = Typography;

const Documents: React.FC = () => {
  const navigate = useNavigate();
  const { id: documentId } = useParams();
  const [loading, setLoading] = useState(false);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocument, setSelectedDocument] = useState<DocumentDetail | null>(null);
  const [detailModalVisible, setDetailModalVisible] = useState(false);
  const [uploading, setUploading] = useState(false);

  useEffect(() => {
    fetchDocuments();
    if (documentId) {
      fetchDocumentDetail(documentId);
    }
  }, [documentId]);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      const data = await documentApi.list();
      setDocuments(data);
    } catch (error) {
      message.error('获取文档列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchDocumentDetail = async (id: string) => {
    try {
      const data = await documentApi.get(id);
      setSelectedDocument(data);
      setDetailModalVisible(true);
    } catch (error) {
      message.error('获取文档详情失败');
    }
  };

  const handleUpload = async (file: File) => {
    const allowedTypes = [
      'application/pdf',
      'text/plain',
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    ];

    if (!allowedTypes.includes(file.type)) {
      message.error('只支持 PDF、TXT、DOCX 格式的文件');
      return false;
    }

    setUploading(true);
    try {
      await documentApi.upload(file);
      message.success('文档上传成功');
      fetchDocuments();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '上传失败');
    } finally {
      setUploading(false);
    }

    return false;
  };

  const handleDelete = async (id: string) => {
    try {
      await documentApi.delete(id);
      message.success('文档已删除');
      fetchDocuments();
    } catch (error) {
      message.error('删除失败');
    }
  };

  const getFileIcon = (mimeType: string) => {
    if (mimeType === 'application/pdf') return <PdfOutlined style={{ color: '#ff4d4f' }} />;
    if (mimeType.includes('word')) return <FileWordOutlined style={{ color: '#1890ff' }} />;
    return <FileOutlined style={{ color: '#52c41a' }} />;
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        文档管理
      </Title>

      {/* 上传区域 */}
      <Card style={{ marginBottom: '24px' }}>
        <Dragger
          accept=".pdf,.txt,.docx"
          showUploadList={false}
          beforeUpload={handleUpload}
          disabled={uploading}
        >
          {uploading ? (
            <div style={{ padding: '40px 0' }}>
              <Spin size="large" />
              <p style={{ marginTop: '16px', color: '#1890ff' }}>正在上传和处理...</p>
            </div>
          ) : (
            <>
              <p className="ant-upload-drag-icon">
                <InboxOutlined style={{ color: '#1890ff' }} />
              </p>
              <p className="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p className="ant-upload-hint">支持 PDF、TXT、DOCX 格式，单文件最大 50MB</p>
            </>
          )}
        </Dragger>
      </Card>

      {/* 文档列表 */}
      <Card title={`文档列表 (${documents.length})`}>
        {loading ? (
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" />
          </div>
        ) : documents.length === 0 ? (
          <Empty description="暂无文档，请上传" />
        ) : (
          <List
            grid={{ gutter: 16, xs: 1, sm: 2, md: 3, lg: 3, xl: 4, xxl: 4 }}
            dataSource={documents}
            renderItem={(doc) => (
              <List.Item>
                <Card
                  hoverable
                  className="document-card"
                  actions={[
                    <EyeOutlined
                      key="view"
                      onClick={() => {
                        setSelectedDocument(null);
                        fetchDocumentDetail(doc.id);
                      }}
                    />,
                    <Popconfirm
                      key="delete"
                      title="确定要删除这个文档吗？"
                      onConfirm={() => handleDelete(doc.id)}
                    >
                      <DeleteOutlined style={{ color: '#ff4d4f' }} />
                    </Popconfirm>,
                  ]}
                >
                  <Card.Meta
                    avatar={getFileIcon(doc.mime_type || '')}
                    title={
                      <Text ellipsis style={{ maxWidth: '200px' }}>
                        {doc.title}
                      </Text>
                    }
                    description={
                      <div>
                        <div>{formatFileSize(doc.file_size || 0)}</div>
                        <div>{doc.word_count} 字</div>
                        <Tag color={doc.is_processed ? 'success' : 'processing'}>
                          {doc.is_processed ? '已处理' : '处理中'}
                        </Tag>
                      </div>
                    }
                  />
                </Card>
              </List.Item>
            )}
          />
        )}
      </Card>

      {/* 文档详情弹窗 */}
      <Modal
        title={
          selectedDocument ? (
            <Space>
              {getFileIcon(selectedDocument.mime_type || '')}
              {selectedDocument.title}
            </Space>
          ) : (
            '文档详情'
          )
        }
        open={detailModalVisible}
        onCancel={() => setDetailModalVisible(false)}
        footer={[
          <Button key="chat" type="primary" onClick={() => navigate('/chat')}>
            与文档对话
          </Button>,
          <Button key="close" onClick={() => setDetailModalVisible(false)}>
            关闭
          </Button>,
        ]}
        width={800}
      >
        {selectedDocument && (
          <div>
            <Card size="small" style={{ marginBottom: '16px' }}>
              <Row gutter={[16, 16]}>
                <Col span={8}>
                  <Statistic title="字数" value={selectedDocument.word_count} />
                </Col>
                <Col span={8}>
                  <Statistic title="页数" value={selectedDocument.page_count} />
                </Col>
                <Col span={8}>
                  <Statistic title="大小" value={formatFileSize(selectedDocument.file_size || 0)} />
                </Col>
              </Row>
            </Card>

            {selectedDocument.summary && (
              <div style={{ marginBottom: '16px' }}>
                <Title level={5}>摘要</Title>
                <Paragraph>{selectedDocument.summary}</Paragraph>
              </div>
            )}

            {selectedDocument.content && (
              <div>
                <Title level={5}>内容预览</Title>
                <Paragraph
                  ellipsis={{ rows: 10, expandable: true }}
                  style={{
                    maxHeight: '400px',
                    overflow: 'auto',
                    whiteSpace: 'pre-wrap',
                    background: '#f5f5f5',
                    padding: '16px',
                    borderRadius: '8px',
                  }}
                >
                  {selectedDocument.content}
                </Paragraph>
              </div>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
};

// 需要导入 Row, Col, Space, Statistic
import { Row, Col, Space, Statistic } from 'antd';

export default Documents;
