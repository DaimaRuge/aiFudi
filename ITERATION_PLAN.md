# AI Fudi - 迭代计划

## v1.0 完成 (2026-02-04)

### ✅ 已完成

- [x] PRD v1.0 产品需求文档
- [x] ARCHITECTURE_v1.0 架构设计文档
- [x] OPENCLAW_BOX_v1.0 RK3588 硬件参考设计
- [x] OpenClaw 中间件框架 (Python)
- [x] Super Gateway 核心实现
- [x] LLM Router 智能路由
- [x] KWS Pipeline 合成数据训练
- [x] Audio Preprocessor (AEC/VAD/Beamforming)
- [x] GitHub 仓库: https://github.com/DaimaRuge/aiFudi

### 📊 统计

- Python 文件: 7 个
- 文档文件: 4 个
- 代码行数: ~3000
- 文档行数: ~5000

---

## POC 计划

### POC-1: 端侧 KWS 训练
**目标**: 搭建合成数据 KWS 训练脚本
- [ ] 完善 TTS 集成 (VITS/Edge-TTS)
- [ ] 实现 RIR 卷积
- [ ] 训练 CRNN 模型
- [ ] 导出 ONNX/TFLite

### POC-2: Super Gateway API
**目标**: 完整 API 网关
- [ ] 接入真实 LLM API (DeepSeek/Qwen)
- [ ] OpenAPI 解析器完善
- [ ] 记忆体实现 (Qdrant)
- [ ] WebSocket 流式支持

### POC-3: RK3588 硬件适配
**目标**: 端侧部署
- [ ] ALSA 音频驱动
- [ ] RKNN 模型转换
- [ ] NPU 推理优化
- [ ] 中断机制 (Barge-in)

---

## GitHub 仓库

- **aiFudi**: https://github.com/DaimaRuge/aiFudi

---

**最后更新**: 2026-02-04
