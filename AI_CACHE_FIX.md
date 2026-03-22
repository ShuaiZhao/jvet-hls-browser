# AI Analysis Cache Fix - Complete Solution

## Problem Summary

AI analysis results were being shared between different syntax structures. When you:
1. Clicked syntax A → viewed parameter → got AI analysis
2. Clicked syntax B → viewed same parameter → **saw the old AI analysis from syntax A** ❌

## Root Cause

The AI analysis container was **not being cleared** when switching parameters, so old results remained visible.

## Solution Applied

### Fix 1: Clear AI Analysis on Parameter Switch

**File:** `web/js/app.js` - `displaySemantics()` function

```javascript
function displaySemantics(paramName, pushToHistory = true, syntaxContext = null) {
    // IMPORTANT: Clear any previous AI analysis when switching parameters
    const aiContainer = document.getElementById('aiAnalysisContainer');
    if (aiContainer) {
        aiContainer.style.display = 'none';
        const aiContent = document.getElementById('aiAnalysisContent');
        if (aiContent) {
            aiContent.innerHTML = '';
        }
    }
    // ... rest of function
}
```

**What this does:**
- Every time you view a parameter's semantics, the old AI analysis is **completely cleared**
- Forces you to explicitly click "Explain with AI" again for each parameter
- Ensures you always get the analysis for the **current context**

### Fix 2: Visual Context Indicator

Added a visual badge showing which syntax structure you're currently viewing:

```javascript
// Add syntax context indicator to modal header
if (currentSemanticsContext) {
    contextIndicator.textContent = `in ${currentSemanticsContext}`;
    contextIndicator.style.display = 'block';
}
```

**What you'll see:**
- Parameter modal title shows: `sps_seq_parameter_set_id` **in seq_parameter_set_rbsp**
- Small gray badge indicates which syntax structure context you're in
- Changes when you view the same parameter in different syntax structures

### Fix 3: Enhanced Debug Logging

Console logs track every step:
- When syntax context changes
- What cache key is generated
- Whether cache hit or miss
- When cache is saved

## How to Verify It's Fixed

### Test Procedure

1. **Start fresh:**
   ```javascript
   // In browser console, clear all AI cache
   Object.keys(localStorage).filter(k => k.startsWith('ai_analysis_')).forEach(k => localStorage.removeItem(k));
   console.log('Cache cleared');
   ```

2. **Test with Syntax A:**
   - Click syntax structure: `seq_parameter_set_rbsp`
   - Click parameter: `sps_seq_parameter_set_id`
   - **Verify:** Modal shows "in seq_parameter_set_rbsp" badge
   - Click AI robot icon
   - **Verify:** Console shows cache key includes `seq_parameter_set_rbsp`
   - Wait for AI response
   - **Note:** The analysis specific to this syntax

3. **Test with Syntax B:**
   - Click different syntax structure: `pic_parameter_set_rbsp`
   - Click same parameter: `sps_seq_parameter_set_id` (if it exists)
   - **Verify:** Modal shows "in pic_parameter_set_rbsp" badge (different!)
   - **Verify:** AI analysis section is **hidden/empty** (not showing old analysis)
   - Click AI robot icon again
   - **Verify:** Console shows cache key includes `pic_parameter_set_rbsp` (different!)
   - **Verify:** Gets new AI analysis specific to this syntax

4. **Test cache persistence:**
   - Go back to `seq_parameter_set_rbsp`
   - Click `sps_seq_parameter_set_id` again
   - Click AI robot icon
   - **Verify:** Console shows "Cache lookup: HIT"
   - **Verify:** Shows the analysis you got in step 2 (cached)
   - **Verify:** Modal shows "in seq_parameter_set_rbsp"

### Expected Console Output

```javascript
// Syntax A - First time
[selectParameter] Parameter: sps_seq_parameter_set_id Syntax Context: seq_parameter_set_rbsp
[displaySemantics] Current Context After: seq_parameter_set_rbsp
[aiExplainParameter] Syntax Context: seq_parameter_set_rbsp
[aiExplainParameter] Cache lookup: MISS Cache Key: ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id
[saveCachedAnalysis] Saving cache with key: ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id

// Syntax B - First time (different cache key!)
[selectParameter] Parameter: sps_seq_parameter_set_id Syntax Context: pic_parameter_set_rbsp
[displaySemantics] Current Context After: pic_parameter_set_rbsp
[aiExplainParameter] Syntax Context: pic_parameter_set_rbsp
[aiExplainParameter] Cache lookup: MISS Cache Key: ai_analysis_vvc_pic_parameter_set_rbsp_sps_seq_parameter_set_id
[saveCachedAnalysis] Saving cache with key: ai_analysis_vvc_pic_parameter_set_rbsp_sps_seq_parameter_set_id

// Back to Syntax A - Uses cache
[selectParameter] Parameter: sps_seq_parameter_set_id Syntax Context: seq_parameter_set_rbsp
[displaySemantics] Current Context After: seq_parameter_set_rbsp
[aiExplainParameter] Syntax Context: seq_parameter_set_rbsp
[aiExplainParameter] Cache lookup: HIT Cache Key: ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id
```

## Key Differences - Before vs After

| Aspect | Before (Broken) | After (Fixed) |
|--------|----------------|---------------|
| **AI Container** | Stayed visible with old content | Cleared when switching parameters |
| **Context Indicator** | None | Shows "in syntax_structure_name" |
| **Cache Key** | Sometimes wrong context | Always correct context |
| **User Experience** | Confusing - wrong analysis shown | Clear - must click AI button again |
| **Debugging** | Hard to track | Console logs every step |

## How to Use Properly

### Workflow for Same Parameter in Different Contexts

1. View parameter in syntax A
2. Click AI explain → Get analysis for context A
3. Switch to syntax B
4. View same parameter → **AI section is empty** (expected!)
5. Click AI explain → Get **new** analysis for context B
6. Switch back to syntax A
7. View parameter → **AI section is empty** (expected!)
8. Click AI explain → Get **cached** analysis for context A (instant)

### Workflow for Related Parameters

1. View parameter in syntax A
2. Click AI explain → Get analysis
3. Click related parameter (stays in modal)
4. Context is **preserved** (still syntax A)
5. Click AI explain → Get analysis for same context

## Cache Structure

Each cache entry is stored with this structure:

```javascript
// Key format:
ai_analysis_{codec}_{syntaxContext}_{parameterName}

// Example keys:
ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id
ai_analysis_vvc_pic_parameter_set_rbsp_sps_seq_parameter_set_id

// Value format:
{
  "explanation": "AI generated text...",
  "timestamp": "2026-03-22T03:00:00.000Z",
  "codec": "vvc",
  "syntaxContext": "seq_parameter_set_rbsp"
}
```

## Cache Management Commands

### View All Cached Analyses

```javascript
Object.keys(localStorage)
  .filter(k => k.startsWith('ai_analysis_'))
  .forEach(key => {
    const data = JSON.parse(localStorage.getItem(key));
    console.log('Key:', key);
    console.log('Context:', data.syntaxContext);
    console.log('Time:', new Date(data.timestamp).toLocaleString());
    console.log('---');
  });
```

### Clear Specific Context

```javascript
const contextToClear = 'seq_parameter_set_rbsp';
Object.keys(localStorage)
  .filter(k => k.includes(contextToClear))
  .forEach(k => localStorage.removeItem(k));
console.log(`Cleared cache for context: ${contextToClear}`);
```

### Clear All AI Cache

```javascript
Object.keys(localStorage)
  .filter(k => k.startsWith('ai_analysis_'))
  .forEach(k => localStorage.removeItem(k));
console.log('Cleared all AI analysis cache');
location.reload(); // Refresh page
```

### Export Cache

```javascript
const cache = {};
Object.keys(localStorage)
  .filter(k => k.startsWith('ai_analysis_'))
  .forEach(key => {
    cache[key] = JSON.parse(localStorage.getItem(key));
  });
console.log(JSON.stringify(cache, null, 2));
```

## Troubleshooting

### "Still seeing old analysis"

**Solution:**
1. Hard refresh browser: Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
2. Clear browser cache
3. Clear AI analysis cache using console commands above

### "Context indicator not showing"

**Solution:**
1. Check console: Is `currentSemanticsContext` set?
2. Make sure you clicked a syntax structure first
3. Refresh page and try again

### "Wrong cache key being used"

**Solution:**
1. Check console logs - what context is being used?
2. Make sure `currentStructure` is set when you click syntax
3. Clear cache and test with fresh analyses

## Summary

✅ **The fix ensures:**
1. Old AI analyses are cleared when switching parameters
2. Each syntax context has independent cache entries
3. Visual indicator shows current context
4. Console logs help debug any issues
5. Re-run button always uses current context

✅ **User now sees:**
- Empty AI section when viewing parameter (expected)
- Must click "Explain with AI" explicitly
- Context badge showing which syntax structure
- Cached results only for exact same (param + context) combination

The AI analysis is now **truly context-specific**! 🎉
