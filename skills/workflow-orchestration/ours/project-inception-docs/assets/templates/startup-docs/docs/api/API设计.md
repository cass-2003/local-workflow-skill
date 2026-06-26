# API 设计

版本：v0.1
日期：<YYYY-MM-DD>

## 1. API 原则

- REST/GraphQL/RPC 风格：<选择>
- 鉴权方式：<方式>
- 幂等策略：<策略>
- 错误格式：统一。
- 异步任务：长任务统一返回 job/task ID。

## 2. 通用响应

成功：

```json
{
  "data": {},
  "meta": {}
}
```

失败：

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human readable message",
    "details": {}
  }
}
```

## 3. Projects

### 3.1 创建项目

`POST /api/projects`

请求：

```json
{
  "name": "<project name>"
}
```

响应：

```json
{
  "data": {
    "id": "<uuid>",
    "name": "<project name>",
    "status": "draft"
  }
}
```

### 3.2 项目列表

`GET /api/projects`

### 3.3 项目详情

`GET /api/projects/{projectId}`

### 3.4 更新项目

`PATCH /api/projects/{projectId}`

### 3.5 删除项目

`DELETE /api/projects/{projectId}`

## 4. Uploads

### 4.1 上传文件

`POST /api/uploads`

- 限制：
- 安全检查：
- 返回：

## 5. Domain Resources

### 5.1 <资源动作>

`POST /api/<resource>`

- 请求：
- 响应：
- 错误：

## 6. Jobs

### 6.1 创建异步任务

`POST /api/jobs`

### 6.2 获取任务列表

`GET /api/jobs`

### 6.3 获取任务详情

`GET /api/jobs/{jobId}`

## 7. Export

### 7.1 创建导出

`POST /api/exports`

### 7.2 获取导出

`GET /api/exports/{exportId}`

## 8. 状态轮询

- 推荐间隔：
- 超时策略：
- 前端停止条件：
