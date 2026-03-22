# Connection Tree Feature

## Overview

The Parameter Connections feature has been redesigned from a complex D3.js force-directed graph to a simple, intuitive hierarchical tree view. This provides a clearer visualization of immediate upstream and downstream parameter relationships.

## What Changed

### Previous Implementation
- Used D3.js force-directed graph visualization
- Showed all connections with physics-based layout
- Could be overwhelming with many connections
- Required D3.js library dependency

### New Implementation
- Hierarchical tree structure with clear sections
- Shows only immediate connections (upstream/downstream)
- Clickable nodes for easy navigation
- Pure CSS styling (no external dependencies)
- Integrated back button support

## Features

### 1. Tree Structure

The connection tree displays parameters in a clear hierarchy:

```
┌─────────────────────────────┐
│  Upstream Dependencies      │  ← What this parameter depends on (blue)
│  • dependency_param_1       │
│  • dependency_param_2       │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│   Current Parameter         │  ← The parameter you're viewing (purple)
│   param_name                │
└─────────────────────────────┘
              ↓
┌─────────────────────────────┐
│  Downstream References      │  ← What depends on this parameter (green)
│  • reference_param_1        │
│  • reference_param_2        │
└─────────────────────────────┘

┌─────────────────────────────┐
│  Related Concepts           │  ← Similar parameters (orange)
│  • related_param_1          │
└─────────────────────────────┘
```

### 2. Color-Coded Nodes

- **Blue nodes**: Upstream dependencies (what this parameter depends on)
- **Purple node**: Current parameter (root of the tree)
- **Green nodes**: Downstream references (what depends on this parameter)
- **Orange nodes**: Related concepts (similar parameters)

### 3. Interactive Navigation

- All nodes (except root) are clickable
- Clicking a node navigates to that parameter's details
- Back button in modal header returns to previous parameter
- Navigation history is preserved

### 4. Visual Design

- Hover effects on clickable nodes (slides right slightly)
- Visual connectors showing flow direction
- Context information shown on each node
- Responsive layout adapting to content

## Technical Implementation

### Files Modified

#### 1. `web/js/app.js`

**Modified `addConnectionsToModal()` function** (lines 728-790)
- Replaced D3.js graph initialization with tree building logic
- Categorizes connections into upstream, downstream, and related
- Generates HTML structure for hierarchical tree

**Added `buildConnectionTree()` function** (lines 795-882)
- Builds the HTML structure for the connection tree
- Creates sections for upstream, root, downstream, and related
- Adds visual connectors between sections
- Makes nodes clickable with `onclick` handlers

**Added `navigateToParameter()` function** (lines 887-891)
- Handles navigation when tree node is clicked
- Calls `displaySemantics()` with history tracking enabled
- Logs navigation for debugging

#### 2. `web/css/style.css`

**Added Connection Tree Styles** (lines 1479-1707)
- `.connection-tree-container`: Container styling with background
- `.tree-node`: Base node styling with transitions
- `.upstream-node`: Blue styling for dependencies
- `.root-node`: Purple gradient for current parameter
- `.downstream-node`: Green styling for references
- `.related-node`: Orange styling for related concepts
- `.tree-connector`: Visual connectors with arrow indicators
- Hover effects and responsive layout

### Data Structure

Connection data is read from `data/vvc/connections.json`:

```json
{
  "parameter_name": {
    "dependencies": [
      {
        "parameter": "dependency_param",
        "context": "Description of dependency",
        "strength": 0.8
      }
    ],
    "references": [
      {
        "parameter": "reference_param",
        "context": "Description of reference",
        "strength": 0.9
      }
    ],
    "related_concepts": [
      {
        "parameter": "related_param",
        "context": "Description of relation"
      }
    ]
  }
}
```

## Usage

### Viewing Connections

1. Click any syntax structure in the sidebar
2. Click a parameter to open its semantics modal
3. Scroll down to the "Parameter Connections" section
4. The tree will display all immediate connections

### Navigating Through Parameters

1. Click any blue upstream node to view a dependency
2. Click any green downstream node to view a reference
3. Click any orange related node to view a related parameter
4. Use the back arrow (←) in the modal header to return to previous parameters

### Understanding Connection Types

**Upstream Dependencies:**
- Parameters that the current parameter depends on
- Example: If `pic_width_in_luma_samples` depends on `sps_pic_width_max_in_luma_samples`, the latter is upstream

**Downstream References:**
- Parameters that depend on or reference the current parameter
- Example: If other parameters use `sps_seq_parameter_set_id` for lookup, they are downstream

**Related Concepts:**
- Parameters with similar names or related functionality
- Example: `sps_num_subpics_minus1` might be related to `pps_num_subpics_minus1`

## Benefits

1. **Clarity**: Immediate visual understanding of parameter relationships
2. **Simplicity**: No complex graph layouts to interpret
3. **Performance**: No external libraries required, faster loading
4. **Navigation**: Easy to explore related parameters with one click
5. **Maintainability**: Pure HTML/CSS, easier to customize and debug

## Browser Compatibility

The connection tree uses modern CSS features:
- CSS Grid and Flexbox
- CSS Gradients
- CSS Transitions
- No JavaScript framework dependencies

Tested and working in:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

## Future Enhancements

Potential improvements:
- Expand/collapse sections for large connection sets
- Filter connections by type or strength
- Show connection strength visually (line thickness, opacity)
- Export connection tree as image
- Breadcrumb navigation for deep parameter exploration
- Search within connections

## Migration Notes

### For Users
- No action required - the new tree view replaces the old graph automatically
- All existing connection data continues to work
- Navigation patterns remain the same

### For Developers
- D3.js dependency can be removed if not used elsewhere
- Connection data format remains unchanged
- The `loadConnectionsData()` function is still used
- Old graph code in `connection-graph.js` can be archived

## Troubleshooting

### Tree Not Displaying
- Check browser console for errors
- Verify `connections.json` exists in `data/vvc/`
- Ensure JavaScript is enabled
- Hard refresh browser (Ctrl+Shift+R or Cmd+Shift+R)

### Nodes Not Clickable
- Check if `navigateToParameter()` function exists in `app.js`
- Verify onclick handlers in generated HTML
- Check browser console for JavaScript errors

### Styling Issues
- Ensure `style.css` is loaded (check Network tab)
- Verify CSS starts at line 1479 for connection tree styles
- Clear browser cache and reload

## Related Documentation

- [README.md](README.md) - Main project documentation
- [AI_CACHE_FIX.md](AI_CACHE_FIX.md) - AI analysis caching system
- [PORT_8000_MIGRATION.md](PORT_8000_MIGRATION.md) - Server configuration
- [QUICK_START.md](QUICK_START.md) - Getting started guide
