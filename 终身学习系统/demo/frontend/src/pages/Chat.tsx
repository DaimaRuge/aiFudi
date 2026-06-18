import React, { useEffect, useState, useRef } from 'react';
import {
  Card,
  Input,
  Button,
  List,
  Typography,
  message,
  Spin,
  Empty,
  Select,
  Space,
  Drawer,
} from 'antd';
import {
  SendOutlined,
  PlusOutlined,
  DeleteOutlined,
  MessageOutlined,
  FileTextOutlined,
} from '@ant-design/icons';
import { chatApi, documentApi } from '../services/api';
import { ChatSession, ChatMessage, Document } from '../types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const Chat: React.FC = () => {
  const [loading, setLoading] = useState(false);
  const [sending, setSending] = useState(false);
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [currentSession, setCurrentSession] = useState<ChatSession | null>(null);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [inputMessage, setInputMessage] = useState('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [selectedDocumentId, setSelectedDocumentId] = useState<string | undefined>();
  const [drawerVisible, setDrawerVisible] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    fetchSessions();
    fetchDocuments();
  }, []);

  useEffect(() => {
    if (currentSession) {
      fetchMessages(currentSession.id);
    }
  }, [currentSession]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const fetchSessions = async () => {
    try {
      setLoading(true);
      const data = await chatApi.listSessions();
      setSessions(data);
      if (data.length > 0 && !currentSession) {
        setCurrentSession(data[0]);
      }
    } catch (error) {
      message.error('获取会话列表失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchDocuments = async () => {
    try {
      const data = await documentApi.list();
      setDocuments(data);
    } catch (error) {
      console.error('获取文档列表失败:', error);
    }
  };

  const fetchMessages = async (sessionId: string) => {
    try {
      setLoading(true);
      const data = await chatApi.getMessages(sessionId);
      setMessages(data);
    } catch (error) {
      message.error('获取消息失败');
    } finally {
      setLoading(false);
    }
  };

  const createNewSession = async () => {
    try {
      const data = await chatApi.createSession('新对话', selectedDocumentId);
      setSessions([data, ...sessions]);
      setCurrentSession(data);
      setMessages([]);
      setDrawerVisible(false);
      message.success('创建新对话成功');
    } catch (error) {
      message.error('创建会话失败');
    }
  };

  const deleteSession = async (sessionId: string) => {
    try {
      await chatApi.deleteSession(sessionId);
      const newSessions = sessions.filter((s) => s.id !== sessionId);
      setSessions(newSessions);
      if (currentSession?.id === sessionId) {
        setCurrentSession(newSessions.length > 0 ? newSessions[0] : null);
        setMessages([]);
      }
      message.success('删除成功');
    } catch (error) {
      message.error('删除失败');
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim()) return;

    setSending(true);
    try {
      const response = await chatApi.sendMessage(
        inputMessage,
        currentSession?.id,
        selectedDocumentId
      );

      // 添加用户消息
      const userMessage: ChatMessage = {
        id: 'temp-user',
        session_id: response.session_id,
        role: 'user',
        content: inputMessage,
        created_at: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage, response.message]);
      setInputMessage('');

      // 如果是新会话，更新会话列表
      if (!currentSession) {
        fetchSessions();
      }
    } catch (error) {
      message.error('发送消息失败');
    } finally {
      setSending(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div style={{ display: 'flex', height: 'calc(100vh - 112px)', gap: '16px' }}>
      {/* 会话列表 */}
      <Card
        style={{ width: '280px', display: 'flex', flexDirection: 'column' }}
        title="对话列表"
        extra={
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => setDrawerVisible(true)}
          >
            新对话
          </Button>
        }
      >
        <div style={{ flex: 1, overflow: 'auto' }}>
          {loading && sessions.length === 0 ? (
            <Spin />
          ) : sessions.length === 0 ? (
            <Empty description="暂无对话" />
          ) : (
            <List
              dataSource={sessions}
              renderItem={(session) => (
                <List.Item
                  onClick={() => setCurrentSession(session)}
                  style={{
                    cursor: 'pointer',
                    backgroundColor: currentSession?.id === session.id ? '#f0f7ff' : 'transparent',
                    borderRadius: '8px',
                    padding: '12px',
                  }}
                  actions={[
                    <DeleteOutlined
                      key="delete"
                      onClick={(e) => {
                        e.stopPropagation();
                        deleteSession(session.id);
                      }}
                      style={{ color: '#ff4d4f' }}
                    />,
                  ]}
                >
                  <List.Item.Meta
                    avatar={<MessageOutlined />}
                    title={session.title}
                    description={new Date(session.updated_at).toLocaleDateString()}
                  />
                </List.Item>
              )}
            />
          )}
        </div>
      </Card>

      {/* 聊天区域 */}
      <Card style={{ flex: 1, display: 'flex', flexDirection: 'column' }} bodyStyle={{ flex: 1, display: 'flex', flexDirection: 'column', padding: 0 }}>
        {/* 文档选择 */}
        <div style={{ padding: '12px 16px', borderBottom: '1px solid #f0f0f0' }}>
          <Space>
            <Text>关联文档:</Text>
            <Select
              style={{ width: 200 }}
              placeholder="选择关联文档（可选）"
              allowClear
              value={selectedDocumentId}
              onChange={(value) => setSelectedDocumentId(value)}
            >
              {documents.map((doc) => (
                <Select.Option key={doc.id} value={doc.id}>
                  <FileTextOutlined /> {doc.title}
                </Select.Option>
              ))}
            </Select>
          </Space>
        </div>

        {/* 消息列表 */}
        <div className="chat-messages" style={{ flex: 1, overflow: 'auto', padding: '24px' }}>
          {loading ? (
            <div style={{ textAlign: 'center', padding: '40px' }}>
              <Spin size="large" />
            </div>
          ) : messages.length === 0 ? (
            <Empty description="开始对话吧" style={{ marginTop: '100px' }} />
          ) : (
            messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-message ${msg.role}`}
                style={{
                  display: 'flex',
                  marginBottom: '20px',
                  justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start',
                }}
              >
                <div
                  style={{
                    maxWidth: '70%',
                    padding: '12px 16px',
                    borderRadius: '16px',
                    backgroundColor: msg.role === 'user' ? '#1890ff' : '#f0f0f0',
                    color: msg.role === 'user' ? 'white' : '#333',
                    borderBottomRightRadius: msg.role === 'user' ? '4px' : '16px',
                    borderBottomLeftRadius: msg.role === 'assistant' ? '4px' : '16px',
                  }}
                >
                  <Paragraph style={{ margin: 0, color: 'inherit', whiteSpace: 'pre-wrap' }}>
                    {msg.content}
                  </Paragraph>
                </div>
              </div>
            ))
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* 输入区域 */}
        <div className="chat-input-area" style={{ padding: '16px 24px', borderTop: '1px solid #f0f0f0', background: '#fafafa' }}>
          <div style={{ display: 'flex', gap: '12px' }}>
            <TextArea
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="输入消息... (Enter 发送，Shift+Enter 换行)"
              autoSize={{ minRows: 1, maxRows: 4 }}
              style={{ flex: 1 }}
            />
            <Button
              type="primary"
              icon={<SendOutlined />}
              onClick={sendMessage}
              loading={sending}
              disabled={!inputMessage.trim()}
            >
              发送
            </Button>
          </div>
        </div>
      </Card>

      {/* 新建对话抽屉 */}
      <Drawer
        title="新建对话"
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        width={400}
      >
        <div style={{ marginBottom: '24px' }}>
          <Text>选择关联文档（可选）:</Text>
          <Select
            style={{ width: '100%', marginTop: '8px' }}
            placeholder="选择文档"
            allowClear
            value={selectedDocumentId}
            onChange={(value) => setSelectedDocumentId(value)}
          >
            {documents.map((doc) => (
              <Select.Option key={doc.id} value={doc.id}>
                <FileTextOutlined /> {doc.title}
              </Select.Option>
            ))}
          </Select>
        </div>
        <Button type="primary" block onClick={createNewSession}>
          创建对话
        </Button>
      </Drawer>
    </div>
  );
};

export default Chat;
