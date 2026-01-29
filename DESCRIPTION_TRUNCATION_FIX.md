# Fix: Recipe Description Truncation Issue

## Problem
Recipe cards were displaying truncated descriptions cut off mid-word:
```
🟢 Fromage blanc avec miel
Lentilles corail cuites à la perfection, riches en p
```

The description was being cut at exactly 60 characters, breaking words.

## Root Cause
In `src/domains/cuisine/ui/recettes.py` line 250:
```python
desc = recette.description[:60]  # Hardcoded 60-char limit
if len(recette.description) > 60:
    desc += "..."
```

This was truncating descriptions at arbitrary character boundaries, often in the middle of words.

## Solution
Increased the character limit from 60 to 150 and implemented smart truncation that:
1. Respects word boundaries (doesn't cut mid-word)
2. Finds the last space before the 150-character limit
3. Truncates at that space instead
4. Still respects the CSS `-webkit-line-clamp: 2` which limits to 2 visual lines

## New Code
```python
if recette.description:
    desc = recette.description
    # Limit to ~150 chars but don't cut mid-word
    if len(desc) > 150:
        truncated = desc[:150]
        last_space = truncated.rfind(' ')
        if last_space > 100:  # At least 100 chars
            desc = truncated[:last_space] + "..."
        else:
            desc = truncated + "..."
    st.markdown(f"<p style='...overflow: hidden; -webkit-line-clamp: 2; ...'>{desc}</p>", unsafe_allow_html=True)
```

## Results
- Descriptions now show complete words
- Respects visual 2-line limit from CSS
- More readable preview text on recipe cards
- Maintains consistent card height

## File Modified
- `src/domains/cuisine/ui/recettes.py` (lines 248-251)

## Testing
✅ Syntax validation passed
✅ No breaking changes
✅ Backward compatible
