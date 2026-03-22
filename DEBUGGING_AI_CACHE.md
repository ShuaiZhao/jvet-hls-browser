# Debugging AI Analysis Cache Issues

## Problem
AI analysis results are being shared between different syntax contexts when they should be independent.

## How the Cache Should Work

Each parameter should have **separate AI analysis** for each syntax structure it appears in:

**Example:**
- `sps_seq_parameter_set_id` in `seq_parameter_set_rbsp` → Cache key: `ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id`
- `sps_seq_parameter_set_id` in `pic_parameter_set_rbsp` → Cache key: `ai_analysis_vvc_pic_parameter_set_rbsp_sps_seq_parameter_set_id`

These should be **different cached entries**.

## Debugging Steps

### Step 1: Open Browser Console

1. Open the application: http://localhost:8000
2. Login with admin/admin_password
3. Press **F12** or **Cmd+Option+I** to open Developer Tools
4. Go to the **Console** tab

### Step 2: Watch the Logs

The code now logs debug information. You'll see:

```javascript
[selectParameter] Parameter: sps_seq_parameter_set_id Syntax Context: seq_parameter_set_rbsp
[displaySemantics] Param: sps_seq_parameter_set_id New Context: seq_parameter_set_rbsp Current Context Before: null
[displaySemantics] Current Context After: seq_parameter_set_rbsp
[aiExplainParameter] Param: sps_seq_parameter_set_id Syntax Context: seq_parameter_set_rbsp Force Refresh: false
[aiExplainParameter] Cache lookup: MISS Cache Key: ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id
[saveCachedAnalysis] Saving cache with key: ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id Context: seq_parameter_set_rbsp
```

### Step 3: Test Different Contexts

1. Click on syntax structure **A** (e.g., `seq_parameter_set_rbsp`)
2. Click a parameter (e.g., `sps_seq_parameter_set_id`)
3. Click "Explain with AI" (robot icon)
4. **Note the cache key in console**

Then:

5. Click on syntax structure **B** (e.g., `pic_parameter_set_rbsp`)
6. Click the **same parameter** if it exists in both
7. Click "Explain with AI" again
8. **Check if the cache key is different**

### Step 4: Inspect What Went Wrong

Look for these issues in the console logs:

**Issue 1: Context is null**
```
[selectParameter] Parameter: xxx Syntax Context: null
```
**Cause:** `currentStructure` is not being set when user clicks a syntax structure.

**Issue 2: Context is not changing**
```
[displaySemantics] New Context: seq_parameter_set_rbsp Current Context Before: seq_parameter_set_rbsp
[displaySemantics] Current Context After: seq_parameter_set_rbsp
```
Then user clicks different structure but context stays same.
**Cause:** Context is being preserved when it shouldn't be.

**Issue 3: Cache key is the same**
```
Cache Key: ai_analysis_vvc__sps_seq_parameter_set_id
```
Notice the double underscore `__` - means syntaxContext is empty string.
**Cause:** Context is empty when it reaches aiExplainParameter.

## Manual Cache Inspection

### View All Cached Entries

Open Console and run:

```javascript
// List all AI analysis cache entries
Object.keys(localStorage).filter(k => k.startsWith('ai_analysis_')).forEach(key => {
    const data = JSON.parse(localStorage.getItem(key));
    console.log('Key:', key);
    console.log('Context:', data.syntaxContext);
    console.log('Timestamp:', data.timestamp);
    console.log('---');
});
```

### Check Specific Cache Entry

```javascript
// Check cache for specific parameter
const paramName = 'sps_seq_parameter_set_id';
const syntaxContext = 'seq_parameter_set_rbsp';
const cacheKey = `ai_analysis_vvc_${syntaxContext}_${paramName}`;
const cached = localStorage.getItem(cacheKey);
console.log('Cache entry:', JSON.parse(cached));
```

### Clear Specific Cache Entry

```javascript
// Clear cache for specific context
const paramName = 'sps_seq_parameter_set_id';
const syntaxContext = 'seq_parameter_set_rbsp';
const cacheKey = `ai_analysis_vvc_${syntaxContext}_${paramName}`;
localStorage.removeItem(cacheKey);
console.log('Cleared cache for:', cacheKey);
```

### Clear ALL AI Analysis Cache

```javascript
// Clear all AI analysis cache (WARNING: deletes all cached analyses)
Object.keys(localStorage).filter(k => k.startsWith('ai_analysis_')).forEach(key => {
    localStorage.removeItem(key);
});
console.log('Cleared all AI analysis cache');
```

## Expected Behavior

### When Working Correctly

1. User clicks `seq_parameter_set_rbsp`
   - Console: `[selectParameter] ... Syntax Context: seq_parameter_set_rbsp`

2. User clicks parameter `sps_seq_parameter_set_id`
   - Console: `[displaySemantics] ... New Context: seq_parameter_set_rbsp`
   - Console: `[displaySemantics] ... Current Context After: seq_parameter_set_rbsp`

3. User clicks "Explain with AI"
   - Console: `[aiExplainParameter] ... Syntax Context: seq_parameter_set_rbsp`
   - Console: `Cache Key: ai_analysis_vvc_seq_parameter_set_rbsp_sps_seq_parameter_set_id`

4. User clicks different syntax: `pic_parameter_set_rbsp`
   - Console: `[selectParameter] ... Syntax Context: pic_parameter_set_rbsp`

5. User clicks same parameter again
   - Console: `[displaySemantics] ... New Context: pic_parameter_set_rbsp`
   - Console: `[displaySemantics] ... Current Context After: pic_parameter_set_rbsp`

6. User clicks "Explain with AI"
   - Console: `Cache Key: ai_analysis_vvc_pic_parameter_set_rbsp_sps_seq_parameter_set_id`
   - **Different cache key!** ✅

## Common Issues and Fixes

### Issue: currentStructure is null

**Symptom:**
```
[selectParameter] Parameter: xxx Syntax Context: null
```

**Fix:** Check that `displaySyntaxStructure` function sets `currentStructure`:
```javascript
function displaySyntaxStructure(structure) {
    currentStructure = structure.name;  // Make sure this line exists
    // ...
}
```

### Issue: Context preserved incorrectly

**Symptom:**
Context doesn't change when clicking different syntax structures.

**Fix:** The `displaySemantics` function should ALWAYS update context when provided:
```javascript
if (syntaxContext !== null) {
    currentSemanticsContext = syntaxContext;  // This updates the context
}
```

### Issue: Cache key has empty context

**Symptom:**
```
Cache Key: ai_analysis_vvc__paramName
```

**Fix:** Check that `currentSemanticsContext` is set before calling `aiExplainParameter`.

## Testing Checklist

- [ ] Open browser console (F12)
- [ ] Click syntax structure A
- [ ] Check console: `currentStructure` should be set
- [ ] Click parameter
- [ ] Check console: `currentSemanticsContext` should equal structure A
- [ ] Click "Explain with AI"
- [ ] Check console: cache key should include structure A name
- [ ] Click syntax structure B
- [ ] Click same parameter
- [ ] Check console: `currentSemanticsContext` should NOW equal structure B
- [ ] Click "Explain with AI"
- [ ] Check console: cache key should include structure B name (different from A)
- [ ] Verify: Two different cache entries exist in localStorage

## Quick Fix: Force Refresh

If cached analysis is wrong for a parameter:

1. Click "Re-run Analysis" button (sync icon)
2. This will fetch a new analysis with correct context
3. Old cache for that context will be overwritten

## Contact

If the issue persists after debugging:
1. Copy the console logs
2. Note which parameters and syntax structures are affected
3. Check if the cache keys are being generated correctly
4. Clear cache and test again
