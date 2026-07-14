# Verified z-bookcard Extraction Pattern (2026-07-01)

## The working extraction script

This was verified on `https://zh.z-library.sk/s/?q=中国民俗史+钟敬文`:

```javascript
() => {
  const cards = document.querySelectorAll('z-bookcard');
  return Array.from(cards).map((card, i) => ({
    index: i,
    title: card.querySelector('[slot="title"]')?.textContent?.trim(),
    href: card.getAttribute('href'),
    download: card.getAttribute('download'),
    extension: card.getAttribute('extension'),
    filesize: card.getAttribute('filesize')
  }));
}
```

**Confirmed**: All four attributes (`href`, `download`, `extension`, `filesize`) are directly on the `<z-bookcard>` element. No shadow DOM traversal needed.

## Sample output

```json
[
  {
    "index": 0,
    "title": "中国民俗史 宋辽金元卷",
    "href": "/book/8vl8MVLave/%E4%B8%AD%E5%9B%BD%E6%B0%91%E4%BF%97%E5%8F%B2-%E5%AE%8B%E8%BE%BD%E9%87%91%E5%85%83%E5%8D%B7.html",
    "download": "/dl/owRN8lzkwl",
    "extension": "pdf",
    "filesize": "50.74 MB"
  },
  {
    "index": 1,
    "title": "中国民俗史 4 宋辽金元卷",
    "href": "/book/9vqd70rPjA/...",
    "download": "/dl/VBnqLROdj1",
    "extension": "pdf",
    "filesize": "36.54 MB"
  }
]
```

## Book detail page URL format

Both work:
- `https://zh.z-library.sk/book/8vl8MVLave/` (ID only, no slug)
- `https://zh.z-library.sk/book/8vl8MVLave/中国民俗史-宋辽金元卷.html` (with slug)

## Download link on detail page

```javascript
() => {
  const dlLink = document.querySelector('a[href*="/dl/"]');
  if (dlLink) {
    dlLink.click();
    return { clicked: true, href: dlLink.getAttribute('href') };
  }
  return { clicked: false };
}
```

The link element typically has class `btn btn-default addDownloadedBook` and text like `pdf, 50.74 MB`.

## Desktop app popup

```javascript
// Dismiss before any data extraction
document.querySelector('.desktop-banner-close')?.click();
```

## DOM vs visual order

The 51 `<z-bookcard>` elements on the search page are in a different order than what's visually displayed. Always filter by title text — never assume `cards[0]` is the first visible result.
