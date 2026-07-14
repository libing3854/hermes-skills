# Z-Library DOM Patterns & URL Reference

## Search Results Page

### Custom Elements
Books are rendered as `<z-bookcard>` custom elements:

```html
<div class="book-item resItemBoxBooks">
  <div class="counter">1</div>
  <z-bookcard
    id="12288183"
    isbn="9787542664143"
    termshash="f107ab5b1b6490ca6cf6b7353f004ca2"
    href="/book/eOWr4BLnvb/..."
  ></z-bookcard>
</div>
```

**Note**: The `href` attribute on `<z-bookcard>` is not always present. In
practice, Z-Library sometimes renders `href` as a direct attribute, and
sometimes only exposes it inside the Shadow DOM. Always try the shadow-root
approach first, and fall back to the direct attribute.

### Extraction Script (Primary — Shadow DOM)
```javascript
const cards = document.querySelectorAll('z-bookcard');
const results = [];
cards.forEach((card, i) => {
  if (card.shadowRoot) {
    const links = card.shadowRoot.querySelectorAll('a[href*="/book/"]');
    links.forEach(a => {
      results.push({
        cardIndex: i,
        bookId: card.id,
        href: a.getAttribute('href'),
        text: card.shadowRoot.textContent.substring(0, 200)
      });
    });
  }
  // Fallback: direct href attribute
  const directHref = card.getAttribute('href');
  if (directHref && directHref.includes('/book/')) {
    results.push({ cardIndex: i, bookId: card.id, href: directHref });
  }
});
return results.slice(0, 5);
```

### Extraction Script (Fallback — Direct attributes, older Z-Library layout)
```javascript
const cards = document.querySelectorAll('z-bookcard');
Array.from(cards).slice(0, 5).map(c => ({
  id: c.getAttribute('id'),
  href: c.getAttribute('href'),
  isbn: c.getAttribute('isbn'),
  termshash: c.getAttribute('termshash')
}));
```

## Book Detail Page

### Available Format Detection
```javascript
// Direct download links use /dl/ path
document.querySelectorAll('a').forEach(a => {
  const href = a.getAttribute('href') || '';
  if (href.startsWith('/dl/')) {
    // This is a direct download format
    // a.textContent will show format + size, e.g., "epub, 25.98 MB"
  }
});
```

### Format Buttons
- Direct download: `<a class="btn btn-default addDownloadedBook" href="/dl/WZMvGO6ojx">`
- Converter-only (unavailable): `<a class="converterLink no-js__unavailable" href="javascript:void(0);">`
- Read online: `<a class="btn btn-primary dlButton reader-link" href="https://reader.z-library.sk/...">`
- Send to: `<button class="btn btn-default dropdown-toggle button-send-book">`
- Format dropdown: `<button class="btn btn-default dropdown-toggle dlDropdownBtn">`

### Download Trigger
```javascript
// Click primary download button
const dlBtn = document.querySelector('.addDownloadedBook');
if (dlBtn) dlBtn.click();

// Or navigate directly to download URL
// Format: https://zh.z-library.sk/dl/<shortcode>
```

## URL Patterns

| Purpose | Pattern |
|---------|---------|
| Homepage | `https://zh.z-library.sk/` |
| Search (URL-based, unreliable) | `https://zh.z-library.sk/s/关键词` |
| Search (form-based, reliable) | `https://zh.z-library.sk/s/?q=关键词` |
| Book detail | `https://zh.z-library.sk/book/<code>/<title>.html` |
| Download | `https://zh.z-library.sk/dl/<shortcode>` |
| Read online | `https://reader.z-library.sk/read/<hash>/book/<code>/<title>` |

## Verifying Page State After Navigation

After any `navigate_page` call, verify the actual URL with JavaScript — do not
trust the tool's response alone. The tool may report "Successfully navigated"
while the DevTools panel is connected to a stale page:

```javascript
() => ({ url: window.location.href, title: document.title })
```

If `window.location.href` doesn't match the intended destination, re-navigate
or use `new_page` with `isolatedContext` for a truly fresh session.

## Known Issues with URL-based Search

Navigating to `https://zh.z-library.sk/s/关键词` (without `?q=` parameter) often shows stale or wrong search results. The page title and search box may reflect a different query than what the URL suggests. Always prefer form-based search via the homepage.

## Isolated Context Behavior

When `navigate_page` opens a new page with `isolatedContext=zlib-fresh`, that page operates in a separate browser context (separate cookies/storage). After navigation, explicitly select the page with `mcp_chrome_devtools_select_page(pageId=X, bringToFront=true)` before running scripts.
