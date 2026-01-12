# Navigation UX: Missing links, dead ends, and accessibility improvements

## Overview

After reviewing the frontend navigation paths, I identified several UX issues that affect user flow and discoverability. This document outlines the problems and provides recommendations.

## Navigation Flow Analysis

```
                    ┌─────────────┐
                    │  HomePage   │
                    │     (/)     │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │ (search)      │ (autocomplete)│
           ↓               ↓               │
    ┌─────────────┐  ┌─────────────┐       │
    │ SearchPage  │  │  WordPage   │←──────┘
    │  (/search)  │  │ (/word/:id) │
    └──────┬──────┘  └──────┬──────┘
           │                │
     ┌─────┴─────┐          │ (view synset)
     ↓           ↓          ↓
┌─────────┐ ┌─────────────────┐
│WordPage │ │   SynsetPage    │←──┐
└─────────┘ │  (/synset/:id)  │───┘ (relations)
            └────────┬────────┘
                     │ (sense relations only)
                     ↓
            ┌─────────────────┐
            │   SensePage     │ ← HARD TO REACH
            │  (/sense/:id)   │
            └─────────────────┘
```

## Critical Issues

### 1. No Back Navigation Button
**Severity:** High
**Location:** All pages

Users must rely on browser back button. There's no in-app back navigation.

**Recommendation:** Add a back button to the page header using `useNavigate(-1)`.

```tsx
import { useNavigate } from 'react-router-dom';

function BackButton() {
  const navigate = useNavigate();
  return (
    <button onClick={() => navigate(-1)} className="...">
      ← Back
    </button>
  );
}
```

### 2. SensePage Nearly Unreachable
**Severity:** High
**Location:** Navigation flow

The SensePage (`/sense/:id`) is only accessible through sense-level relations. It's NOT linked from:
- WordPage (even though words have senses)
- SearchPage results

**Recommendation:**
- Add "View Sense" links in WordPage's Senses section
- Include sense results in SearchPage

### 3. Derived Words Not Clickable
**Severity:** High
**Location:** `WordPage.tsx`

Derived words are displayed as static tags, but should link to their respective word pages.

**Current:**
```tsx
{word.derived_words.map((derivedWord, i) => (
  <span key={i} className="px-3 py-1 rounded-full bg-[hsl(var(--secondary))] text-sm">
    {derivedWord}
  </span>
))}
```

**Recommendation:** Convert to clickable links:
```tsx
{word.derived_words.map((derivedWord, i) => (
  <Link
    key={i}
    to={`/search?q=${encodeURIComponent(derivedWord)}`}
    className="px-3 py-1 rounded-full bg-[hsl(var(--secondary))] text-sm hover:bg-[hsl(var(--primary))] hover:text-white transition-colors"
  >
    {derivedWord}
  </Link>
))}
```

### 4. Lemmas Not Clickable
**Severity:** High
**Location:** `SynsetPage.tsx`

Synset lemmas are displayed as static tags but should link to word search/pages.

**Recommendation:** Make lemmas clickable links to search for that word.

### 5. Breadcrumbs Component Not Rendered
**Severity:** Medium
**Location:** `ThreePanelLayout.tsx`

The `Breadcrumbs.tsx` component exists but is not included in the layout. Users have no visual indication of their navigation path.

**Recommendation:** Add `<Breadcrumbs />` to `ThreePanelLayout` above the main content area:
```tsx
import { Breadcrumbs } from '@/components/Breadcrumbs';

// In the main section:
<main className="flex-1 flex flex-col overflow-hidden">
  <div className="px-6 pt-4">
    <Breadcrumbs />
  </div>
  <div className="flex-1 overflow-auto p-6 lg:pl-6 pl-16">{main}</div>
</main>
```

### 6. Relations Truncated Without Pagination
**Severity:** Medium
**Location:** `SynsetPage.tsx`

Relations show only first 10 items with "+N more..." text, but there's no way to view all items.

**Recommendation:** Add "View All" button or implement expand/collapse:
```tsx
const [showAll, setShowAll] = useState(false);
const displayItems = showAll ? items : items.slice(0, 10);

// ... render displayItems ...

{items.length > 10 && (
  <button onClick={() => setShowAll(!showAll)}>
    {showAll ? 'Show Less' : `View All ${items.length}`}
  </button>
)}
```

## Summary Table

| Issue | Severity | Component | Status |
|-------|----------|-----------|--------|
| No back button | High | All pages | **Fixed** |
| SensePage unreachable | High | Navigation flow | **Fixed** |
| Derived Words not clickable | High | WordPage | **Fixed** |
| Lemmas not clickable | High | SynsetPage | **Fixed** |
| Breadcrumbs not rendered | Medium | ThreePanelLayout | **Fixed** |
| Relations truncated | Medium | SynsetPage | **Fixed** |
| Senses not in search results | Low | SearchPage | Open |

## Additional Notes

- The SearchBar being available on all pages is excellent for navigation
- URL structure is clean and RESTful (`/word/:id`, `/synset/:id`, `/sense/:id`)
- Consider showing selected lexicon filter more prominently on detail pages
- The Zustand store already tracks navigation history - could be leveraged for back/forward buttons

## Related Files

- `frontend/src/App.tsx` - Route definitions
- `frontend/src/pages/*.tsx` - Page components
- `frontend/src/components/Breadcrumbs.tsx` - Unused breadcrumbs component
- `frontend/src/components/SearchBar.tsx` - Search with autocomplete
- `frontend/src/stores/appStore.ts` - Navigation history state
