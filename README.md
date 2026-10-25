# AI 施工作业安全方案 Agent · 六阶段 Workflow

戚逸霖个人架构研究与流程示例仓库。简历中的项目定位为 Architecture Study。

本仓库于 2026-10-25 整理发布；`workflow.py` 是本次新增的可运行参考实现，不代表历史生产系统、实际工地部署或已经接入模型的完整产品。

## 业务流程

1. 作业识别与已评估风险录入。
2. 缺失信息追问与答复整理。
3. 人工审核的安全检查清单及依据。
4. 作业方案大纲。
5. 风险与对策矩阵。
6. WBS 任务与报告章节。

代码实现阶段顺序检查、必填字段验证、人工审核人登记、本地 JSON 状态保存和 Markdown 报告导出。它只编排人工提供的材料，不自动决定工程风险等级或生成可直接施工的安全指令。

## 运行

仅依赖 Python 3 标准库。

```bash
python -m unittest -v
python workflow.py init --description "仅用于流程演示的作业描述"
python workflow.py status
python workflow.py submit --input example-intake.json --reviewer "示例审核人"
python workflow.py status
```

首阶段输入示例：

```json
{
  "stage": "risk_intake",
  "data": {
    "work_description": "仅用于流程演示，不对应真实施工现场",
    "assessed_risk": "由具备资质的现场人员评估后填入"
  }
}
```

后续阶段字段见 `workflow.py` 的 `STAGES`。所有阶段审核完成后可执行：

```bash
python workflow.py export --output report.md
```

## 架构研究范围

目标应用架构包括 Next.js / TypeScript 交互层、结构化输出校验、OpenAI-compatible 模型适配、检索与引用、人工审核和产物导出。当前参考实现不包含这些完整产品能力；知识库检索、模型调用、DOCX/PDF 导出与认证权限属于后续实现范围。

模型生成内容即使后续接入，也应作为待审核草稿；真实施工方案必须由相应专业人员核验和审批。
