├── src/aifudi/
│   ├── __init__.py
│   ├── agents/
│   │   └── openclaw.py          # OpenClaw 中间件
│   ├── core/
│   │   ├── audio/
│   │   │   ├── kws_pipeline.py   # KWS 训练管线
│   │   │   └── preprocessor.py    # 音频前端处理
│   │   └── llm/
│   │       └── router.py         # LLM 路由
│   └── gateway/
│       └── super_gateway.py       # Super Gateway
├── docs/
│   ├── PRD_v1.0.md              # 产品需求文档
│   ├── ARCHITECTURE_v1.0.md     # 架构设计文档
│   └── OPENCLAW_BOX_v1.0.md    # RK3588 硬件设计
├── examples/
│   └── demo.py                   # 演示脚本
├── requirements.txt
└── README.md
