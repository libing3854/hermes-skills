# Z-Library Browser Automation Reference

## Account & Access

- **Registration**: `/registration` page, requires email + password + nickname, then email verification code
- **Login**: `/login` page, email + password
- **Premium**: Registration grants 2 weeks of premium membership (unlimited download speed, more daily downloads)
- **Daily limit**: BASIC accounts get 10 downloads/day; premium removes this
- **File naming convention**: Downloads include site name in parentheses: `Book Title (z-library.sk, 1lib.sk, z-lib.sk).pdf`

## URL Patterns

| Type | Format | Example |
|------|--------|---------|
| Search | `https://zh.z-library.sk/s/{query}` | `/s/道教大辞典` |
| Book detail | `https://zh.z-library.sk/book/{hash}/{slug}.html` | `/book/ZjKa821qO0/道教大辞典.html` |
| Direct download (UNRELIABLE) | `https://zh.z-library.sk/dl/{hash}` | `/dl/XBebno8Pwb` |
| Login | `https://zh.z-library.sk/login` | |
| Registration | `https://zh.z-library.sk/registration` | |

## Critical Pitfall: Direct /dl/ URLs Return "Bad Gateway"

**Do NOT use direct `/dl/{hash}` URLs** — they frequently return "Bad Gateway" errors even when logged in.

**Correct approach**: Always navigate to the **book detail page** first (`/book/{hash}/{slug}.html`), then click the download link (typically a "PDF, XX.XX MB" link).

```
# WRONG — often fails with Bad Gateway
navigate_page(url="https://zh.z-library.sk/dl/XBebno8Pwb")

# CORRECT — navigate to detail page, then click download link
navigate_page(url="https://zh.z-library.sk/book/ZjKa821qO0/道教大辞典.html")
take_snapshot()
click(uid_of_pdf_download_link)
```

## Search & Download Workflow

```
1. navigate_page → https://zh.z-library.sk/s/{search_term}
2. take_snapshot → scan results for book titles, authors, years, file sizes
3. click → book link (uid for the book title link)
4. take_snapshot → find PDF download link (look for "PDF, XX.XX MB" text)
5. click → PDF download link
6. terminal → monitor ~/Downloads for .crdownload files (still downloading)
7. terminal → verify .pdf appeared and .crdownload gone
8. terminal → move to organized destination
9. browser_back → return to search results for next book
```

## Book Detail Page Element Pattern

On book detail pages, the download link is typically structured as:
- Look for elements containing "PDF" and file size (e.g., "PDF, 58.90 MB")
- The link text format is: `PDF, {size} MB`

## Batch Download Considerations

- **Speed**: Each book requires ~1-2 minutes (navigate + snapshot + click + wait for download)
- **20+ books**: Consider suggesting alternatives (desktop client, manual download with organized list)
- **Z-Library desktop client**: Available at `/z-access#desktop_app_tab`, 122MB for macOS, gives 2x daily limits
- **Per-book folders**: User preference — create `mkdir -p "{base}/{book_name}"` for each book before downloading

## Multi-Search Strategy for Curated Downloads

When user wants "find good books about X":
```
1. Use delegate_task to search multiple keywords in parallel
2. Each subagent searches 1 keyword, records top 10 books (title, author, year, size, URL)
3. Consolidate results, deduplicate, present curated list to user
4. After user approves, batch download
```

Keywords for Chinese traditional culture:
- 中国民俗 / 民间信仰 / 神话传说 / 鬼神文化
- 道藏 / 道教经典 / 道德经 / 庄子 / 抱朴子
- 佛经 / 金刚经 / 心经 / 楞严经 / 法华经
- 四书五经 / 儒家经典 / 论语 / 孟子 / 诸子百家

## File Organization Convention

User preference: each book gets its own folder under a category directory:
```
{base_dir}/{category}/{book_name}/
  └── {book_name} (z-library.sk, ...).pdf
```
