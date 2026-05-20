# JSON Schemas

本文档定义了 Hermes Skill Creator 使用的 JSON schema。

---

## evals.json

定义技能的评估用例。位于技能目录下的 `evals/evals.json`。

```json
{
  "skill_name": "example-skill",
  "evals": [
    {
      "id": 1,
      "name": "basic-csv-to-table",
      "prompt": "用户的实际任务描述",
      "expected_output": "期望结果的描述",
      "files": ["evals/files/sample1.csv"],
      "expectations": [
        "输出包含表格标题行",
        "输出来自脚本 parse_csv.py"
      ]
    }
  ]
}
```

**字段说明：**
- `skill_name`: 匹配技能前端中的 name
- `evals[].id`: 唯一整数标识
- `evals[].name`: 人类可读的名称（用作 viewer 中的节标题）
- `evals[].prompt`: 要执行的任务
- `evals[].expected_output`: 成功标准的人工描述
- `evals[].files`: 可选，输入文件路径列表（相对技能根目录）
- `evals[].expectations`: 可验证的陈述列表

---

## eval_metadata.json

评估运行的元数据。位于 `<workspace>/iteration-N/eval-<name>/eval_metadata.json`。

```json
{
  "eval_id": 1,
  "eval_name": "basic-csv-to-table",
  "prompt": "用户的任务 prompt",
  "assertions": [
    {
      "text": "输出文件是一个 HTML 文件",
      "description": "验证输出格式"
    },
    {
      "text": "表格包含 CSV 中的所有数据列",
      "description": "验证数据完整性"
    }
  ]
}
```

**字段说明：**
- `eval_id`: 匹配 evals.json 中的 id
- `eval_name`: 匹配 evals.json 中的 name
- `prompt`: 原始任务 prompt
- `assertions[]`: 可验证的断言
  - `text`: 断言内容
  - `description`: 断言描述

---

## grading.json

评分代理的输出。位于 `<workspace>/iteration-N/eval-<name>/<config>/run-<N>/grading.json`。

```json
{
  "expectations": [
    {
      "text": "输出包含名称 '张三'",
      "passed": true,
      "evidence": "在 transcript 第 3 步找到：'提取的名称：张三、李四'"
    },
    {
      "text": "电子表格有 SUM 公式在 B10 单元格",
      "passed": false,
      "evidence": "未创建电子表格。输出是一个文本文件。"
    }
  ],
  "summary": {
    "passed": 2,
    "failed": 1,
    "total": 3,
    "pass_rate": 0.67
  },
  "execution_metrics": {
    "tool_calls": {
      "Read": 5,
      "Write": 2,
      "Bash": 8
    },
    "total_tool_calls": 15,
    "total_steps": 6,
    "errors_encountered": 0,
    "output_chars": 12450,
    "transcript_chars": 3200
  },
  "timing": {
    "executor_duration_seconds": 165.0,
    "grader_duration_seconds": 26.0,
    "total_duration_seconds": 191.0
  },
  "claims": [
    {
      "claim": "表单有 12 个可填写字段",
      "type": "factual",
      "verified": true,
      "evidence": "在 field_info.json 中统计出 12 个字段"
    }
  ],
  "user_notes_summary": {
    "uncertainties": ["使用了 2023 年的数据，可能过期"],
    "needs_review": [],
    "workarounds": ["对不可填写的字段回退到文本叠加"]
  },
  "eval_feedback": {
    "suggestions": [],
    "overall": "评估看起来不错。"
  }
}
```

**关键要求：** `expectations` 数组必须使用字段名 `text`、`passed`、`evidence`（不要用 `name`/`met`/`details` 或其他变种）—— viewer 依赖这些精确字段名。

---

## timing.json

运行的耗时数据。位于 `<run-dir>/timing.json`。

```json
{
  "total_tokens": 84852,
  "duration_ms": 23332,
  "total_duration_seconds": 23.3,
  "executor_start": "2026-01-15T10:30:00Z",
  "executor_end": "2026-01-15T10:32:45Z"
}
```

---

## benchmark.json

聚合基准测试结果。位于 `<workspace>/iteration-N/benchmark.json`。

```json
{
  "metadata": {
    "skill_name": "example-skill",
    "skill_path": "/path/to/skill",
    "executor_model": "deepseek-v4-flash",
    "timestamp": "2026-01-15T10:30:00Z",
    "evals_run": [1, 2, 3],
    "runs_per_configuration": 3
  },
  "runs": [
    {
      "eval_id": 1,
      "eval_name": "basic-csv-to-table",
      "configuration": "with_skill",
      "run_number": 1,
      "result": {
        "pass_rate": 0.85,
        "passed": 6,
        "failed": 1,
        "total": 7,
        "time_seconds": 42.5,
        "tokens": 3800,
        "tool_calls": 18,
        "errors": 0
      },
      "expectations": [
        {"text": "...", "passed": true, "evidence": "..."}
      ],
      "notes": ["使用了 2023 年数据"]
    }
  ],
  "run_summary": {
    "with_skill": {
      "pass_rate": {"mean": 0.85, "stddev": 0.05, "min": 0.80, "max": 0.90},
      "time_seconds": {"mean": 45.0, "stddev": 12.0, "min": 32.0, "max": 58.0},
      "tokens": {"mean": 3800, "stddev": 400, "min": 3200, "max": 4100}
    },
    "without_skill": {
      "pass_rate": {"mean": 0.35, "stddev": 0.08, "min": 0.28, "max": 0.45},
      "time_seconds": {"mean": 32.0, "stddev": 8.0, "min": 24.0, "max": 42.0},
      "tokens": {"mean": 2100, "stddev": 300, "min": 1800, "max": 2500}
    },
    "delta": {
      "pass_rate": "+0.50",
      "time_seconds": "+13.0",
      "tokens": "+1700"
    }
  },
  "notes": [
    "断言 '输出是 HTML 文件' 在两种配置中均 100% 通过——可能不能区分技能价值",
    "Eval 3 显示高方差（50% ± 40%）——可能不稳定",
    "带技能比不带技能增加了 13 秒平均执行时间，但通过率提高了 50%"
  ]
}
```

---

## 文件关系图

```
workspace/iteration-N/
├── eval_metadata.json           # 元数据（从 evals.json 生成）
├── eval-basic-csv/
│   ├── eval_metadata.json       # 该 eval 的元数据
│   ├── with_skill/
│   │   ├── run-1/
│   │   │   ├── outputs/         # 输出文件（子代理生成）
│   │   │   ├── timing.json      # 耗时数据（从任务结果捕获）
│   │   │   └── grading.json     # 评分结果（评分代理生成）
│   │   └── run-2/
│   │       └── ...
│   └── without_skill/
│       └── run-1/
│           └── ...
├── benchmark.json               # 聚合结果（aggregate_benchmark.py 生成）
└── benchmark.md                 # 人类可读的报告
```
