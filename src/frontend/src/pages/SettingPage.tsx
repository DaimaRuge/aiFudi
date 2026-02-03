// Settings Page
//设置页面

import React from 'react';
import { Card, Form, Input, Button, Switch, Select, Divider, message } from 'antd';
import { SaveOutlined } from '@ant-design/icons';

export function SettingPage() {
  const [form] = Form.useForm();

  const handleSave = async () => {
    try {
      await form.validateFields();
      message.success('设置已保存');
    } catch {
      message.error('保存失败');
    }
  };

  return (
    <div className="settings-page">
      <h1>⚙️ 系统设置</h1>
      
      <Card title="文档扫描" style={{ marginBottom: 16 }}>
        <Form layout="vertical" form={form}>
          <Form.Item label="扫描路径">
            <Input placeholder="~/Documents" />
          </Form.Item>
          <Form.Item label="递归扫描">
            <Switch defaultChecked />
          </Form.Item>
        </Form>
      </Card>
      
      <Card title="AI 配置" style={{ marginBottom: 16 }}>
        <Form layout="vertical" form={form}>
          <Form.Item label="AI 模型提供商">
            <Select
              defaultValue="openai"
              options={[
                { label: 'OpenAI', value: 'openai' },
                { label: 'Anthropic Claude', value: 'anthropic' },
                { label: '智谱 GLM', value: 'zhipu' },
              ]}
            />
          </Form.Item>
          <Form.Item label="API Key">
            <Input.Password placeholder="输入 API Key" />
          </Form.Item>
          <Form.Item label="自动分类">
            <Switch defaultChecked />
          </Form.Item>
        </Form>
      </Card>
      
      <Card title="同步设置">
        <Form layout="vertical" form={form}>
          <Form.Item label="启用云端同步">
            <Switch />
          </Form.Item>
          <Form.Item label="同步频率">
            <Select
              defaultValue="realtime"
              options={[
                { label: '实时同步', value: 'realtime' },
                { label: '每小时', value: 'hourly' },
                { label: '每天', value: 'daily' },
              ]}
            />
          </Form.Item>
        </Form>
      </Card>
      
      <div style={{ marginTop: 16 }}>
        <Button type="primary" icon={<SaveOutlined />} onClick={handleSave}>
          保存设置
        </Button>
      </div>
    </div>
  );
}
