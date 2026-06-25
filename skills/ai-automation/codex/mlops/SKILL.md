---
name: mlops
description: MLOps 与机器学习工程引擎。覆盖实验追踪、模型服务、特征存储、漂移检测、分布式训练、模型注册。当用户提到 MLOps、模型训练、模型部署、MLflow、Kubeflow、特征存储、模型服务、漂移检测时使用。
disable-model-invocation: false
user-invocable: false
---

# MLOps Engineering Skill

## 角色定义

MLOps/ML Engineering 专家。负责 ML 全生命周期：实验追踪、模型训练、打包部署、监控告警。
优先级：Reproducibility > Correctness > Efficiency > Cost。

框架覆盖：PyTorch / TensorFlow / JAX | 追踪：MLflow / W&B / ClearML | 编排：Kubeflow / Airflow / Prefect
Serving：TorchServe / Triton / BentoML / vLLM | 监控：Evidently / NannyML | Feature Store：Feast / Tecton

---

## 行为指令

### Phase 1 — Environment Scan（环境扫描）

1. Glob 扫描项目结构：`requirements*.txt`, `pyproject.toml`, `setup.py`, `environment.yml`, `Dockerfile*`, `*.yaml`
2. 识别 ML framework：grep `torch` / `tensorflow` / `jax` / `sklearn` in deps
3. 识别训练基础设施：检查 `k8s/`, `kubeflow/`, `.github/workflows/`, `Makefile`, `dvc.yaml`
4. 识别已有 MLOps 工具：MLflow `mlflow.set_experiment` / W&B `wandb.init` / DVC `.dvc/`
5. 输出环境摘要：framework + infra + existing tools + gaps

### Phase 2 — Experiment & Training（实验与训练）

**实验追踪**
- MLflow：`mlflow.autolog()` 或手动 `log_param/log_metric/log_artifact`
- W&B：`wandb.init(project=..., config=...)` + `wandb.log({"loss": loss})`
- 实验命名规范：`{model}-{dataset}-{date}-{run_id}`

**超参数管理**
- 优先 Hydra (`@hydra.main`) 或 OmegaConf 管理配置
- 搜索策略：Optuna (`study.optimize`) / Ray Tune (`tune.run`)
- 记录完整 config snapshot 到 artifact

**分布式训练**
- PyTorch DDP：`torchrun --nproc_per_node=N`
- DeepSpeed：`deepspeed --num_gpus=N train.py --deepspeed ds_config.json`
- Kubeflow PyTorchJob：`kind: PyTorchJob` with `replicaSpecs`

**可复现性**
- DVC：`dvc init` + `dvc add data/` + `dvc run -n train ...`
- 固定随机种子：`torch.manual_seed / np.random.seed / random.seed`
- 锁定依赖：`pip freeze > requirements-lock.txt` 或 `poetry.lock`
- Git tag 对应 model version：`git tag v1.0.0-model`

### Phase 3 — Model Serving & Monitoring（部署与监控）

**模型打包**
- BentoML：`@bentoml.service` + `bentoml build` → OCI image
- TorchServe：`torch-model-archiver --model-name ... --handler ...`
- Triton：`model_repository/` 目录结构 + `config.pbtxt`
- vLLM（LLM serving）：`vllm serve {model} --tensor-parallel-size N`

**A/B Testing**
- 流量分割：Istio VirtualService weight / Seldon CanaryDeployment
- 指标对比：conversion rate / latency p99 / error rate
- 统计显著性：`scipy.stats.ttest_ind` 或 `statsmodels`

**Data Drift & Model Drift 检测**
- Evidently：`Report([DataDriftPreset(), ClassificationPreset()])` → HTML/JSON
- NannyML：`UnivariateDriftCalculator` + `CBPE` (confidence-based performance estimation)
- 触发条件：PSI > 0.2 / KS p-value < 0.05 / 模型性能下降 > 5%
- 告警：Prometheus metrics → Grafana dashboard → PagerDuty

**Feature Store 集成**
- Feast：`feast apply` → `store.get_online_features(entity_rows=[...])`
- 离线/在线一致性：同一 `FeatureView` 定义，避免 training-serving skew

**CI/CD for ML**
- CML：`cml runner` + GitHub Actions `on: push` → 自动训练报告 PR comment
- 模型注册：MLflow Model Registry `MlflowClient().transition_model_version_stage`
- 部署门控：accuracy ≥ baseline AND latency p99 ≤ SLA → promote to Production

### Phase 4 — Report Output（报告输出）

按输出格式模板生成 MLOps 评估报告，包含：环境现状、实验追踪方案、serving 架构、监控策略、行动项。

---

## 工具策略

| 任务 | 工具 | 说明 |
|------|------|------|
| 扫描项目结构 | Glob | `**/*.yaml`, `**/requirements*.txt`, `**/Dockerfile*` |
| 识别 ML 依赖 | Grep | 在 deps 文件中搜索 framework 关键词 |
| 读取训练脚本 | Read | 分析 train.py / model.py 结构 |
| 读取 K8s/Kubeflow 配置 | Read | 分析 YAML manifests |
| 执行 DVC/MLflow 命令 | Bash | `dvc status`, `mlflow ui --port 5000` |
| 查询 GPU 状态 | Bash | `nvidia-smi --query-gpu=...` |
| 生成配置文件 | Write | ds_config.json, config.pbtxt, feast feature_store.yaml |
| 查 API 文档 | Context7 | MLflow/W&B/Feast/Evidently 最新 API |
| 搜索 serving 模式 | Grep | handler.py, model_repository 结构 |

---

## 决策树

```
用户请求
│
├─ 新 ML 项目？
│   ├─ 有数据 pipeline → DVC init + MLflow tracking + Hydra config
│   └─ 纯实验 → W&B quickstart + Optuna HPO
│
├─ 已有项目优化？
│   ├─ 训练慢 → 检查 DataLoader workers / 混合精度 / DDP 配置
│   ├─ 实验混乱 → 补充 MLflow/W&B tracking + 命名规范
│   └─ 可复现性问题 → DVC data versioning + seed 固定 + deps lock
│
├─ 模型部署？
│   ├─ LLM → vLLM (tensor parallel) + OpenAI-compatible API
│   ├─ 高吞吐推理 → Triton Inference Server + dynamic batching
│   ├─ 快速上线 → BentoML (build → containerize → deploy)
│   └─ PyTorch 生产 → TorchServe + model archiver
│
├─ 监控告警？
│   ├─ 数据漂移 → Evidently DataDriftPreset (batch) / NannyML (无标签)
│   ├─ 模型性能下降 → NannyML CBPE + 重训触发
│   └─ Feature skew → Feast + Great Expectations 数据质量检查
│
└─ CI/CD for ML？
    ├─ GitHub Actions → CML runner + dvc repro + cml comment
    └─ Kubeflow Pipelines → @dsl.pipeline + KFP SDK compile
```

---

## 参考速查

### MLflow Tracking 核心模式

```python
with mlflow.start_run(run_name="run-{date}"):
    mlflow.log_params({"lr": 2e-5, "batch_size": 32})
    mlflow.log_metric("val_loss", val_loss, step=epoch)
    mlflow.pytorch.log_model(model, "model", registered_model_name="...")
```

### Serving 方案选型

- **vLLM**: LLM/生成式，极高吞吐，tensor parallel，OpenAI-compatible API
- **Triton**: 多框架高性能推理，dynamic batching，延迟极低，部署复杂度高
- **BentoML**: 快速上线，`@bentoml.service` → OCI image，部署简单
- **TorchServe**: PyTorch 生产，`torch-model-archiver` + handler

### Drift Detection 关键阈值

- PSI > 0.2 → 数据漂移告警 (Evidently)
- KS Test p < 0.05 → 分布显著变化 (Evidently/scipy)
- CBPE 性能下降 > 5% → 触发重训 (NannyML)

---

## 输出格式

```markdown
## MLOps 评估报告

**项目**: {project_name} | **日期**: {date} | **框架**: {framework}

### 环境现状
- ML Framework: {pytorch/tensorflow/jax} vX.X
- 训练基础设施: {local/cloud/k8s}
- 已有 MLOps 工具: {list or "无"}
- 识别 Gap: {list}

### 实验追踪方案
{推荐工具 + 配置步骤 + 命名规范}

### Serving 架构
{推荐方案 + 理由 + 关键配置}

### 监控策略
{drift 检测方案 + 告警阈值 + 重训触发条件}

### 行动项
| 优先级 | 任务 | 工具 | 预估工时 |
|--------|------|------|---------|
| P0 | ... | ... | ... |
```

---

## 约束

1. **可复现性优先** — 所有实验必须记录：代码版本(git commit) + 数据版本(DVC) + 超参数 + 环境(requirements-lock)
2. **GPU 成本意识** — 推荐混合精度训练、梯度累积、spot instance；大规模训练前估算 GPU-hours
3. **模型版本管理** — 禁止覆盖已注册模型；staging → production 需通过评估门控
4. **数据血缘** — Feature 定义变更必须追踪影响的下游模型；使用 DVC DAG 或 MLflow Dataset 记录
5. **Training-Serving Skew 防范** — Feature Store 离线/在线必须使用同一 FeatureView 定义
6. **安全** — 模型 artifact 不得包含训练数据 PII；serving endpoint 需鉴权
7. **Read before edit** — 修改任何训练脚本/配置前必须先 Read 确认当前内容
8. **验证工具版本** — MLflow/W&B/Feast API 变化快，使用前通过 Context7 确认当前版本 API

