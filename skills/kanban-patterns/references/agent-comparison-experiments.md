# Agent对照实验经验（2026-06-26）

## 核心问题：共享目录踩踏
同时给多个agent派相同文件的修改任务时，它们会同时修改同一文件导致冲突。

## 解决方案
1. 为每个agent创建独立副本目录
2. 用`--workspace "dir:/path/to/agent_dir"`分别指定
3. 任务完成后对比各目录结果

## 实际案例：小说P0修复对照实验
- 闪莉(LongCat)：修改4/5项通过
- 闪莉agnes(Agnes 2.0)：修改5/5项全通过（最靠谱）
- nvlinshi(DeepSeek V4 Flash)：protocol_violation崩溃，基本没改

## 结论
修改任务优先用agnes(5/5)，闪莉(4/5)次之，nvlinshi(1/5)不适合文件修改。
