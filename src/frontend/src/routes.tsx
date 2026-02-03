// React Router Configuration
//路由配置

import { Routes, Route, Navigate } from 'react-router-dom';
import { Layout } from './components/Layout';
import { HomePage } from './pages/HomePage';
import { DocumentPage } from './pages/DocumentPage';
import { SearchPage } from './pages/SearchPage';
import { CategoryPage } from './pages/CategoryPage';
import { SettingPage } from './pages/SettingPage';

export function AppRoutes() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<HomePage />} />
        <Route path="documents" element={<DocumentPage />} />
        <Route path="documents/:id" element={<DocumentPage />} />
        <Route path="search" element={<SearchPage />} />
        <Route path="categories" element={<CategoryPage />} />
        <Route path="settings" element={<SettingPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
