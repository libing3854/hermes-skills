# 含标题+作者的封面提示词模板

Agnes AI (agnes-image-2.0-flash) 支持在提示词中嵌入中文标题和作者名。
以下模板已验证可用（2026-07）。

## 标题文字写法

```
large 3D metallic bronze-gold Chinese title text "书名" at the top with cracked weathered texture and warm fiery highlights
```

## 作者名写法

```
author name "作者名" in elegant silver text at the bottom
```

## 暗黑奇幻类（含文字版）

### 风格1：魔法阵
```
Dark fantasy novel book cover, large 3D metallic bronze-gold Chinese title text "书名" at the top with cracked weathered texture and warm fiery highlights, a mysterious figure in a long dark robe standing before a glowing ornate circular magical formation, dark background with warm golden and orange glowing magical runes and symbols, mystical atmosphere, epic fantasy art style, detailed digital painting, cinematic lighting, dark purple and black color scheme with golden accents, author name "作者名" in elegant silver text at the bottom, 2:3 aspect ratio
```

### 风格2：事务所
```
Dark urban fantasy novel book cover, large 3D metallic bronze-gold Chinese title text "书名" at the top with weathered cracked texture, a mysterious antique office desk with glowing documents and ethereal contracts floating in the air, dark abyssal portal behind the desk, candles and mysterious artifacts on shelves, atmospheric fog, dark moody lighting with blue and purple magical glow, supernatural detective office aesthetic, detailed illustration, cinematic composition, author name "作者名" in elegant silver text at the bottom, 2:3 aspect ratio
```

### 风格3：人物立绘
```
Dark fantasy character portrait book cover, large 3D metallic bronze-gold Chinese title text "书名" at the top with cracked weathered texture, a young man with sharp features and mysterious eyes wearing a dark formal suit with subtle magical sigils, one hand extended with swirling dark energy and golden sparks, dark abyssal background with floating runic symbols, dramatic side lighting, anime-influenced realistic style, detailed face and expression, mysterious and confident aura, author name "作者名" in elegant silver text at the bottom, 2:3 aspect ratio
```

### 风格4：恐怖悬疑
```
Horror supernatural novel book cover, large 3D metallic bronze-gold Chinese title text "书名" at the top with cracked weathered texture, a shadowy figure emerging from a dark doorway of an ancient building, eerie green and purple glowing eyes in the darkness, twisted reality effect with impossible architecture, dripping walls and mysterious symbols, terrifying atmosphere, dark color palette with sickly green and deep purple accents, psychological horror style, detailed dark illustration, author name "作者名" in elegant silver text at the bottom, 2:3 aspect ratio
```

### 风格5：都市奇幻
```
Urban dark fantasy novel book cover, large 3D metallic bronze-gold Chinese title text "书名" at the top with weathered cracked texture, modern city skyline at night with a massive dark portal opening in the sky, a silhouette of a man in suit standing on a rooftop looking up at the portal, lightning and magical energy crackling around the portal, cyberpunk-inspired neon accents in blue and pink, dramatic perspective, cinematic movie poster style, dark atmospheric mood, author name "作者名" in elegant silver text at the bottom, 2:3 aspect ratio
```

### 风格6：极简设计
```
Minimalist dark fantasy book cover design, large elegant golden Chinese title text "书名" centered at the top, solid deep black background, a single ornate golden key floating in the center with subtle magical glow, thin golden geometric lines forming a subtle portal pattern around the key, elegant and mysterious aesthetic, luxury book design, clean composition, high contrast gold on black, author name "作者名" in small elegant gold text at the bottom, 2:3 aspect ratio
```

### 风格7：中国风暗黑
```
Chinese dark fantasy novel book cover, large 3D metallic red and gold Chinese title text "书名" at the top with traditional calligraphy style, a mysterious figure in traditional Chinese robes standing before an ancient temple gate, dark ink wash painting style with glowing red and gold magical seals, traditional Chinese architectural elements shrouded in dark mist, yin-yang symbol and bagua patterns glowing in the background, Eastern mysticism aesthetic, dark atmospheric mood with red and gold accents, detailed illustration, author name "作者名" in elegant gold text at the bottom, 2:3 aspect ratio
```

### 风格8：蒸汽朋克+克苏鲁
```
Steampunk Lovecraftian horror novel book cover, large 3D metallic bronze-gold Chinese title text "书名" at the top with weathered cracked metallic texture and warm fiery highlights, a mysterious man in tattered dark brown trench coat and top hat walking toward viewer on wet cobblestone street, holding ornate cane, Victorian steampunk buildings with brass gears and gas street lamps on both sides, all-seeing eye symbol on building facade, dark industrial smokestacks in hazy background, warm orange-gold lighting contrasted with deep shadows, painterly gritty texture, atmospheric noir mood, author name "作者名" in silver-white text at the bottom within decorative frame, 2:3 aspect ratio
```

## 借鉴番茄古风世情类（含文字版）

### 风格9：暗黑山水（借鉴番茄古风构图）
```
Dark fantasy novel book cover inspired by Chinese landscape painting composition, large 3D metallic bronze-gold Chinese title text "书名" at the top with cracked weathered texture, a mysterious figure in dark robes standing on ancient stone ruins in the foreground, middle ground with dark misty rivers and flying shadowy creatures, background with layered dark mountains under blood-red sunset, warm golden and orange magical energy flowing through the landscape, atmospheric fog, cinematic lighting, dark purple and black color scheme with golden accents, author name "作者名" in elegant silver text at the bottom, 2:3 aspect ratio
```

**借鉴点**：
- 前景人物+中远景山水的分层构图
- 暖色调与冷色调的平衡
- 古典意境与暗黑元素的结合

### 风格10：意象氛围（借鉴番茄意象风格）
```
Dark fantasy novel book cover with symbolic imagery, large elegant golden Chinese title text "书名" centered at the top, solid deep black background, floating magical artifacts in the air: an ornate golden key, glowing purple crystal, ancient scroll with mysterious symbols, subtle dark magical energy swirling around the objects, minimalist composition with ample negative space, elegant and mysterious aesthetic, luxury book design, high contrast gold on black, author name "作者名" in small elegant gold text at the bottom, 2:3 aspect ratio
```

**借鉴点**：
- 用意象符号替代具象人物
- 留白构图，营造想象空间
- 极简设计，突出核心元素

### 风格11：局部特写（借鉴番茄局部构图）
```
Dark fantasy novel book cover with close-up detail, large 3D metallic bronze-gold Chinese title text "书名" at the top with cracked weathered texture, a mysterious hand with pale fingers reaching out from darkness, wearing an ornate dark ring with glowing purple gemstone, dark magical energy swirling around the fingers, background with blurred ancient symbols and mysterious lights, dramatic side lighting, detailed texture on hand and ring, atmospheric dark mood, author name "作者名" in elegant silver text at the bottom, 2:3 aspect ratio
```

**借鉴点**：
- 局部特写营造氛围感
- 手部+魔法物品的细节刻画
- 暗黑背景与亮色点缀的对比

## 使用方法

1. 替换 `书名` 和 `作者名` 为实际值
2. 直接传给 `image_generate(prompt=..., aspect_ratio="portrait")`
3. 生成后检查文字渲染是否准确（可能有少量错字）
