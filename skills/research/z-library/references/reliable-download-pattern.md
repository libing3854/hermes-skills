# Reliable Download Pattern (2026-07-01 verified)

## Problem

Z-Library (zh.z-library.sk) has severe redirect issues:
- URL-based search `/s/关键词` → redirects to unrelated search pages
- Direct navigation to `/book/ID/` → redirects to random book pages
- Snapshot-based clicking → elements disappear between snapshot and click

## Reliable Flow (tested and working)

### Step 1: Navigate to homepage
```
mcp_chrome_devtools_navigate_page → https://zh.z-library.sk/
```

### Step 2: Fill search form on homepage
Use the main-page search form (not the nav bar). Get its UID from a quick snapshot.

### Step 3: Click search, then extract results with JS
```js
// Wait for results, extract z-bookcard attributes
() => {
  const cards = document.querySelectorAll('z-bookcard');
  return Array.from(cards).map(c => ({
    href: c.getAttribute('href'),       // /book/ID/slug.html
    download: c.getAttribute('download'), // /dl/CODE
    title: c.querySelector('[slot="title"]')?.textContent?.trim(),
    extension: c.getAttribute('extension'),
  }));
}
```

### Step 4: Navigate to book page via JS (NOT navigate_page)
```js
() => {
  window.location.href = 'https://zh.z-library.sk/book/BOOK_ID/';
  return 'navigating';
}
```

### Step 5: Immediately trigger download via JS
```js
() => {
  const dlLink = document.querySelector('a[href*="/dl/"]');
  if (dlLink) {
    dlLink.click();
    return { href: dlLink.href, text: dlLink.innerText.trim() };
  }
  // If redirected, check document.title
  return { error: 'no dl link', title: document.title };
}
```

### Step 6: Wait and move file
```bash
sleep 20 && ls -lt ~/Downloads/ | head -3
mv "oldname.epub" "target_folder/"
ls -lh "target_folder/"
```

## Session Book Links (2026-07-01)

These specific books were found and confirmed on Z-Library. All IDs verified by extracting `href` from `z-bookcard` elements.

| Book | Z-Lib ID | Format | Size |
|------|----------|--------|------|
| 中国史话·社会风俗系列 (11本) | 0v1WDqQbRp | EPUB | 5.03 MB |
| 中国风俗通史丛书 宋代风俗 | JveNNkdpOE | - | - |
| 中国风俗通史丛书 隋唐五代风俗 | VOwBBel8v3 | - | - |
| 上古神话演义 (钟毓龙) | P0vpK4Agjr | - | - |
| **2026-07-01 session additions** | | | |
| 中国风俗史(外一种) (张亮采 & 尚秉和) | wRxbQ99Jv4 | EPUB | 37.83 MB |
| 中国民间信仰风俗辞典 (王景琳,徐刕) | Bj4m3xV8v3 | PDF | 32.12 MB |

## Format Preference

When both PDF and EPUB are available: prefer PDF. If only EPUB: download EPUB.
The download link text shows the format: "PDF, XX MB" or "EPUB, XX MB".
Check z-bookcard's `extension` attribute BEFORE navigating to the detail page to confirm available format.

## Known Z-Library Frontend Bugs

### Phantom navigation during snapshot
Taking `mcp_chrome_devtools_take_snapshot` on search results or book detail pages can trigger Z-Library's JavaScript to navigate to an unrelated search page. This is a Z-Library bug (likely a11y tree traversal side-effect), not a tool bug.
- **Workaround**: Use `evaluate_script` for all data extraction. Reserve `take_screenshot` for visual debugging only.
- **Observed**: 2026-07-01 — search results page spontaneously changed from "中国风俗史 张亮采" to "中国民间信仰风俗辞典" after snapshot calls.
