// Category Page
//分类管理页面

import React, { useEffect, useState } from 'react';
import { Tree, Button, Modal, Form, Input, message, Card } from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import { useDocumentStore } from '../stores/documentStore';
import './pages.css';

export function CategoryPage() {
  const { categories, fetchCategories, selectCategory } = useDocumentStore();
  const [form] = Form.useForm();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [parentPath, setParentPath] = useState<string | null>(null);

  useEffect(() => {
    fetchCategories();
  }, []);

  const handleAddCategory = (path: string | null) => {
    setParentPath(path);
    setIsModalOpen(true);
    form.resetFields();
  };

  const handleSubmit = async (values: { name: string }) => {
    try {
      message.success('分类创建成功');
      setIsModalOpen(false);
      fetchCategories();
    } catch {
      message.error('创建失败');
    }
  };

  const treeData = categories.map((cat: any) => ({
    title: (
      <span>
        {cat.name}
        <Button
          type="text"
          size="small"
          icon={<PlusOutlined />}
          onClick={(e) => {
            e.stopPropagation();
            handleAddCategory(cat.path);
          }}
        />
      </span>
    ),
    key: cat.id,
    path: cat.path,
    children: cat.children?.map((child: any) => ({
      title: child.name,
      key: child.id,
      path: child.path,
    })),
  }));

  return (
    <div className="category-page">
      <div className="page-header">
        <h1>🏷️ 分类管理</h1>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => handleAddCategory(null)}
        >
          添加分类
        </Button>
      </div>

      <Card>
        <Tree
          treeData={treeData}
          onSelect={([key]) => {
            if (key) {
              selectCategory(key as string);
            }
          }}
          showIcon
          defaultExpandAll
        />
      </Card>

      <Modal
        title="添加分类"
        open={isModalOpen}
        onCancel={() => setIsModalOpen(false)}
        onOk={() => form.submit()}
      >
        <Form form={form} onFinish={handleSubmit}>
          <Form.Item
            name="name"
            label="分类名称"
            rules={[{ required: true, message: '请输入分类名称' }]}
          >
            <Input placeholder="输入分类名称" />
          </Form.Item>
          {parentPath && (
            <div style={{ color: '#999' }}>
              父分类: {parentPath}
            </div>
          )}
        </Form>
      </Modal>
    </div>
  );
}
