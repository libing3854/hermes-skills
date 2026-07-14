# Cronjob Update Pitfalls

## ⚠️ model 字段无法通过 update 设为 null

**问题：** `cronjob(action='update', job_id='xxx', model=null)` 不会清除已有的 model 值。原任务 model 是 `deepseek-v4-flash`，更新后仍保留。

**影响：** 纯脚本任务（`no_agent=true`）的 model 字段实际上不会被使用，所以保留旧值不影响功能。

**如果需要彻底清除 model：** 只能通过删除重建任务实现。

## ✅ 多模型投递

`deliver` 字段支持逗号分隔：`telegram:611807381,qqbot`

QQ Bot home channel 从 `~/.hermes/.env` 的 `QQBOT_HOME_CHANNEL` 读取。

## ✅ 章节发布到番茄小说 — 错别字弹窗自动重试

**现象：** 首次发布时遇到"错别字检测弹窗"（`检测到你有错别字未修改，是否确定提交？`），脚本自动点"取消提交"后重试，第二次成功。

**原因：** 这是番茄后台的 AI 检测机制，首次填充内容后触发。脚本内置自动重试（第二次就能正常走通）。

**无需手动干预。**
