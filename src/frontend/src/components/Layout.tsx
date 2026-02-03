// Layout Component
//布局组件

import React, { useState, useEffect } from 'react';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  Layout as AntLayout,
  Menu,
  Input,
  Badge,
  Avatar,
  Dropdown,
  Space,
} from 'antd';
import {
  HomeOutlined,
  FileSearchOutlined,
  AppstoreOutlined,
  SettingOutlined,
  BellOutlined,
  UserOutlined,
  LogoutOutlined,
  BookOutlined,
} from '@ant-design/icons';
import { useDocumentStore } from '../stores/documentStore';
import './Layout.css';

const { Header, Sider, Content } = AntLayout;

export function Layout() {
  const [collapsed, setCollapsed] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { searchDocuments, searchQuery } = useDocumentStore();

  const menuItems = [
    { key: '/', icon: <HomeOutlined />, label: '首页' },
    { key: '/documents', icon: <FileSearchOutlined />, label: '文档' },
    { key: '/search', icon: <BookOutlined />, label: '搜索' },
    { key: '/categories', icon: <AppstoreOutlined />, label: '分类' },
    { key: '/settings', icon: <SettingOutlined />, label: '设置' },
  ];

  const userMenuItems = [
    { key: 'profile', icon: <UserOutlined />, label: '个人资料' },
    { type: 'divider' as const },
    { key: 'logout', icon: <LogoutOutlined />, label: '退出登录' },
  ];

  const handleSearch = (value: string) => {
    searchDocuments(value);
    navigate('/search');
  };

  return (
    <AntLayout className="app-layout">
      <AntLayout>
        <Header className="app-header">
          <div className="app-logo">
            <BookOutlined />
            <span>天一阁</span>
          </div>
          
          <Input.Search
            placeholder="搜索文档..."
            className="search-box"
            value={searchQuery}
            onSearch={handleSearch}
            allowClear
            enterButton
          />
          
          <Space size="middle">
            <Badge count={3}>
              <BellOutlined style={{ fontSize: 18, cursor: 'pointer' }} />
            </Badge>
            
            <Dropdown menu={{ items: userMenuItems }} trigger={['click']}>
              <Avatar
                style={{ backgroundColor: '#1A73E8', cursor: 'pointer' }}
                icon={<UserOutlined />}
              />
            </Dropdown>
          </Space>
        </Header>
        
        <AntLayout>
          <Sider
            width={220}
            collapsedWidth={64}
            collapsed={collapsed}
            className="app-sider"
          >
            <Menu
              mode="inline"
              selectedKeys={[location.pathname]}
              items={menuItems}
              onClick={({ key }) => navigate(key)}
              style={{ borderRight: 0 }}
            />
          </Sider>
          
          <Content className="app-content">
            <Outlet />
          </Content>
        </AntLayout>
      </AntLayout>
    </AntLayout>
  );
}
