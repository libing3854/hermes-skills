# GitHub JavaScript Selectors

Useful DOM selectors for extracting data from GitHub pages via `browser_console`.

## Repository List (User Profile Page)

```javascript
// All repo names on current page
Array.from(document.querySelectorAll('[itemprop="name codeRepository"]'))
  .map(el => el.textContent.trim())

// Repo descriptions
Array.from(document.querySelectorAll('[itemprop="description"]'))
  .map(el => el.textContent.trim())

// Star counts
Array.from(document.querySelectorAll('a[href$="/stargazers"]'))
  .map(el => el.textContent.trim())
```

## README Content

```javascript
// Full README text
document.querySelector('article.markdown-body')?.innerText

// README in chunks (for large READMEs)
const readme = document.querySelector('article.markdown-body')?.innerText || '';
readme.substring(0, 3000);   // First chunk
readme.substring(3000, 6000); // Second chunk

// README HTML (preserves formatting)
document.querySelector('article.markdown-body')?.innerHTML
```

## File Tree

```javascript
// All file/folder names in repo root
Array.from(document.querySelectorAll('a[data-testid="file-list-item"]'))
  .map(el => el.textContent.trim())

// Or via aria labels
Array.from(document.querySelectorAll('[aria-label*="Directory"]'))
  .map(el => el.textContent.trim())
```

## Issues and PRs

```javascript
// Issue titles
Array.from(document.querySelectorAll('a[data-hovercard-type="issue"]'))
  .map(el => el.textContent.trim())

// PR titles
Array.from(document.querySelectorAll('a[data-hovercard-type="pull_request"]'))
  .map(el => el.textContent.trim())
```

## Search Results

```javascript
// Repo search results
Array.from(document.querySelectorAll('[data-testid="results-list"] li'))
  .map(el => ({
    name: el.querySelector('a')?.textContent.trim(),
    desc: el.querySelector('.mb-1')?.textContent.trim(),
    stars: el.querySelector('[href$="/stargazers"]')?.textContent.trim()
  }))
```

## Pitfalls

- GitHub uses React-like rendering; selectors may change with UI updates
- Use `browser_snapshot` first to identify current element structure
- For paginated lists, scroll or navigate to next page first
- `document.querySelectorAll` returns a NodeList, not Array — use `Array.from()` or spread
