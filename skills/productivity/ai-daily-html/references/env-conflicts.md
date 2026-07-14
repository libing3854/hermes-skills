# 环境依赖冲突备忘

## Lama Cleaner + diffusers 版本冲突

**现象**：安装 lama-cleaner 1.2.5 后，如果升级 diffusers 或 transformers（如为了使用新版 Stable Diffusion inpainting），会导致 lama-cleaner 无法导入。

**根因**：
- lama-cleaner 1.2.5 锁定 `diffusers==0.16.1` 和 `transformers==4.27.4`
- 新版 diffusers（0.30+）需要 transformers 4.40+
- huggingface_hub 0.25+ 移除了 `cached_download` API

**解决方案**：
- 如果只需要 Lama Cleaner：不升级 diffusers/transformers
- 如果只需要新版 diffusers：不安装 lama-cleaner，用 diffusers 的 `StableDiffusionInpaintPipeline` 直接做 inpainting
- 两者都需要：用两个不同的 Python 虚拟环境隔离

## HuggingFace Hub 认证

**现象**：下载 HuggingFace 模型时报 401 Unauthorized，即使是公开模型。

**根因**：huggingface_hub 新版本对某些公开模型也需要认证。

**解决方案**：注册 HuggingFace 账号（免费），生成 Access Token，设置 `HF_TOKEN` 环境变量。
