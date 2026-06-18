import React, { useEffect, useState } from 'react';
import {
  Card,
  Button,
  List,
  Typography,
  Modal,
  Form,
  Input,
  Select,
  message,
  Progress,
  Tag,
  Empty,
  Spin,
  Drawer,
  Steps,
  Checkbox,
  Space,
  Descriptions,
} from 'antd';
import {
  PlusOutlined,
  BookOutlined,
  ClockCircleOutlined,
  CheckCircleOutlined,
  DeleteOutlined,
  RobotOutlined,
} from '@ant-design/icons';
import { useNavigate, useParams } from 'react-router-dom';
import { learningApi } from '../services/api';
import { LearningPath, LearningUnit } from '../types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

const LearningPaths: React.FC = () => {
  const navigate = useNavigate();
  const { id: pathId } = useParams();
  const [loading, setLoading] = useState(false);
  const [paths, setPaths] = useState<LearningPath[]>([]);
  const [selectedPath, setSelectedPath] = useState<LearningPath | null>(null);
  const [createModalVisible, setCreateModalVisible] = useState(false);
  const [generateModalVisible, setGenerateModalVisible] = useState(false);
  const [detailDrawerVisible, setDetailDrawerVisible] = useState(false);
  const [completingUnit, setCompletingUnit] = useState<string | null>(null);
  const [form] = Form.useForm();
  const [generateForm] = Form.useForm();

  useEffect(() => {
    fetchPaths();
  }, []);

  useEffect(() => {
    if (pathId) {
      fetchPathDetail(pathId);
    }
  }, [pathId]);

  const fetchPaths = async () => {
    try {
      setLoading(true);
      const data = await learningApi.listPaths();
      setPaths(data);
    } catch (error) {
      message.error('获取学习路径失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchPathDetail = async (id: string) => {
    try {
      setLoading(true);
      const data = await learningApi.getPath(id);
      setSelectedPath(data);
      setDetailDrawerVisible(true);
    } catch (error) {
      message.error('获取学习路径详情失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCreate = async (values: any) => {
    try {
      await learningApi.createPath(values);
      message.success('创建成功');
      setCreateModalVisible(false);
      form.resetFields();
      fetchPaths();
    } catch (error) {
      message.error('创建失败');
    }
  };

  const handleGenerate = async (values: any) => {
    try {
      setLoading(true);
      await learningApi.generatePath(values.topic, values.difficulty);
      message.success('AI 生成学习路径成功');
      setGenerateModalVisible(false);
      generateForm.resetFields();
      fetchPaths();
    } catch (error) {
      message.error('生成失败');
    } finally {
      setLoading(false);
    }
  };

  const handleCompleteUnit = async (pathId: string, unitId: string) => {
    try {
      setCompletingUnit(unitId);
      await learningApi.completeUnit(pathId, unitId);
      message.success('已完成该学习单元');

      // 刷新数据
      fetchPaths();
      if (selectedPath?.id === pathId) {
        const updated = await learningApi.getPath(pathId);
        setSelectedPath(updated);
      }
    } catch (error) {
      message.error('操作失败');
    } finally {
      setCompletingUnit(null);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await learningApi.deletePath(id);
      message.success('删除成功');
      fetchPaths();
      if (selectedPath?.id === id) {
        setDetailDrawerVisible(false);
        setSelectedPath(null);
      }
    } catch (error) {
      message.error('删除失败');
    }
  };

  const getDifficultyColor = (difficulty: string) => {
    const colors: Record<string, string> = {
      beginner: 'green',
      intermediate: 'blue',
      advanced: 'red',
    };
    return colors[difficulty] || 'default';
  };

  const getDifficultyText = (difficulty: string) => {
    const texts: Record<string, string> = {
      beginner: '入门',
      intermediate: '进阶',
      advanced: '高级',
    };
    return texts[difficulty] || difficulty;
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      active: 'processing',
      completed: 'success',
      paused: 'warning',
    };
    return colors[status] || 'default';
  };

  const getStatusText = (status: string) => {
    const texts: Record<string, string> = {
      active: '进行中',
      completed: '已完成',
      paused: '已暂停',
    };
    return texts[status] || status;
  };

  const getTotalDuration = (units: LearningUnit[]) => {
    return units.reduce((sum, unit) => sum + unit.duration_minutes, 0);
  };

  return (
    <div>
      <Title level={2} style={{ marginBottom: '24px' }}>
        学习路径
      </Title>

      {/* 操作按钮 */}
      <Card style={{ marginBottom: '24px' }}>
        <Space>
          <Button type="primary" icon={<PlusOutlined />} onClick={() => setCreateModalVisible(true)}>
            手动创建
          </Button>
          <Button icon={<RobotOutlined />} onClick={() => setGenerateModalVisible(true)}>
            AI 生成
          </Button>
        </Space>
      </Card>

      {/* 学习路径列表 */}
      {loading && paths.length === 0 ? (
        <Card>
          <div style={{ textAlign: 'center', padding: '40px' }}>
            <Spin size="large" />
          </div>
        </Card>
      ) : paths.length === 0 ? (
        <Card>
          <Empty description="暂无学习路径，点击上方按钮创建" />
        </Card>
      ) : (
        <List
          grid={{ gutter: 16, xs: 1, sm: 2, md: 2, lg: 3, xl: 3, xxl: 4 }}
          dataSource={paths}
          renderItem={(path) => (
            <List.Item>
              <Card
                hoverable
                onClick={() => {
                  setSelectedPath(path);
                  setDetailDrawerVisible(true);
                }}
                actions={[
                  <DeleteOutlined
                    key="delete"
                    onClick={(e) => {
                      e.stopPropagation();
                      Modal.confirm({
                        title: '确认删除',
                        content: '确定要删除这个学习路径吗？',
                        onOk: () => handleDelete(path.id),
                      });
                    }}
                    style={{ color: '#ff4d4f' }}
                  />,
                ]}
              >
                <Card.Meta
                  avatar={<BookOutlined style={{ fontSize: '32px', color: '#1890ff' }} />}
                  title={path.title}
                  description={
                    <div>
                      <div style={{ marginBottom: '8px' }}>
                        <Tag color={getDifficultyColor(path.difficulty)}>
                          {getDifficultyText(path.difficulty)}
                        </Tag>
                        <Tag color={getStatusColor(path.status)}>
                          {getStatusText(path.status)}
                        </Tag>
                      </div>
                      <Progress percent={Math.round(path.progress * 100)} size="small" />
                      <Text type="secondary" style={{ fontSize: '12px' }}>
                        {path.units.length} 个单元 · {getTotalDuration(path.units)} 分钟
                      </Text>
                    </div>
                  }
                />
              </Card>
            </List.Item>
          )}
        />
      )}

      {/* 手动创建弹窗 */}
      <Modal
        title="创建学习路径"
        open={createModalVisible}
        onCancel={() => setCreateModalVisible(false)}
        footer={null}
      >
        <Form form={form} layout="vertical" onFinish={handleCreate}>
          <Form.Item
            name="title"
            label="标题"
            rules={[{ required: true, message: '请输入标题' }]}
          >
            <Input placeholder="学习路径标题" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="描述这个学习路径的内容" />
          </Form.Item>
          <Form.Item name="goal" label="学习目标">
            <Input placeholder="学习目标" />
          </Form.Item>
          <Form.Item name="difficulty" label="难度" initialValue="intermediate">
            <Select>
              <Select.Option value="beginner">入门</Select.Option>
              <Select.Option value="intermediate">进阶</Select.Option>
              <Select.Option value="advanced">高级</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" block>
              创建
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* AI 生成弹窗 */}
      <Modal
        title="AI 生成学习路径"
        open={generateModalVisible}
        onCancel={() => setGenerateModalVisible(false)}
        footer={null}
      >
        <Form form={generateForm} layout="vertical" onFinish={handleGenerate}>
          <Form.Item
            name="topic"
            label="学习主题"
            rules={[{ required: true, message: '请输入学习主题' }]}
          >
            <Input placeholder="例如：Python 编程、机器学习、英语口语" />
          </Form.Item>
          <Form.Item name="difficulty" label="难度级别" initialValue="intermediate">
            <Select>
              <Select.Option value="beginner">入门</Select.Option>
              <Select.Option value="intermediate">进阶</Select.Option>
              <Select.Option value="advanced">高级</Select.Option>
            </Select>
          </Form.Item>
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block icon={<RobotOutlined />}>
              AI 生成
            </Button>
          </Form.Item>
        </Form>
      </Modal>

      {/* 详情抽屉 */}
      <Drawer
        title={selectedPath?.title || '学习路径详情'}
        open={detailDrawerVisible}
        onClose={() => setDetailDrawerVisible(false)}
        width={600}
      >
        {selectedPath && (
          <div>
            <Descriptions column={2} style={{ marginBottom: '24px' }}>
              <Descriptions.Item label="难度">
                <Tag color={getDifficultyColor(selectedPath.difficulty)}>
                  {getDifficultyText(selectedPath.difficulty)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Tag color={getStatusColor(selectedPath.status)}>
                  {getStatusText(selectedPath.status)}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="总时长">
                {getTotalDuration(selectedPath.units)} 分钟
              </Descriptions.Item>
              <Descriptions.Item label="单元数">
                {selectedPath.units.length} 个
              </Descriptions.Item>
            </Descriptions>

            {selectedPath.description && (
              <Paragraph style={{ marginBottom: '24px' }}>
                <Text strong>描述：</Text>
                {selectedPath.description}
              </Paragraph>
            )}

            {selectedPath.goal && (
              <Paragraph style={{ marginBottom: '24px' }}>
                <Text strong>学习目标：</Text>
                {selectedPath.goal}
              </Paragraph>
            )}

            <div style={{ marginBottom: '16px' }}>
              <Text strong>学习进度</Text>
              <Progress percent={Math.round(selectedPath.progress * 100)} />
            </div>

            <Title level={5}>学习单元</Title>
            <div className="unit-list">
              {selectedPath.units.map((unit, index) => (
                <div
                  key={unit.id}
                  className={`unit-item ${unit.is_completed ? 'completed' : ''}`}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    padding: '16px',
                    background: unit.is_completed ? '#f6ffed' : '#fafafa',
                    borderRadius: '8px',
                    marginBottom: '12px',
                    borderLeft: unit.is_completed ? '4px solid #52c41a' : '4px solid transparent',
                  }}
                >
                  <div style={{ marginRight: '16px' }}>
                    {unit.is_completed ? (
                      <CheckCircleOutlined style={{ fontSize: '24px', color: '#52c41a' }} />
                    ) : (
                      <Text style={{ fontSize: '18px', fontWeight: 'bold', color: '#999' }}>
                        {index + 1}
                      </Text>
                    )}
                  </div>
                  <div style={{ flex: 1 }}>
                    <Text strong>{unit.title}</Text>
                    {unit.description && (
                      <Text type="secondary" style={{ display: 'block', fontSize: '13px' }}>
                        {unit.description}
                      </Text>
                    )}
                    <div style={{ marginTop: '8px' }}>
                      <Space>
                        <Tag>{getDifficultyText(unit.difficulty)}</Tag>
                        <Text type="secondary">
                          <ClockCircleOutlined /> {unit.duration_minutes} 分钟
                        </Text>
                      </Space>
                    </div>
                  </div>
                  {!unit.is_completed && (
                    <Button
                      type="primary"
                      size="small"
                      loading={completingUnit === unit.id}
                      onClick={() => handleCompleteUnit(selectedPath.id, unit.id)}
                    >
                      完成
                    </Button>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </Drawer>
    </div>
  );
};

export default LearningPaths;
