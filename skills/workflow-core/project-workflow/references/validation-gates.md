# Validation Gates

## Principle

完成声明必须有证据，而且证据范围要和改动范围匹配。

## Validation Levels

| 级别 | 适用场景 | 期望证据 |
|---|---|---|
| V0 | 纯分析 | 源码/文档检查与一致性说明 |
| V1 | 纯文档或纯 workflow 调整 | 路径校验、引用校验、结构一致性检查 |
| V2 | 单模块代码改动 | 局部 build/typecheck/test |
| V3 | 跨模块行为改动 | 多模块验证、接口或契约检查 |
| V4 | 交付面、高风险或运行时敏感改动 | 更强验证、回归或 smoke check |

## Selection Order

优先按这个顺序选择验证方式：

1. 项目本地 validation skill
2. 项目文档里规定的验证命令
3. 仓库原生脚本
4. 最小可行的全局通用验证

## Workflow And Skill Validation

如果本次工作主要在改 workflow / skill：

- 检查引用路径是否真实存在
- 检查 authority 层描述是否和真实结构一致
- 检查是否引入了重复真相源
- 检查主 `SKILL.md` 与 references 是否分工清晰

## Recording Rules

始终记录：

- 验证了什么
- 用了什么命令或证据
- 有什么没验证
- 为什么没做更宽的验证

如果没有验证，也要明确写出“未验证”。
