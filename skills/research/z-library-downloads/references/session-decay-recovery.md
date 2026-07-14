# Z-Library Session Decay: Reproduction & Recovery

## Symptom

After 1–2 successful `/s/KEYWORD` searches on Z-Library, subsequent search URL navigations redirect to either:
- An unrelated book detail page (e.g., a book about "民间百神" or "中国史话" despite searching for "四书五经")
- An unrelated search results page (e.g., `/s/中国民俗文化%20鬼神`)

The URL bar shows the correct search URL, but the page content is wrong.

## Root Cause

Z-Library's session state becomes stale or corrupted after download triggers. The site appears to maintain internal state that interferes with URL-based search navigation.

## Recovery Procedure

1. Navigate to `https://zh.z-library.sk/login`
2. The page will show the user is still authenticated:
   ```
   欢迎光临,  {username} !
   {email}
   高级帐户
   直到 {expiry_date}
   每日限额 X/10
   ```
3. Click "继续" button (uid from snapshot) or navigate to `https://zh.z-library.sk/`
4. Resume searching with `/s/KEYWORD` URLs

## Session Persistence Check

On the login page, look for:
- `uid=N heading "欢迎光临,  USERNAME !"` — user IS logged in
- `uid=N link "登录"` — user is NOT logged in

The first download in this session succeeded on a page where the nav showed user profile (logged in). After that download, subsequent pages showed "登录" (not logged in) despite the login page confirming authentication — suggesting the session state is page/tab-specific after downloads.

## Verification

After recovery, a search like `/s/四书五经` should return actual search results with matching book titles, not random unrelated pages.
