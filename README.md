# Dify 外部知识库 API - Railway 部署

将 API 部署到 Railway（免费），获得可靠的 HTTPS 端点供 Dify Cloud 使用。

## 部署步骤

### 方法 1: 通过 Railway CLI

1. **安装 Railway CLI**
   ```bash
   npm install -g @railway/cli
   ```

2. **登录 Railway**
   ```bash
   railway login
   ```

3. **初始化项目**
   ```bash
   cd /Users/kjonekong/EspoCRM-Dify/configs/external-kb-api-railway
   railway init
   ```

4. **部署**
   ```bash
   railway up
   ```

5. **设置环境变量**
   ```bash
   railway variables set PINECONE_API_KEY="pcsk_4yKQbF_CqsK8AiPcwH1TT4iYf9f8d8mFinR6Liay57iHS277QqJr7to2CXFeL6yVqUQLGJ"
   railway variables set PINECONE_HOST="https://dify-knowledge-rpws0mx.svc.aped-4627-b74a.pinecone.io"
   railway variables set PINECONE_INDEX_NAME="dify-knowledge"
   railway variables set QWEN_API_KEY="sk-45bb48bd7bf448cdb728f54037de8e09"
   railway variables set DIFY_API_KEY="dify_external_kb_secret_key_2026"
   ```

### 方法 2: 通过 Railway Web 控制台

1. 访问 https://railway.app/new
2. 选择 **Deploy from GitHub repo**
3. 或选择 **Deploy from CLI** 然后拖放此目录
4. 设置环境变量：
   - `PINECONE_API_KEY` = `pcsk_4yKQbF_CqsK8AiPcwH1TT4iYf9f8d8mFinR6Liay57iHS277QqJr7to2CXFeL6yVqUQLGJ`
   - `PINECONE_HOST` = `https://dify-knowledge-rpws0mx.svc.aped-4627-b74a.pinecone.io`
   - `PINECONE_INDEX_NAME` = `dify-knowledge`
   - `QWEN_API_KEY` = `sk-45bb48bd7bf448cdb728f54037de8e09`
   - `DIFY_API_KEY` = `dify_external_kb_secret_key_2026`

5. 点击 **Deploy**

## 获取部署 URL

部署完成后，Railway 会提供一个类似这样的 URL：
```
https://your-app-name.up.railway.app
```

## Dify Cloud 配置

| 配置项 | 值 |
|--------|-----|
| 名称 | Pinecone 知识库 |
| API 接口地址 | `https://your-app-name.up.railway.app` |
| API Key | `dify_external_kb_secret_key_2026` |

| 连接配置 | 值 |
|----------|-----|
| 外部知识库 ID | `dify-knowledge` |
| Top K | 3 |
| Score 阈值 | 0.5 |

## 测试

```bash
# 健康检查
curl https://your-app-name.up.railway.app/health

# 检索测试
curl -X POST https://your-app-name.up.railway.app/retrieval \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer dify_external_kb_secret_key_2026" \
  -d '{
    "knowledge_id": "dify-knowledge",
    "query": "测试问题",
    "retrieval_setting": {"top_k": 3, "score_threshold": 0.5}
  }'
```

## 成本

Railway 免费套餐：
- $5 免费额度/月
- 512MB RAM
- 1 vCPU
- 足够用于个人使用

## 故障排查

### 查看日志
```bash
railway logs
```

### 重启服务
```bash
railway restart
```
