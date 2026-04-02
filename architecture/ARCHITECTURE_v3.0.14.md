# 天一阁架构文档 v3.0.14

**版本**: v3.0.14
**日期**: 2026-04-02
**主题**: 监控可观测性 + API 限流与成本控制 + 性能优化 + 高级搜索增强

---

## 📋 版本历史

| 版本 | 日期 | 说明 |
|------|------|------|
| v3.0.14 | 2026-04-02 | 监控架构 + 限流架构 + 性能优化 + 搜索增强 |
| v3.0.13 | 2026-03-30 | 移动端架构 + AI 写作架构 + 知识图谱架构 + 权限架构 + 备份架构 |
| v3.0.12 | 2026-03-29 | LibIndex One 同步架构 + 项目管理架构 + 协作架构 + 插件架构 |
| v3.0.11 | 2026-03-29 | 前端认证架构 + 向量搜索架构 + 批量操作架构 |

---

## 🏗️ 系统架构总览

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           前端层 (React + PWA)                           │
├─────────────────────────────────────────────────────────────────────────┤
│  Mobile UI   │  AI Writing   │  Knowledge Graph  │  Permissions  │ Backup │
│  - Responsive│  - Assistant  │  - Visualization  │  - Roles      │        │
│  - Touch     │  - Grammar    │  - Navigator      │  - Policies   │        │
│  - PWA       │  - Translate  │  - Explorer       │  - Audit      │        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                           API 层 (FastAPI)                               │
├─────────────────────────────────────────────────────────────────────────┤
│  /mobile     │  /ai-writing  │  /knowledge-graph │  /permissions │ /backup│
│  - Detect    │  - continue   │  - nodes/edges    │  - check      │ - jobs │
│  - Manifest  │  - polish     │  - search         │  - roles      │ - restore
├─────────────────────────────────────────────────────────────────────────┤
│  /monitoring │  /rate-limit  │  /search/advanced │  /analytics   │ /perf  │
│  - metrics   │  - quota      │  - facets         │  - events     │ - cache│
│  - health    │  - throttle   │  - suggestions    │  - dashboards │ - opt  │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                        服务层 (Services)                                  │
├─────────────────────────────────────────────────────────────────────────┤
│  MobileAdapter      │  AIWritingService      │  KnowledgeGraphService    │
│  - Breakpoint       │  - Continue            │  - GraphBuilder            │
│  - TouchHandler      │  - Polish              │  - LayoutEngine           │
│  - PWAConfig        │  - GrammarCheck        │  - Navigator              │
├─────────────────────────────────────────────────────────────────────────┤
│  PermissionService  │  BackupService         │  MonitoringService        │
│  - RBAC             │  - Full/Incremental    │  - MetricsCollector       │
│  - ABAC             │  - Compression         │  - AlertManager           │
│  - Audit            │  - Encryption          │  - HealthChecker          │
├─────────────────────────────────────────────────────────────────────────┤
│  RateLimitService   │  SearchService         │  PerformanceService       │
│  - QuotaManager     │  - FacetedSearch       │  - CacheManager           │
│  - Throttler        │  - SearchAnalytics    │  - QueryOptimizer        │
│  - CostTracker      │  - SuggestionEngine   │  - ConnectionPool        │
└─────────────────────────────────────────────────────────────────────────┘
                                   │
┌─────────────────────────────────────────────────────────────────────────┐
│                        数据层                                             │
├─────────────────────────────────────────────────────────────────────────┤
│  PostgreSQL  │  Redis         │  Object Storage      │  Vector DB       │
│  - roles     │  - permissions │  - backup archives   │  - graph cache   │
│  - policies  │  - cache       │  - attachments       │  - embeddings    │
│  - audit     │  - rate limit  │  - analytics data   │                  │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📊 一、监控与可观测性架构

### 1.1 整体可观测性架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Observability Architecture                             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐    │
│   │   Logs     │  │  Metrics    │  │   Traces    │  │   Events    │    │
│   │            │  │             │  │             │  │             │    │
│   │  Structured│  │  Prometheus │  │  OpenTelemetry│ │  Business  │    │
│   │  JSON Log  │  │  Counters   │  │  Spans      │  │  Events     │    │
│   └──────┬──────┘  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘    │
│          │                │                │                │            │
│          └────────────────┴────────────────┴────────────────┘            │
│                                   │                                       │
│                          ┌────────▼────────┐                            │
│                          │   Collector     │                            │
│                          │   (OTLP/Agent)  │                            │
│                          └────────┬────────┘                            │
│                                   │                                       │
│          ┌────────────────────────┼────────────────────────┐             │
│          │                        │                        │             │
│   ┌──────▼──────┐         ┌──────▼──────┐         ┌──────▼──────┐     │
│   │  Prometheus  │         │   Jaeger    │         │  Elasticsearch│    │
│   │  (Metrics)   │         │  (Traces)   │         │   (Logs)     │     │
│   └──────┬──────┘         └──────┬──────┘         └──────┬──────┘     │
│          │                        │                        │             │
│          └────────────────────────┴────────────────────────┘            │
│                                   │                                       │
│                          ┌────────▼────────┐                              │
│                          │   Grafana      │                              │
│                          │   Dashboards   │                              │
│                          └────────────────┘                              │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 1.2 Metrics 收集架构

```typescript
// services/monitoring/metrics.ts
import { Counter, Histogram, Gauge } from 'prom-client';

export const MetricsService {
  // 请求指标
  httpRequestsTotal: Counter = new Counter({
    name: 'http_requests_total',
    help: 'Total HTTP requests',
    labelNames: ['method', 'path', 'status'],
  });

  httpRequestDuration: Histogram = new Histogram({
    name: 'http_request_duration_seconds',
    help: 'HTTP request duration',
    labelNames: ['method', 'path'],
    buckets: [0.01, 0.05, 0.1, 0.5, 1, 2, 5],
  });

  // 业务指标
  documentsIndexed: Counter = new Counter({
    name: 'documents_indexed_total',
    help: 'Total documents indexed',
    labelNames: ['source', 'status'],
  });

  searchQueriesTotal: Counter = new Counter({
    name: 'search_queries_total',
    help: 'Total search queries',
    labelNames: ['type', 'results_count'],
  });

  // 资源指标
  vectorDbSize: Gauge = new Gauge({
    name: 'vector_db_size_bytes',
    help: 'Vector database size',
  });

  activeConnections: Gauge = new Gauge({
    name: 'active_connections',
    help: 'Number of active connections',
    labelNames: ['type'],
  });

  // AI 使用指标
  llmTokensUsed: Counter = new Counter({
    name: 'llm_tokens_used_total',
    help: 'Total LLM tokens used',
    labelNames: ['model', 'type'], // type: prompt/completion
  });

  llmLatency: Histogram = new Histogram({
    name: 'llm_latency_seconds',
    help: 'LLM request latency',
    labelNames: ['model'],
    buckets: [0.1, 0.5, 1, 2, 5, 10, 30],
  });

  llmCostUSD: Counter = new Counter({
    name: 'llm_cost_usd_total',
    help: 'Total LLM cost in USD',
    labelNames: ['model'],
  });
}
```

### 1.3 健康检查架构

```typescript
// services/monitoring/health.ts
interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  timestamp: string;
  version: string;
  uptime: number;
  checks: HealthCheck[];
}

interface HealthCheck {
  name: string;
  status: 'pass' | 'fail' | 'warn';
  latency?: number;
  message?: string;
  details?: Record<string, any>;
}

export class HealthCheckService {
  async checkHealth(): Promise<HealthStatus> {
    const checks = await Promise.all([
      this.checkDatabase(),
      this.checkVectorDb(),
      this.checkRedis(),
      this.checkObjectStorage(),
      this.checkExternalServices(),
    ]);

    const overallStatus = this.determineOverallStatus(checks);
    return {
      status: overallStatus,
      timestamp: new Date().toISOString(),
      version: process.env.APP_VERSION,
      uptime: process.uptime(),
      checks,
    };
  }

  private async checkDatabase(): Promise<HealthCheck> {
    const start = Date.now();
    try {
      await this.db.query('SELECT 1');
      return {
        name: 'postgresql',
        status: 'pass',
        latency: Date.now() - start,
      };
    } catch (e) {
      return {
        name: 'postgresql',
        status: 'fail',
        latency: Date.now() - start,
        message: e.message,
      };
    }
  }

  private async checkVectorDb(): Promise<HealthCheck> {
    const start = Date.now();
    try {
      await this.vectorDb.collection('health').fetch({ limit: 1 });
      return {
        name: 'qdrant',
        status: 'pass',
        latency: Date.now() - start,
      };
    } catch (e) {
      return {
        name: 'qdrant',
        status: 'fail',
        latency: Date.now() - start,
        message: e.message,
      };
    }
  }
}
```

### 1.4 告警架构

```typescript
// services/monitoring/alerts.ts
interface AlertRule {
  name: string;
  condition: AlertCondition;
  severity: 'critical' | 'warning' | 'info';
  cooldown: number; // seconds
  notification: NotificationConfig;
}

type AlertCondition = 
  | { type: 'threshold'; metric: string; operator: '>' | '<'; value: number }
  | { type: 'rate'; metric: string; window: number; threshold: number }
  | { type: 'absence'; metric: string; duration: number };

interface Alert {
  id: string;
  rule: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  firedAt: Date;
  value?: number;
  resolvedAt?: Date;
}

export class AlertManager {
  private alertRules: AlertRule[] = [
    {
      name: 'high_error_rate',
      condition: {
        type: 'threshold',
        metric: 'http_requests_total',
        operator: '>',
        value: 100, // per minute
      },
      severity: 'critical',
      cooldown: 300,
      notification: { type: 'email' },
    },
    {
      name: 'slow_response',
      condition: {
        type: 'threshold',
        metric: 'http_request_duration_p95',
        operator: '>',
        value: 2, // seconds
      },
      severity: 'warning',
      cooldown: 600,
      notification: { type: 'slack' },
    },
    {
      name: 'high_llm_cost',
      condition: {
        type: 'rate',
        metric: 'llm_cost_usd_total',
        window: 3600, // per hour
        threshold: 100, // USD
      },
      severity: 'warning',
      cooldown: 3600,
      notification: { type: 'email' },
    },
    {
      name: 'vector_db_down',
      condition: {
        type: 'absence',
        metric: 'vector_db_health',
        duration: 60, // seconds
      },
      severity: 'critical',
      cooldown: 60,
      notification: { type: 'sms' },
    },
  ];
}
```

---

## 🚦 二、API 限流与成本控制架构

### 2.1 限流架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Rate Limiting Architecture                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Client Request                                                         │
│         │                                                                │
│         ▼                                                                │
│   ┌─────────────┐                                                        │
│   │  IP/User    │                                                        │
│   │  Extractor  │                                                        │
│   └──────┬──────┘                                                        │
│          │                                                               │
│          ▼                                                               │
│   ┌─────────────┐     ┌─────────────┐     ┌─────────────┐               │
│   │   Redis     │────▶│  Lua Script │────▶│   Decision  │               │
│   │  Counter    │     │  (Atomic)   │     │             │               │
│   └─────────────┘     └─────────────┘     └──────┬──────┘               │
│                                                  │                       │
│                              ┌───────────────────┼───────────────────┐  │
│                              │                   │                   │  │
│                         Allow               Rate Limit           Block │
│                              │                   │                   │  │
│                              ▼                   ▼                   ▼  │
│                        ┌──────────┐        ┌──────────┐        ┌──────────┐
│                        │  Next    │        │  429    │        │  403    │
│                        │  Handler │        │  Retry  │        │  Ban    │
│                        └──────────┘        │  After  │        │  IP     │
│                                            └──────────┘        └──────────┘
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 2.2 限流策略实现

```python
# services/rate_limit/rate_limiter.py
from enum import Enum
from dataclasses import dataclass
from typing import Optional
import time
import hashlib


class RateLimitTier(str, Enum):
    FREE = "free"
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"


@dataclass
class RateLimitConfig:
    tier: RateLimitTier
    requests_per_minute: int
    requests_per_hour: int
    requests_per_day: int
    burst_size: int
    embedding_limit_per_day: int  # LLM calls
    search_limit_per_day: int


RATE_LIMITS = {
    RateLimitTier.FREE: RateLimitConfig(
        tier=RateLimitTier.FREE,
        requests_per_minute=10,
        requests_per_hour=100,
        requests_per_day=1000,
        burst_size=20,
        embedding_limit_per_day=100,
        search_limit_per_day=500,
    ),
    RateLimitTier.BASIC: RateLimitConfig(
        tier=RateLimitTier.BASIC,
        requests_per_minute=60,
        requests_per_hour=1000,
        requests_per_day=10000,
        burst_size=100,
        embedding_limit_per_day=1000,
        search_limit_per_day=5000,
    ),
    RateLimitTier.PRO: RateLimitConfig(
        tier=RateLimitTier.PRO,
        requests_per_minute=300,
        requests_per_hour=5000,
        requests_per_day=50000,
        burst_size=500,
        embedding_limit_per_day=10000,
        search_limit_per_day=50000,
    ),
    RateLimitTier.ENTERPRISE: RateLimitConfig(
        tier=RateLimitTier.ENTERPRISE,
        requests_per_minute=1000,
        requests_per_hour=20000,
        requests_per_day=200000,
        burst_size=2000,
        embedding_limit_per_day=-1,  # unlimited
        search_limit_per_day=-1,
    ),
}


class RateLimitService:
    """Redis-based distributed rate limiting using sliding window."""
    
    LUA_SCRIPT = """
    local key = KEYS[1]
    local now = tonumber(ARGV[1])
    local window = tonumber(ARGV[2])
    local limit = tonumber(ARGV[3])
    local burst = tonumber(ARGV[4])
    
    -- Remove old entries outside the window
    redis.call('ZREMRANGEBYSCORE', key, 0, now - window * 1000)
    
    -- Count current requests in window
    local count = redis.call('ZCARD', key)
    
    -- Check if within limit or burst
    if count < limit then
        redis.call('ZADD', key, now, now .. '-' .. math.random())
        redis.call('EXPIRE', key, window)
        return {1, limit - count - 1, 0}  -- allowed, remaining, retry_after
    elseif count < limit + burst then
        -- Burst allow with penalty
        redis.call('ZADD', key, now, now .. '-' .. math.random())
        redis.call('EXPIRE', key, window)
        return {2, 0, 0}  -- allowed (burst), remaining, retry_after
    else
        local oldest = redis.call('ZRANGE', key, 0, 0, 'WITHSCORES')
        local retry_after = 0
        if #oldest > 0 then
            retry_after = math.ceil((tonumber(oldest[2]) + window * 1000 - now) / 1000)
        end
        return {0, 0, retry_after}  -- denied, remaining, retry_after
    end
    """
    
    async def check_rate_limit(
        self,
        identifier: str,  # user_id or ip
        tier: RateLimitTier,
        endpoint: Optional[str] = None,
    ) -> RateLimitResult:
        config = RATE_LIMITS[tier]
        
        # Use different keys for different limit types
        minute_key = f"rl:minute:{identifier}"
        hour_key = f"rl:hour:{identifier}"
        day_key = f"rl:day:{identifier}"
        
        now = time.time()
        
        # Check all limits
        minute_result = await self.redis.eval(
            self.LUA_SCRIPT, 1, minute_key,
            int(now * 1000), 60, config.requests_per_minute, config.burst_size // 6
        )
        
        hour_result = await self.redis.eval(
            self.LUA_SCRIPT, 1, hour_key,
            int(now * 1000), 3600, config.requests_per_hour, config.burst_size
        )
        
        day_result = await self.redis.eval(
            self.LUA_SCRIPT, 1, day_key,
            int(now * 1000), 86400, config.requests_per_day, config.burst_size * 6
        )
        
        # Return most restrictive result
        if minute_result[0] == 0:
            return RateLimitResult(allowed=False, retry_after=minute_result[2])
        elif hour_result[0] == 0:
            return RateLimitResult(allowed=False, retry_after=hour_result[2])
        elif day_result[0] == 0:
            return RateLimitResult(allowed=False, retry_after=day_result[2])
        
        return RateLimitResult(
            allowed=True,
            remaining={
                'minute': minute_result[1],
                'hour': hour_result[1],
                'day': day_result[1],
            }
        )
```

### 2.3 AI 成本控制架构

```python
# services/cost_control/llm_cost_tracker.py
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from decimal import Decimal


@dataclass
class LLMUsageRecord:
    timestamp: datetime
    model: str
    prompt_tokens: int
    completion_tokens: int
    cost_usd: Decimal
    user_id: str
    endpoint: str


# Model pricing (per 1M tokens)
LLM_PRICING = {
    # OpenAI
    'gpt-4o': {'input': 5.0, 'output': 15.0},
    'gpt-4o-mini': {'input': 0.15, 'output': 0.60},
    'gpt-4-turbo': {'input': 10.0, 'output': 30.0},
    'gpt-3.5-turbo': {'input': 0.5, 'output': 1.5},
    
    # Anthropic
    'claude-3-5-sonnet': {'input': 3.0, 'output': 15.0},
    'claude-3-5-haiku': {'input': 0.8, 'output': 4.0},
    'claude-3-opus': {'input': 15.0, 'output': 75.0},
    
    # Local / Open Source
    'llama-3-8b': {'input': 0.0, 'output': 0.0},  # local
    'qwen-7b': {'input': 0.0, 'output': 0.0},    # local
}


class LLMCostTracker:
    """Track and control LLM usage costs."""
    
    def __init__(self, db: Database, redis: Redis):
        self.db = db
        self.redis = redis
        self.cache_ttl = 3600  # 1 hour
    
    def calculate_cost(
        self,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> Decimal:
        pricing = LLM_PRICING.get(model, {'input': 0, 'output': 0})
        
        input_cost = Decimal(prompt_tokens) / 1_000_000 * Decimal(pricing['input'])
        output_cost = Decimal(completion_tokens) / 1_000_000 * Decimal(pricing['output'])
        
        return input_cost + output_cost
    
    async def check_daily_limit(
        self,
        user_id: str,
        tier: RateLimitTier,
    ) -> bool:
        """Check if user has remaining LLM quota for today."""
        config = RATE_LIMITS[tier]
        
        if config.embedding_limit_per_day == -1:
            return True  # unlimited
        
        key = f"llm:daily:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
        current = await self.redis.get(key)
        
        if current is None:
            return True
        
        return int(current) < config.embedding_limit_per_day
    
    async def record_usage(
        self,
        user_id: str,
        model: str,
        prompt_tokens: int,
        completion_tokens: int,
    ):
        """Record LLM usage and update counters."""
        cost = self.calculate_cost(model, prompt_tokens, completion_tokens)
        
        record = LLMUsageRecord(
            timestamp=datetime.utcnow(),
            model=model,
            prompt_tokens=prompt_tokens,
            completion_tokens=completion_tokens,
            cost_usd=cost,
            user_id=user_id,
            endpoint='unknown',
        )
        
        # Store in database
        await self.db.llm_usage.insert(record)
        
        # Update Redis counters
        today = datetime.utcnow().strftime('%Y-%m-%d')
        daily_key = f"llm:daily:{user_id}:{today}"
        
        pipe = self.redis.pipeline()
        pipe.incrbyfloat(daily_key, float(cost))
        pipe.expire(daily_key, 86400 * 2)  # 2 days TTL
        await pipe.execute()
        
        # Track by model
        model_key = f"llm:model:{model}:{today}"
        pipe = self.redis.pipeline()
        pipe.incrby(model_key, prompt_tokens + completion_tokens)
        pipe.expire(model_key, 86400 * 2)
        await pipe.execute()
        
        return cost
    
    async def get_cost_breakdown(
        self,
        user_id: str,
        start_date: datetime,
        end_date: datetime,
    ) -> dict:
        """Get cost breakdown by model and date."""
        records = await self.db.llm_usage.find({
            'user_id': user_id,
            'timestamp': {'$gte': start_date, '$lte': end_date},
        })
        
        breakdown = defaultdict(lambda: {'cost': Decimal(0), 'tokens': 0})
        
        for record in records:
            key = record.model
            breakdown[key]['cost'] += record.cost_usd
            breakdown[key]['tokens'] += record.prompt_tokens + record.completion_tokens
        
        return dict(breakdown)
```

---

## ⚡ 三、性能优化架构

### 3.1 多级缓存架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                      Multi-Level Caching Architecture                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Request                                                               │
│     │                                                                   │
│     ▼                                                                   │
│   ┌──────────────┐                                                      │
│   │ L1: Memory   │ ◀── Hot data (LRU, 100MB)                           │
│   │ Cache        │     Latency: ~0.1ms                                 │
│   └──────┬───────┘                                                      │
│          │ Cache Hit                                                    │
│          ▼ Cache Miss                                                   │
│   ┌──────────────┐                                                      │
│   │ L2: Redis    │ ◀── Warm data (TTL: 1-24h)                         │
│   │ Distributed  │     Latency: ~1ms                                   │
│   └──────┬───────┘                                                      │
│          │ Cache Hit                                                    │
│          ▼ Cache Miss                                                   │
│   ┌──────────────┐                                                      │
│   │ L3: Database │ ◀── Cold data                                      │
│   │ PostgreSQL   │     Latency: ~10ms                                  │
│   └──────────────┘                                                      │
│                                                                          │
│   Cache Strategy:                                                        │
│   ┌────────────────────────────────────────────────────────────────┐   │
│   │ Pattern                  │ Strategy    │ TTL        │ Invalidate│   │
│   ├────────────────────────────────────────────────────────────────┤   │
│   │ User session             │ Write-Read  │ 24h        │ On change │   │
│   │ Document metadata        │ Read-Aside  │ 1h         │ On update │   │
│   │ Search results           │ Write-Aside │ 5min       │ On index  │   │
│   │ Vector embeddings (hot)  │ Write-Aside │ 7d         │ On reindex│   │
│   │ Category tree            │ Read-Aside  │ 24h        │ On change │   │
│   │ Access control policy    │ Write-Through│ 1h        │ On change │   │
│   └────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 3.2 缓存实现

```python
# services/cache/multi_level_cache.py
from typing import TypeVar, Generic, Optional, Callable, Any
from dataclasses import dataclass
import hashlib
import json
import pickle
from functools import wraps
import time


T = TypeVar('T')


@dataclass
class CacheStats:
    hits: int
    misses: int
    hit_rate: float
    latency_ms: float


class MemoryCache:
    """L1 in-memory LRU cache using Python dict + OrderedDict."""
    
    def __init__(self, max_size_mb: int = 100):
        self.max_size = max_size_mb * 1024 * 1024
        self.current_size = 0
        self.cache: dict = {}
        self.access_order: list = []  # LRU tracking
    
    def get(self, key: str) -> Optional[bytes]:
        if key in self.cache:
            # Move to end (most recently used)
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def set(self, key: str, value: bytes, ttl: int = 3600):
        # Check if key exists
        if key in self.cache:
            self.current_size -= len(self.cache[key])
        
        # Check size limit
        while self.current_size + len(value) > self.max_size and self.access_order:
            oldest_key = self.access_order.pop(0)
            self.current_size -= len(self.cache.pop(oldest_key))
        
        self.cache[key] = value
        self.current_size += len(value)
        
        if key not in self.access_order:
            self.access_order.append(key)


class MultiLevelCache:
    """Three-level cache: Memory → Redis → Database."""
    
    def __init__(
        self,
        memory_cache: MemoryCache,
        redis: Redis,
        db: Database,
    ):
        self.l1 = memory_cache
        self.l2 = redis
        self.l3 = db
        self.stats = {'hits': 0, 'misses': 0, 'latency': []}
    
    def _make_key(self, prefix: str, *args) -> str:
        """Generate cache key from prefix and arguments."""
        key_data = f"{prefix}:{':'.join(str(arg) for arg in args)}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    async def get_or_fetch(
        self,
        key: str,
        fetch_func: Callable[[], Any],
        ttl: int = 3600,
        cache_level: str = 'all',
    ) -> Any:
        """Get from cache or fetch, with automatic caching."""
        start_time = time.time()
        
        # Try L1
        if cache_level in ('all', 'l1'):
            cached = self.l1.get(key)
            if cached:
                self.stats['hits'] += 1
                return pickle.loads(cached)
        
        # Try L2
        if cache_level in ('all', 'l2'):
            cached = await self.l2.get(key)
            if cached:
                self.stats['hits'] += 1
                # Populate L1
                if cache_level == 'all':
                    self.l1.set(key, cached, ttl)
                return pickle.loads(cached)
        
        # Fetch from source (L3)
        self.stats['misses'] += 1
        value = await fetch_func()
        
        # Cache the result
        serialized = pickle.dumps(value)
        
        if cache_level in ('all', 'l1'):
            self.l1.set(key, serialized, ttl)
        
        if cache_level in ('all', 'l2'):
            await self.l2.setex(key, ttl, serialized)
        
        latency = (time.time() - start_time) * 1000
        self.stats['latency'].append(latency)
        
        return value
    
    def get_stats(self) -> CacheStats:
        total = self.stats['hits'] + self.stats['misses']
        avg_latency = sum(self.stats['latency']) / len(self.stats['latency']) if self.stats['latency'] else 0
        return CacheStats(
            hits=self.stats['hits'],
            misses=self.stats['misses'],
            hit_rate=self.stats['hits'] / total if total > 0 else 0,
            latency_ms=avg_latency,
        )


def cached(ttl: int = 3600, key_prefix: str = 'default'):
    """Decorator for caching function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            cache_key = hashlib.md5(cache_key.encode()).hexdigest()
            
            result = await self.cache.get_or_fetch(
                cache_key,
                lambda: func(self, *args, **kwargs),
                ttl=ttl,
            )
            return result
        return wrapper
    return decorator
```

### 3.3 数据库连接池优化

```python
# services/database/connection_pool.py
from contextlib import asynccontextmanager
from dataclasses import dataclass
import asyncio


@dataclass
class PoolConfig:
    min_size: int = 10
    max_size: int = 100
    max_overflow: int = 50
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True


class AsyncConnectionPool:
    """Optimized async connection pool with pre-warming and monitoring."""
    
    def __init__(self, dsn: str, config: PoolConfig):
        self.dsn = dsn
        self.config = config
        self._pool: Optional[Pool] = None
        self._semaphore = asyncio.Semaphore(config.max_size)
        self._metrics = {
            'acquired': 0,
            'released': 0,
            'waiters': 0,
            'timeouts': 0,
        }
    
    async def initialize(self):
        """Pre-warm the pool."""
        self._pool = await create_pool(
            self.dsn,
            min_size=self.config.min_size,
            max_size=self.config.max_size,
            command_timeout=self.config.pool_timeout,
        )
        
        # Pre-warm with minimum connections
        for _ in range(self.config.min_size):
            conn = await self._pool.acquire()
            await conn.execute('SELECT 1')
            self._pool.release(conn)
    
    @asynccontextmanager
    async def acquire(self, timeout: Optional[float] = None):
        """Acquire a connection with timeout and metrics."""
        try:
            self._metrics['acquired'] += 1
            self._metrics['waiters'] += 1
            
            async with asyncio.timeout(timeout or self.config.pool_timeout):
                conn = await self._pool.acquire()
                yield conn
        except asyncio.TimeoutError:
            self._metrics['timeouts'] += 1
            raise PoolTimeoutError(f"Could not acquire connection within {timeout}s")
        finally:
            self._metrics['released'] += 1
            self._metrics['waiters'] -= 1
            if 'conn' in locals():
                self._pool.release(conn)
    
    def get_metrics(self) -> dict:
        return {
            **self._metrics,
            'size': self._pool.maxsize if self._pool else 0,
            'frees': len(self._pool.frees) if self._pool else 0,
        }
```

---

## 🔍 四、高级搜索增强架构

### 4.1 分面搜索架构

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    Faceted Search Architecture                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   Search Query                                                          │
│   ┌──────────────┐                                                      │
│   │ Full-text    │                                                      │
│   │ + Vector     │                                                      │
│   │ + Filters    │                                                      │
│   └──────┬───────┘                                                      │
│          │                                                               │
│          ▼                                                               │
│   ┌──────────────┐     ┌──────────────┐     ┌──────────────┐            │
│   │ Query Parser │ ──▶ │   Router     │ ──▶ │  Executor    │            │
│   │              │     │              │     │              │            │
│   │ - keywords   │     │ - Vector DB  │     │ - Parallel   │            │
│   │ - filters    │     │ - Keyword    │     │ - Merge      │            │
│   │ - facets     │     │ - Hybrid     │     │ - Rank       │            │
│   └──────────────┘     └──────────────┘     └──────┬───────┘            │
│                                                    │                     │
│                                                    ▼                     │
│   ┌──────────────────────────────────────────────────────────────────┐   │
│   │                         Search Results                            │   │
│   ├──────────────────────────────────────────────────────────────────┤   │
│   │  Documents: [doc1, doc2, doc3, ...]                              │   │
│   │  Facets:                                                         │   │
│   │  ├── Category: { "技术": 45, "产品": 32, "运营": 28 }           │   │
│   │  ├── Tags: { "AI": 12, "SaaS": 8, "安全": 6 }                   │   │
│   │  ├── Date: { "Today": 5, "This Week": 23, "This Month": 67 }    │   │
│   │  └── Source: { "Web": 45, "Local": 60 }                         │   │
│   │  Suggestions: ["AI 产品", "安全 策略", ...]                     │   │
│   └──────────────────────────────────────────────────────────────────┘   │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

### 4.2 分面搜索实现

```python
# services/search/faceted_search.py
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum


class FacetType(str, Enum):
    TERMS = "terms"
    RANGE = "range"
    DATE_HISTOGRAM = "date_histogram"
    HISTOGRAM = "histogram"


@dataclass
class FacetDefinition:
    name: str
    field: str
    type: FacetType
    size: int = 10
    ranges: Optional[List[Dict[str, Any]]] = None  # For range type
    interval: Optional[str] = None  # For date_histogram: day, week, month


class FacetedSearchService:
    """Service for executing faceted searches."""
    
    FACETS = [
        FacetDefinition(
            name="category",
            field="category_path",
            type=FacetType.TERMS,
            size=20,
        ),
        FacetDefinition(
            name="tags",
            field="tags",
            type=FacetType.TERMS,
            size=30,
        ),
        FacetDefinition(
            name="date_range",
            field="created_at",
            type=FacetType.DATE_HISTOGRAM,
            interval="month",
        ),
        FacetDefinition(
            name="file_size",
            field="file_size",
            type=FacetType.RANGE,
            ranges=[
                {"key": "tiny", "to": 1024},
                {"key": "small", "from": 1024, "to": 1024 * 1024},
                {"key": "medium", "from": 1024 * 1024, "to": 10 * 1024 * 1024},
                {"key": "large", "from": 10 * 1024 * 1024},
            ],
        ),
        FacetDefinition(
            name="source",
            field="source_type",
            type=FacetType.TERMS,
            size=10,
        ),
    ]
    
    async def search(
        self,
        query: str,
        user_id: str,
        filters: Dict[str, Any],
        requested_facets: Optional[List[str]] = None,
        page: int = 1,
        page_size: int = 20,
    ) -> SearchResult:
        # Build query
        vector_query = None
        if query and len(query) > 2:
            vector_query = await self.embedding_service.encode(query)
        
        # Execute main search
        search_results = await self.vector_db.search(
            collection='documents',
            query_vector=vector_query,
            query_text=query,
            filters=self._build_filters(filters, user_id),
            limit=page_size,
            offset=(page - 1) * page_size,
        )
        
        # Execute facet aggregations in parallel
        facets = {}
        if requested_facets:
            facet_defs = [f for f in self.FACETS if f.name in requested_facets]
        else:
            facet_defs = self.FACETS
        
        facet_results = await asyncio.gather(*[
            self._execute_facet(facet, filters, user_id)
            for facet in facet_defs
        ])
        
        for facet_def, facet_result in zip(facet_defs, facet_results):
            facets[facet_def.name] = facet_result
        
        # Generate suggestions
        suggestions = await self._generate_suggestions(query)
        
        return SearchResult(
            documents=search_results['documents'],
            total=search_results['total'],
            facets=facets,
            suggestions=suggestions,
            page=page,
            page_size=page_size,
        )
    
    async def _execute_facet(
        self,
        facet: FacetDefinition,
        filters: Dict[str, Any],
        user_id: str,
    ) -> Dict[str, Any]:
        if facet.type == FacetType.TERMS:
            return await self.vector_db.aggs.terms(
                collection='documents',
                field=facet.field,
                size=facet.size,
                filter=self._build_filters(filters, user_id),
            )
        elif facet.type == FacetType.DATE_HISTOGRAM:
            return await self.vector_db.aggs.date_histogram(
                collection='documents',
                field=facet.field,
                interval=facet.interval,
                filter=self._build_filters(filters, user_id),
            )
        elif facet.type == FacetType.RANGE:
            return await self.vector_db.aggs.range(
                collection='documents',
                field=facet.field,
                ranges=facet.ranges,
                filter=self._build_filters(filters, user_id),
            )
```

### 4.3 搜索分析架构

```python
# services/search/search_analytics.py
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class SearchEvent:
    user_id: str
    query: str
    filters: dict
    result_count: int
    clicked_doc_id: Optional[str]
    session_id: str
    response_time_ms: int
    timestamp: datetime


class SearchAnalyticsService:
    """Track and analyze search behavior."""
    
    async def record_search(self, event: SearchEvent):
        """Record a search event."""
        await self.db.search_events.insert(event)
        
        # Update Redis counters for real-time analytics
        today = event.timestamp.strftime('%Y-%m-%d')
        
        pipe = self.redis.pipeline()
        
        # Count searches per day
        pipe.hincrby(f'analytics:searches:{today}', 'total', 1)
        pipe.hincrby(f'analytics:searches:{today}', f'result_{event.result_count}', 1)
        
        # Track popular queries (top K)
        pipe.zincrby(f'analytics:popular_queries', 1, event.query.lower())
        
        # Track response time
        pipe.zadd(f'analytics:response_times:{today}', {event.session_id: event.response_time_ms})
        
        await pipe.execute()
    
    async def get_popular_queries(
        self,
        days: int = 7,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """Get most popular queries over the past N days."""
        result = await self.redis.zrevrange(
            'analytics:popular_queries',
            0,
            limit - 1,
            withscores=True,
        )
        
        return [{'query': q, 'count': int(score)} for q, score in result]
    
    async def get_zero_result_queries(
        self,
        days: int = 7,
    ) -> List[str]:
        """Get queries that returned zero results."""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        zero_results = await self.redis.hgetall(f'analytics:searches:{today}:result_0')
        return list(zero_results.keys())
    
    async def get_average_latency(
        self,
        days: int = 7,
    ) -> float:
        """Calculate average search latency over N days."""
        all_times = []
        for i in range(days):
            date = (datetime.utcnow() - timedelta(days=i)).strftime('%Y-%m-%d')
            times = await self.redis.zrange(f'analytics:response_times:{date}', 0, -1)
            all_times.extend([float(t) for t in times])
        
        return sum(all_times) / len(all_times) if all_times else 0
```

---

## 📊 数据模型

### 监控表

```sql
-- 监控指标存储
CREATE TABLE monitoring_metrics (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    metric_name VARCHAR(100) NOT NULL,
    metric_labels JSONB NOT NULL DEFAULT '{}',
    metric_value DOUBLE PRECISION NOT NULL,
    recorded_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_metrics_name_recorded (metric_name, recorded_at DESC),
    INDEX idx_metrics_labels (metric_labels) USING GIN,
    INDEX idx_recorded_at (recorded_at DESC)
);

-- LLM 使用记录
CREATE TABLE llm_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    model VARCHAR(50) NOT NULL,
    prompt_tokens INTEGER NOT NULL,
    completion_tokens INTEGER NOT NULL,
    cost_usd DECIMAL(10, 6) NOT NULL,
    endpoint VARCHAR(100),
    request_id VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_llm_user_created (user_id, created_at DESC),
    INDEX idx_llm_model_created (model, created_at DESC)
);

-- 搜索事件
CREATE TABLE search_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES users(id),
    session_id VARCHAR(100) NOT NULL,
    query VARCHAR(500) NOT NULL,
    filters JSONB NOT NULL DEFAULT '{}',
    result_count INTEGER NOT NULL,
    response_time_ms INTEGER NOT NULL,
    clicked_doc_id UUID REFERENCES documents(id),
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_search_user_session (user_id, session_id),
    INDEX idx_search_created (created_at DESC),
    INDEX idx_search_query (query varchar_pattern_ops)
);

-- 限流记录
CREATE TABLE rate_limit_violations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    ip_address INET,
    tier VARCHAR(20) NOT NULL,
    limit_type VARCHAR(20) NOT NULL,  -- 'minute', 'hour', 'day'
    attempted_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    
    INDEX idx_ratelimit_user (user_id),
    INDEX idx_ratelimit_ip (ip_address),
    INDEX idx_ratelimit_at (attempted_at DESC)
);
```

---

## 🔧 API 设计

### 监控 API

```yaml
# GET /api/v1/monitoring/metrics
/api/v1/monitoring/metrics:
  get:
    tags:
      - Monitoring
    summary: Get system metrics
    parameters:
      - name: metric
        in: query
        schema:
          type: string
      - name: start_time
        in: query
        schema:
          type: string
          format: date-time
      - name: end_time
        in: query
        schema:
          type: string
          format: date-time
    responses:
      '200':
        description: Metrics data
        content:
          application/json:
            schema:
              type: object

# GET /api/v1/monitoring/health
/api/v1/monitoring/health:
  get:
    tags:
      - Monitoring
    summary: Get health status
    responses:
      '200':
        description: Health check result
```

### 限流 API

```yaml
# GET /api/v1/rate-limit/status
/api/v1/rate-limit/status:
  get:
    tags:
      - Rate Limiting
    summary: Get current rate limit status
    security:
      - BearerAuth: []
    responses:
      '200':
        description: Rate limit status
        content:
          application/json:
            schema:
              type: object
              properties:
                tier:
                  type: string
                limits:
                  type: object
                remaining:
                  type: object
                reset_at:
                  type: string
                  format: date-time
```

### 搜索分析 API

```yaml
# GET /api/v1/analytics/search
/api/v1/analytics/search:
  get:
    tags:
      - Analytics
    summary: Get search analytics
    parameters:
      - name: period
        in: query
        schema:
          type: string
          enum: [day, week, month]
    responses:
      '200':
        description: Search analytics data

# GET /api/v1/analytics/popular-queries
/api/v1/analytics/popular-queries:
  get:
    tags:
      - Analytics
    summary: Get popular search queries
    parameters:
      - name: limit
        in: query
        schema:
          type: integer
          default: 20
    responses:
      '200':
        description: Popular queries
```

---

## 📈 性能考虑

### 性能指标目标

| 指标 | 目标值 | 告警阈值 |
|------|--------|----------|
| API P50 延迟 | < 50ms | > 200ms |
| API P95 延迟 | < 200ms | > 500ms |
| API P99 延迟 | < 500ms | > 1000ms |
| 搜索 P95 延迟 | < 500ms | > 1500ms |
| LLM P95 延迟 | < 5s | > 15s |
| 系统可用性 | > 99.9% | < 99.5% |
| 缓存命中率 | > 80% | < 60% |
| 错误率 | < 0.1% | > 1% |

### 扩展策略

1. **水平扩展**: API 服务无状态，支持任意扩展
2. **读写分离**: 读请求走 Redis 缓存，写请求走主库
3. **分片**: 向量数据库按用户 ID 分片
4. **CDN**: 静态资源、下载文件走 CDN

---

## 🔒 安全考虑

### 限流安全

1. **IP 限流**: 防止 DDoS 和暴力破解
2. **用户限流**: 基于用户配额
3. **API Key 限流**: 基于 API Key
4. **行为检测**: 异常行为触发临时封禁

### 成本控制

1. **LLM 预算**: 用户级别日/周/月预算
2. **Token 限制**: 单次请求 Token 上限
3. **模型路由**: 简单请求走小模型，复杂请求走大模型
4. **缓存复用**: 相同问题不重复调用 LLM

---

## 📊 版本总结

### v3.0.14 新增模块

| 模块 | 功能 | 复杂度 |
|------|------|--------|
| 监控服务 | Metrics + Tracing + Logging | 高 |
| 限流服务 | 多级限流 + 配额管理 | 高 |
| 成本控制 | LLM 使用追踪 + 预算控制 | 中 |
| 缓存服务 | 多级缓存 + 性能优化 | 高 |
| 分面搜索 | 高级搜索 + 聚合分析 | 中 |
| 搜索分析 | 用户行为追踪 + 分析 | 中 |

### 累计功能覆盖

| 版本 | 新增功能 | 状态 |
|------|----------|------|
| v3.0.14 | 监控 + 限流 + 成本 + 性能 + 搜索增强 | ✅ |
| v3.0.13 | 移动端 + AI 写作 + 知识图谱 + 权限 + 备份 | ✅ |
| v3.0.12 | LibIndex 同步 + 项目管理 + 协作 + 插件 | ✅ |
| v3.0.11 | 前端认证 + 向量搜索 + 批量操作 | ✅ |
| v3.0.10 | WebSocket + QA Agent + 断点续传 | ✅ |
| v3.0.9 | WebSocket 设计 + 知识库问答 + 断点续传设计 | ✅ |
| v3.0.8 | WebSocket 通信 + RAG Tool + 工作流编排 | ✅ |
| v3.0.7 | 异步任务队列架构 | ✅ |
| v3.0.6 | API 层重构 | ✅ |
| v3.0.5 | 服务层重构 | ✅ |
| v3.0.4 | 认证/权限/导入导出/备份 | ✅ |
| v3.0.3 | 文档管理 + 分类管理 | ✅ |
| v3.0.2 | AI 分类 + 标签系统 | ✅ |
| v3.0.1 | 核心架构设计 | ✅ |

---

**下次迭代预告 (v3.0.15)**: 
- 国际化与本地化 (i18n)
- A/B 测试框架
-更多高级特性...
