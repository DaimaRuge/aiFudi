# 涂鸦云服务API接口文档体系

## 📋 文档概述

本文档系统梳理涂鸦IoT云服务平台的核心API接口体系，涵盖设备管理、功能控制、数据统计、状态监控及云云对接等关键能力。适用于智能电工设备（插座、开关、照明等）的集成开发。

---

## 🏗️ **API体系架构**

### **1. 基础服务层**
- **认证授权**：OAuth2.0、Access Token管理
- **设备接入**：MQTT、HTTP、WebSocket协议支持
- **消息推送**：设备状态变更实时通知

### **2. 设备管理层**
- **设备注册/注销**：设备入网、解绑管理
- **设备信息**：设备属性、能力查询
- **设备分组**：房间、场景分组管理

### **3. 功能控制层**
- **指令下发**：开关控制、模式切换
- **定时任务**：循环定时、随机定时
- **场景联动**：自动化规则配置

### **4. 数据统计层**
- **能耗统计**：电量、功率、电流电压
- **使用分析**：设备使用频率、时长
- **故障监控**：异常状态告警

### **5. 云云对接层**
- **第三方平台**：开放API对接
- **数据同步**：双向数据流转
- **事件回调**：Webhook通知机制

---

## 📊 **核心API接口目录**

### **一、设备管理接口**

#### **1.1 设备注册与认证**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 设备注册 | POST | `/v1.0/devices` | 新设备接入注册 | `product_key`, `uuid`, `auth_key` |
| 设备激活 | POST | `/v1.0/devices/{device_id}/activate` | 设备激活上线 | `device_id`, `activation_code` |
| 设备解绑 | DELETE | `/v1.0/devices/{device_id}` | 移除设备绑定 | `device_id` |
| 设备信息查询 | GET | `/v1.0/devices/{device_id}` | 获取设备详情 | `device_id` |

#### **1.2 设备状态管理**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 设备在线状态 | GET | `/v1.0/devices/{device_id}/status` | 查询设备在线状态 | `device_id` |
| 设备能力查询 | GET | `/v1.0/devices/{device_id}/functions` | 获取设备功能点 | `device_id` |
| 设备属性更新 | PUT | `/v1.0/devices/{device_id}/attributes` | 更新设备属性 | `device_id`, `attributes` |

#### **1.3 设备分组管理**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 创建设备组 | POST | `/v1.0/device-groups` | 创建设备分组 | `name`, `device_ids` |
| 分组设备添加 | POST | `/v1.0/device-groups/{group_id}/devices` | 向分组添加设备 | `group_id`, `device_ids` |
| 分组设备移除 | DELETE | `/v1.0/device-groups/{group_id}/devices` | 从分组移除设备 | `group_id`, `device_ids` |
| 分组设备列表 | GET | `/v1.0/device-groups/{group_id}/devices` | 获取分组设备列表 | `group_id` |

### **二、功能控制接口**

#### **2.1 基础控制指令**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 设备指令下发 | POST | `/v1.0/devices/{device_id}/commands` | 发送控制指令 | `device_id`, `commands` |
| 批量设备控制 | POST | `/v1.0/devices/commands` | 批量控制设备 | `device_commands` |
| 指令状态查询 | GET | `/v1.0/devices/{device_id}/commands/{command_id}` | 查询指令执行状态 | `device_id`, `command_id` |

#### **2.2 定时任务管理**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 创建定时任务 | POST | `/v1.0/devices/{device_id}/timers` | 创建设备定时 | `device_id`, `timer_config` |
| 查询定时列表 | GET | `/v1.0/devices/{device_id}/timers` | 获取设备定时列表 | `device_id` |
| 更新定时任务 | PUT | `/v1.0/timers/{timer_id}` | 修改定时配置 | `timer_id`, `timer_config` |
| 删除定时任务 | DELETE | `/v1.0/timers/{timer_id}` | 删除定时任务 | `timer_id` |

#### **2.3 场景联动接口**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 创建自动化场景 | POST | `/v1.0/scenes` | 创建自动化规则 | `name`, `conditions`, `actions` |
| 触发场景执行 | POST | `/v1.0/scenes/{scene_id}/execute` | 手动触发场景 | `scene_id` |
| 场景状态查询 | GET | `/v1.0/scenes/{scene_id}` | 获取场景详情 | `scene_id` |
| 场景启用/禁用 | PUT | `/v1.0/scenes/{scene_id}/status` | 修改场景状态 | `scene_id`, `enabled` |

### **三、数据统计接口**

#### **3.1 能耗数据统计**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 电量统计查询 | GET | `/v1.0/devices/{device_id}/energy` | 查询设备电量数据 | `device_id`, `start_time`, `end_time` |
| 功率实时数据 | GET | `/v1.0/devices/{device_id}/power` | 获取实时功率 | `device_id` |
| 电流电压查询 | GET | `/v1.0/devices/{device_id}/electrical` | 查询电流电压 | `device_id` |
| 能耗趋势分析 | GET | `/v1.0/devices/{device_id}/energy/trend` | 能耗趋势图表 | `device_id`, `period` |

#### **3.2 使用数据分析**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 设备使用时长 | GET | `/v1.0/devices/{device_id}/usage/duration` | 统计使用时长 | `device_id`, `date_range` |
| 开关次数统计 | GET | `/v1.0/devices/{device_id}/usage/count` | 统计开关次数 | `device_id`, `date_range` |
| 使用时段分析 | GET | `/v1.0/devices/{device_id}/usage/time-distribution` | 使用时段分布 | `device_id` |

#### **3.3 故障监控接口**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 故障状态查询 | GET | `/v1.0/devices/{device_id}/faults` | 查询设备故障 | `device_id` |
| 故障历史记录 | GET | `/v1.0/devices/{device_id}/faults/history` | 故障历史记录 | `device_id`, `start_time`, `end_time` |
| 告警配置管理 | PUT | `/v1.0/devices/{device_id}/alerts` | 配置告警规则 | `device_id`, `alert_rules` |

### **四、状态监控接口**

#### **4.1 实时状态监控**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 设备状态订阅 | POST | `/v1.0/subscriptions` | 订阅状态变更 | `device_ids`, `event_types` |
| 状态变更推送 | Webhook | 回调URL | 实时状态推送 | - |
| 状态历史查询 | GET | `/v1.0/devices/{device_id}/status/history` | 查询状态历史 | `device_id`, `start_time`, `end_time` |

#### **4.2 设备健康检查**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 设备健康状态 | GET | `/v1.0/devices/{device_id}/health` | 设备健康检查 | `device_id` |
| 网络质量检测 | GET | `/v1.0/devices/{device_id}/network` | 网络连接质量 | `device_id` |
| 固件版本检查 | GET | `/v1.0/devices/{device_id}/firmware` | 固件版本信息 | `device_id` |

### **五、云云对接接口**

#### **5.1 第三方平台对接**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 平台授权认证 | POST | `/v1.0/oauth/token` | OAuth2.0授权 | `client_id`, `client_secret`, `grant_type` |
| 用户设备同步 | GET | `/v1.0/users/{user_id}/devices` | 同步用户设备 | `user_id`, `access_token` |
| 数据导出接口 | GET | `/v1.0/data/export` | 批量数据导出 | `data_type`, `format`, `date_range` |

#### **5.2 Webhook事件回调**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| Webhook注册 | POST | `/v1.0/webhooks` | 注册回调地址 | `url`, `event_types`, `secret` |
| Webhook验证 | GET | 回调URL | 验证回调地址 | `challenge` |
| 事件回调接收 | POST | 回调URL | 接收事件通知 | - |

#### **5.3 数据同步接口**
| 接口名称 | 请求方法 | 接口路径 | 功能描述 | 必选参数 |
|---------|---------|---------|---------|---------|
| 设备数据同步 | POST | `/v1.0/sync/devices` | 设备数据同步 | `sync_data` |
| 状态数据同步 | POST | `/v1.0/sync/status` | 状态数据同步 | `status_data` |
| 历史数据同步 | POST | `/v1.0/sync/history` | 历史数据同步 | `history_data` |

---

## 🔧 **智能电工设备功能点定义**

### **标准功能点（DP）体系**

#### **基础控制功能**
| DP ID | 功能点名称 | 标识符 | 数据类型 | 取值范围 | 单位 | 必选 |
|-------|-----------|--------|----------|----------|------|------|
| 1 | 开关控制 | `switch_1` | bool | true/false | - | 是 |
| 9 | 倒计时 | `countdown_1` | value | 0-86400 | s | 是 |
| 38 | 上电状态 | `relay_status` | enum | off/on/memory | - | 否 |

#### **电量统计功能**
| DP ID | 功能点名称 | 标识符 | 数据类型 | 取值范围 | 单位 | 必选 |
|-------|-----------|--------|----------|----------|------|------|
| 17 | 增加电量 | `add_ele` | value | 0-50000 | kWh | 是 |
| 18 | 当前电流 | `cur_current` | value | 0-30000 | mA | 是 |
| 19 | 当前功率 | `cur_power` | value | 0-80000 | W | 是 |
| 20 | 当前电压 | `cur_voltage` | value | 0-5000 | V | 是 |

#### **校准系数功能**
| DP ID | 功能点名称 | 标识符 | 数据类型 | 取值范围 | 单位 | 必选 |
|-------|-----------|--------|----------|----------|------|------|
| 22 | 电压校准 | `voltage_coe` | value | 0-1000000 | - | 是 |
| 23 | 电流校准 | `electric_coe` | value | 0-1000000 | - | 是 |
| 24 | 功率校准 | `power_coe` | value | 0-1000000 | - | 是 |
| 25 | 电量校准 | `electricity_coe` | value | 0-1000000 | - | 是 |

#### **故障告警功能**
| DP ID | 功能点名称 | 标识符 | 数据类型 | 故障值 | 必选 |
|-------|-----------|--------|----------|--------|------|
| 26 | 故障告警 | `fault` | fault | ov_cr, ov_vol, ov_pwr, ls_cr, ls_vol, ls_pow | 是 |

#### **高级定时功能**
| DP ID | 功能点名称 | 标识符 | 数据类型 | 说明 | 必选 |
|-------|-----------|--------|----------|------|------|
| 41 | 循环定时 | `cycle_time` | string | 最大10个定时 | 否 |
| 42 | 随机定时 | `random_time` | string | 最大16个定时 | 否 |

---

## 🚀 **云云对接关键接口**

### **对接流程**
1. **平台注册** → 获取Client ID/Secret
2. **OAuth授权** → 获取Access Token
3. **设备同步** → 拉取用户设备列表
4. **状态订阅** → 建立实时连接
5. **指令控制** → 实现设备控制
6. **数据同步** → 双向数据流转

### **核心对接接口**

#### **1. 授权认证接口**
```http
POST /v1.0/oauth/token
Content-Type: application/json

{
  "grant_type": "authorization_code",
  "client_id": "your_client_id",
  "client_secret": "your_client_secret",
  "code": "authorization_code"
}
```

#### **2. 设备列表接口**
```http
GET /v1.0/users/{user_id}/devices
Authorization: Bearer {access_token}
```

#### **3. 指令下发接口**
```http
POST /v1.0/devices/{device_id}/commands
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "commands": [
    {
      "code": "switch_1",
      "value": true
    }
  ]
}
```

#### **4. Webhook注册接口**
```http
POST /v1.0/webhooks
Authorization: Bearer {access_token}
Content-Type: application/json

{
  "url": "https://your-server.com/webhook",
  "event_types": ["device_online", "device_offline", "status_report"],
  "secret": "your_webhook_secret"
}
```

---

## 📈 **API调用最佳实践**

### **1. 认证安全**
- 使用HTTPS协议
- Access Token定期刷新
- 敏感信息加密传输
- IP白名单限制

### **2. 性能优化**
- 批量接口减少请求次数
- 合理设置请求频率限制
- 使用长连接保持会话
- 异步处理耗时操作

### **3. 错误处理**
- 实现重试机制
- 记录完整错误日志
- 监控API调用成功率
- 设置告警阈值

### **4. 数据同步**
- 增量同步减少数据量
- 数据校验保证一致性
- 冲突解决策略
- 定期全量同步

---

## 🔍 **故障排查指南**

### **常见问题**
1. **设备离线**：检查网络连接、设备电源
2. **指令超时**：检查设备在线状态、网络延迟
3. **数据不一致**：检查数据同步机制、时间戳
4. **认证失败**：检查Token有效期、权限配置

### **调试工具**
- 涂鸦开发者平台调试工具
- API调用日志分析
- 设备日志抓取
- 网络抓包分析

---

## 📚 **参考资源**

### **官方文档**
- [涂鸦开发者平台](https://developer.tuya.com)
- [API接口文档](https://developer.tuya.com/cn/docs/cloud)
- [SDK下载](https://github.com/tuya)
- [技术论坛](https://www.tuya.com/community)

### **开发工具**
- Postman API测试集合
- 涂鸦IoT模拟器
- 设备调试工具
- 日志分析工具

---

## 📅 **版本历史**

| 版本 | 日期 | 更新内容 | 作者 |
|------|------|---------|------|
| v1.0 | 2026-03-25 | 初始版本，完整API体系梳理 | 群哥 |
| v1.1 | - | 待更新：接口示例代码补充 | -