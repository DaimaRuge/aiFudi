import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Button } from 'antd';
import { Outlet, useNavigate, useLocation } from 'react-router-dom';
import {
  HomeOutlined,
  FileTextOutlined,
  ApiOutlined,
  MessageOutlined,
  BookOutlined,
  LogoutOutlined,
  UserOutlined,
} from '@ant-design/icons';
import { useAuth } from '../../hooks/useAuth';

const { Header, Sider, Content } = Layout;

const MainLayout: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '仪表盘',
    },
    {
      key: '/documents',
      icon: <FileTextOutlined />,
      label: '文档管理',
    },
    {
      key: '/knowledge',
      icon: <ApiOutlined />,
      label: '知识图谱',
    },
    {
      key: '/chat',
      icon: <MessageOutlined />,
      label: 'AI 对话',
    },
    {
      key: '/learning',
      icon: <BookOutlined />,
      label: '学习路径',
    },
  ];

  const userMenuItems = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人信息',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  const handleMenuClick = (key: string) => {
    if (key === 'logout') {
      logout();
      navigate('/login');
    }
  };

  return (
    <Layout className="app-layout">
      <Header className="app-header">
        <div className="logo">
          <BookOutlined style={{ fontSize: '28px' }} />
          <span>终身学习系统</span>
        </div>
        <div className="user-info">
          <Dropdown
            menu={{
              items: userMenuItems,
              onClick: ({ key }) => handleMenuClick(key),
            }}
            placement="bottomRight"
          >
            <div style={{ cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Avatar icon={<UserOutlined />} style={{ backgroundColor: 'rgba(255,255,255,0.2)' }} />
              <span>{user?.username}</span>
            </div>
          </Dropdown>
        </div>
      </Header>
      <Layout>
        <Sider width={220} className="app-sider">
          <Menu
            mode="inline"
            selectedKeys={[location.pathname.split('/').slice(0, 2).join('/') || '/']}
            style={{ height: '100%', borderRight: 0 }}
            items={menuItems}
            onClick={({ key }) => navigate(key)}
          />
        </Sider>
        <Content className="app-content">
          <Outlet />
        </Content>
      </Layout>
    </Layout>
  );
};

export default MainLayout;
