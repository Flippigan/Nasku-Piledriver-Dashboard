# Compact Dashboard Redesign

## Problem Statement

The current dashboard has poor usability:
- Icons/elements are too large
- Cards take up too much vertical and horizontal space
- Users cannot see all inverters at a glance
- Scrolling required to view 20-30 inverters typical in a project

## Goal

All inverters visible on one screen without scrolling, with essential status information scannable at a glance.

## Design Specification

### Card Structure

Each compact card displays:
1. **Inverter name** - Top of card, truncated with ellipsis if exceeds width
2. **Vertical progress bar** - Primary visual element, fills most of card height
3. **Percentage label** - Below the progress bar (e.g., "73%")
4. **Current workflow step** - Bottom of card, small text, truncated if needed
5. **Status color** - Integrated into progress bar fill:
   - Green: > 6 days until due
   - Yellow: 2-6 days until due
   - Red: < 2 days or overdue

### Card Dimensions

- Width: ~120px
- Height: ~180px
- Progress bar height: ~100px
- Minimal padding to maximize density

### Grid Layout

- **Columns:** 6-8 depending on viewport width
- **Rows:** 4-5 visible without scrolling
- **Capacity:** 24-40 cards visible on 1080p display
- **Sorting:** Alphabetical by inverter name (existing behavior)

### Interaction

- **Click:** Opens expanded detail view (existing `expanded_card.py`)
- **Hover:** Tooltip shows full inverter name and step name if truncated
- Details button removed (entire card is clickable)

### Visual Hierarchy

1. Progress bar (largest element, immediate visual scan)
2. Status color (urgency at a glance via color)
3. Inverter name (identification)
4. Percentage (precise progress)
5. Step name (current work context)

## Technical Approach

### Files to Modify

- `src/ui/dashboard.py` - Main grid layout and card rendering
- Possibly new CSS/styling for vertical progress bars (Streamlit custom components or HTML)

### Implementation Notes

Streamlit's native `st.progress()` is horizontal only. Options for vertical progress:
1. **Custom HTML/CSS** - Use `st.markdown()` with inline styles for vertical bar
2. **Plotly bar chart** - Single vertical bar chart, minimal chrome
3. **SVG** - Inline SVG via `st.markdown()`

Recommended: Custom HTML/CSS for simplicity and full control over styling.

### Example Card HTML Structure

```html
<div class="inverter-card" style="width:120px; height:180px; border:1px solid #ddd; border-radius:8px; padding:8px; text-align:center; cursor:pointer;">
  <div class="name" style="font-size:12px; font-weight:bold; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
    INV-001
  </div>
  <div class="progress-container" style="height:100px; width:30px; margin:8px auto; background:#eee; border-radius:4px; position:relative;">
    <div class="progress-fill" style="position:absolute; bottom:0; width:100%; height:73%; background:#22c55e; border-radius:4px;"></div>
  </div>
  <div class="percentage" style="font-size:14px; font-weight:bold;">73%</div>
  <div class="step" style="font-size:10px; color:#666; white-space:nowrap; overflow:hidden; text-overflow:ellipsis;">
    Pile Installation
  </div>
</div>
```

## Delivery

- Create feature branch: `feature/compact-dashboard`
- Implement changes
- Open PR for review before merging to main

## Success Criteria

- [ ] All 30 inverters visible on 1080p screen without scrolling
- [ ] Each card shows: name, vertical progress, status color, current step
- [ ] Click on card opens existing detail view
- [ ] Responsive to different screen widths (fewer columns on narrower screens)
- [ ] No loss of existing functionality

---
