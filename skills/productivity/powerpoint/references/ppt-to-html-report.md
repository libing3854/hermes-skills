# PPT to HTML Report Workflow

## Pattern
Extract content + images from PPT → Generate comprehensive HTML report → Multi-agent review cycle

## Step 1: Extract PPT Content

```python
from pptx import Presentation

pptx_path = "/path/to/file.pptx"
prs = Presentation(pptx_path)

for i, slide in enumerate(prs.slides):
    print(f"\n=== Slide {i+1} ===")
    for shape in slide.shapes:
        if hasattr(shape, "text") and shape.text.strip():
            print(shape.text)
```

## Step 2: Extract PPT Images

```python
from pptx.enum.shapes import MSO_SHAPE_TYPE
import os

output_dir = "/path/to/images"
os.makedirs(output_dir, exist_ok=True)

for slide_idx in target_slides:
    slide = prs.slides[slide_idx - 1]
    for shape in slide.shapes:
        if shape.shape_type == MSO_SHAPE_TYPE.PICTURE:
            image = shape.image
            ext = image.ext
            filename = f"slide_{slide_idx:03d}_{img_count:02d}.{ext}"
            with open(os.path.join(output_dir, filename), 'wb') as f:
                f.write(image.blob)
```

**Note**: Script execution may require user approval in terminal. If blocked, ask user to approve.

## Step 3: Generate HTML Report

- Use dark theme with gradient headers
- Embed images using relative paths: `<img src="images/filename.png">`
- Include TOC with anchor links
- Use tag system for priority: `tag-req` (required), `tag-rec` (recommended), `tag-info` (info)
- Add slide references: `<div class="slide-ref">参考PPT幻灯片 XX</div>`

## Step 4: Multi-Agent Review Cycle

1. **大莉M review** → identifies gaps, errors, inconsistencies
2. **Fix issues** identified in review
3. **大莉M re-verify** → confirms fixes, checks for new issues
4. Repeat until clean

### Review dimensions:
- Content consistency (vs source document)
- Completeness (no omissions)
- Accuracy (numbers, terminology)
- Image correspondence (images match text)
- HTML structure (valid markup)

## Self-Contained HTML with Base64 Images

For portable HTML files that work without external dependencies, embed images as base64:

```python
import base64, os

img_dir = "/path/to/extracted_images"
html_path = "/path/to/report.html"

with open(html_path, 'r') as f:
    html = f.read()

for filename in os.listdir(img_dir):
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        with open(os.path.join(img_dir, filename), 'rb') as img_file:
            img_data = base64.b64encode(img_file.read()).decode('utf-8')
        ext = filename.split('.')[-1].lower()
        mime = 'image/png' if ext == 'png' else 'image/jpeg'
        html = html.replace(f'images/{filename}', f'data:{mime};base64,{img_data}')

with open(html_path, 'w') as f:
    f.write(html)
```

**Trade-offs:**
- ✅ Single file, no external dependencies — works anywhere
- ✅ No need to ship image folder alongside HTML
- ❌ File size increases significantly (105 images → 31MB)
- ❌ Cannot update images without regenerating the entire HTML

**When to use base64:** User wants a single portable file, or images are few/small.
**When to use relative paths:** Large image sets (>50MB), or images will be updated independently.

## Pitfalls
- PPT may have internal contradictions (different slides state different values) → note and choose the most recent/authoritative
- Image extraction requires user approval for script execution — terminal will prompt "Command required approval"
- Large PPTs (100+ slides) may have 100+ images → show key images in HTML, keep rest in folder
- HTML `</ul>` tags can accumulate during patching → clean up after edits
- Base64 embedding large images (>500KB each) will significantly inflate HTML file size
- Python script execution via heredoc (`python3 << 'EOF'`) requires terminal approval — if user denies, the script is blocked
