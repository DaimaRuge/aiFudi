// Document Page
//文档列表页面

import React, { useEffect, useState } from 'react';
import {
  Table,
  Button,
  Space,
  Tag,
  Input,
  Select,
  Modal,
  message,
  Dropdown,
} from 'antd';
import {
  SearchOutlined,
  UploadOutlined,
  DeleteOutlined,
  TagOutlined,
  FilterOutlined,
  MoreOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useDocumentStore } from '../stores/documentStore';
import './pages.css';

const { Search } = Input;

export function DocumentPage() {
  const {
    documents,
    loading,
    total,
    page,
    selectedCategory,
    fetchDocuments,
    selectCategory,
    deleteDocument,
    classifyDocument,
  } = useDocumentStore();

  const [searchText, setSearchText] = useState('');
  const [statusFilter, setStatusFilter] = useState<string | null>(null);

  useEffect(() => {
    fetchDocuments();
  }, [selectedCategory, statusFilter]);

  const handleSearch = (value: string) => {
    fetchDocuments({ search: value });
  };

  const handleDelete = async (id: string) => {
    Modal.confirm({
      title: '确认删除',
      content: '确定要删除此文档吗？',
      onOk: async () => {
        try {
          await deleteDocument(id);
          message.success('删除成功');
        } catch {
          message.error('删除失败');
        }
      },
    });
  };

  const handleClassify = async (id: string) => {
    try {
      await classifyDocument(id);
      message.success('AI 分类完成');
    } catch {
      message.error('分类失败');
    }
  };

  const columns = [
    {
      title: '文档',
      dataIndex: 'title',
      key: 'title',
      render: (title: string, record: any) => (
        <div>
          <div style={{ fontWeight: 500 }}>{title || record.file_name}</div>
          <div style={{ color: '#999', fontSize: 12 }}>
            {record.file_name}
          </div>
        </div>
      ),
    },
    {
      title: '分类',
      dataIndex: 'category_path',
      key: 'category',
      render: (path: string) =>
        path ? <Tag color="blue">{path}</Tag> : <Tag>未分类</Tag>,
    },
    {
      title: '状态',
      dataIndex: 'status',
      key: 'status',
      render: (status: string) => (
        <Tag color={status === 'classified' ? 'green' : 'orange'}>
          {status === 'classified' ? '已分类' : '待分类'}
        </Tag>
      ),
    },
    {
      title: '更新时间',
      dataIndex: 'updated_at',
      key: 'updated_at',
      render: (date: string) => new Date(date).toLocaleString(),
    },
    {
      title: '操作',
      key: 'action',
      width: 150,
      render: (_: any, record: any) => (
        <Space size="small">
          <Button
            size="small"
            icon={<TagOutlined />}
            onClick={() => handleClassify(record.id)}
          >
            AI 分类
          </Button>
          <Dropdown
            menu={{
              items: [
                {
                  key: 'delete',
                  icon: <DeleteOutlined />,
                  label: '删除',
                  danger: true,
                  onClick: () => handleDelete(record.id),
                },
              ],
            }}
          >
            <Button size="small" icon={<MoreOutlined />} />
          </Dropdown>
        </Space>
      ),
    },
  ];

  return (
    <div className="document-page">
      <div className="page-header">
        <h1>📄 文档管理</h1>
        <Space>
          <Search
            placeholder="搜索文档..."
            onSearch={handleSearch}
            style={{ width: 250 }}
            allowClear
          />
          <Select
            placeholder="状态筛选"
            allowClear
            style={{ width: 120 }}
            onChange={setStatusFilter}
            options={[
              { label: '全部', value: null },
              { label: '待分类', value: 'pending' },
              { label: '已分类', value: 'classified' },
            ]}
          />
          <Button icon={<ReloadOutlined />} onClick={() => fetchDocuments()}>
            刷新
          </Button>
        </Space>
      </div>

      <Table
        columns={columns}
        dataSource={documents}
        rowKey="id"
        loading={loading}
        pagination={{
          total,
          current: page,
          pageSize: 20,
          onChange: (p) => fetchDocuments({ page: p }),
        }}
      />
    </div>
  );
}
