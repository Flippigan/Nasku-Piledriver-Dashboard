# Inverter Tracker Dashboard - Design Document

## Overview

A dashboard for VDC engineers to visualize pile installation progress and workflow status across solar site inverters. Built as a desktop .exe that connects to a shared Supabase database for multi-user access.

## Tech Stack

- **Frontend/App**: Streamlit (Python), packaged as .exe via PyInstaller
- **Database**: Supabase (hosted PostgreSQL)
- **Data Flow**: Read-only import of CSVs, app owns workflow state

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Streamlit App (.exe)                 │
├─────────────┬─────────────┬─────────────┬──────────────┤
│  Dashboard  │   Import    │  Settings   │   Alerts     │
│    View     │   Manager   │    Panel    │   Manager    │
└──────┬──────┴──────┬──────┴──────┬──────┴───────┬──────┘
       │             │             │              │
       └─────────────┴──────┬──────┴──────────────┘
                            │
                    ┌───────▼───────┐
                    │  Data Layer   │  ← Abstraction for DB operations
                    └───────┬───────┘
                            │
                    ┌───────▼───────┐
                    │   Supabase    │  ← Shared PostgreSQL
                    └───────────────┘
```

**Key Design Decisions:**
- Data layer abstraction so database could be swapped if needed
- Alert manager designed as plugin system for future notification types
- CSV import is one-way (into Supabase), app never writes back to CSV files

## Data Model

### Tables

**projects**
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| name | text | Project name (e.g., "Solar Site Alpha") |
| default_scan_threshold_pct | integer | Global default for first scan trigger (e.g., 90) |
| default_pile_rate | integer | Piles/day for unstarted inverter ETA |
| created_at | timestamp | Creation time |

**inverters**
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| project_id | uuid | Foreign key to projects |
| name | text | Inverter name (e.g., "Inverter 1") |
| total_piles | integer | Expected pile count |
| scan_threshold_override | integer | Null = use project default |
| milestone_thresholds | jsonb | Array of percentages (e.g., [50, 75, 90]) |
| created_at | timestamp | Creation time |

**piles**
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| inverter_id | uuid | Foreign key to inverters |
| upn | text | Unique pile number from drivelog |
| hammering_status | text | From nasku (e.g., "COMPLETED") |
| hammering_flag | text | From nasku (e.g., "GOOD") |
| hammering_time_sec | float | Hammering time in seconds |
| positioning_time_sec | float | Positioning time in seconds |
| driven_at | timestamp | When pile was completed |

**workflow_steps**
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| inverter_id | uuid | Foreign key to inverters |
| step_name | text | e.g., "First Scan", "Processed" |
| step_order | integer | 1-11 |
| is_complete | boolean | Whether step is done |
| completed_at | timestamp | When completed (nullable) |
| due_date | date | Optional due date |
| assigned_engineer | text | Engineer name (nullable) |

**alerts**
| Column | Type | Description |
|--------|------|-------------|
| id | uuid | Primary key |
| inverter_id | uuid | Foreign key to inverters |
| alert_type | text | e.g., "milestone_reached" |
| threshold_value | integer | e.g., 75 |
| acknowledged | boolean | Whether user acknowledged |
| created_at | timestamp | When alert was triggered |

### Workflow Steps (per inverter)

1. First Scan
2. Processed
3. Points Picked
4. Pushed to ArcGIS
5. Remediation Performed
6. Second Scan Complete
7. Processed
8. Points Picked
9. Pushed to ArcGIS
10. Second Remediation Performed
11. Walk Down

## CSV Import Logic

### Drivelog Import (project setup)

1. User uploads drivelog.csv
2. App extracts only required columns, discards the rest:
   - `Inverter`, `UPN`, `Hammering_Status`, `Hammering_Flag`
3. Creates unique inverter records with pile counts
4. Creates 11 workflow_steps per inverter (all unchecked)
5. Stores pile rows with UPN as unique identifier

### Nasku Import (progress updates)

1. User uploads nasku.csv
2. App extracts only required columns:
   - `name` (UPN), `hammeringStatus`, `hammeringFlag`, `hammeringTime`, `positioningTime`, `processedAt`
3. For each row, match to existing pile by UPN
4. **If any UPN has no match, reject entire import** with error showing unmatched UPNs
5. Update matched piles with new status data
6. A pile counts as "installed" only if: `hammering_status = "COMPLETED"` AND `hammering_flag = "GOOD"`
7. After import, recalculate:
   - Progress % per inverter
   - ETA based on new rate data
   - Check milestone thresholds → create alerts if crossed

### Future API Hook

- Import logic lives in a module that accepts data (not file paths)
- Easy to swap "read from CSV" with "fetch from API endpoint"
- Placeholder for scheduled polling interval setting

## Dashboard UI

### Main View - Grid of Cards

```
┌─────────────────────────────────────────────────────────────┐
│  Project: Solar Site Alpha          [Import CSV] [Settings] │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐         │
│  │ Inverter 1  │  │ Inverter 2  │  │ Inverter 3  │   ...   │
│  │ ████████░░  │  │ ██████░░░░  │  │ ░░░░░░░░░░  │         │
│  │ 82% (1640)  │  │ 61% (1220)  │  │ 0% (0)      │         │
│  │             │  │             │  │             │         │
│  │ Points Pick │  │ First Scan  │  │ Not Started │         │
│  │ 🟡 Due: 2d  │  │ 🟢          │  │ 🟢          │         │
│  │ @Sarah      │  │ @John       │  │ --          │         │
│  │             │  │             │  │             │         │
│  │ ETA: Feb 3  │  │ ETA: Feb 8  │  │ ETA: Feb 15 │         │
│  │ 45 piles/d  │  │ 38 piles/d  │  │ (default)   │         │
│  │        [!]  │  │             │  │             │         │
│  └─────────────┘  └─────────────┘  └─────────────┘         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Card Elements (at a glance)

- Inverter name
- Progress bar with % and pile count
- Current workflow step name
- Color indicator based on due date
- Assigned engineer for current step
- ETA date + piles/day (shows "default" if unstarted)
- Alert badge `[!]` if milestone needs acknowledgment

### Expanded Card (on click)

- Full workflow checklist with checkboxes
- Each step shows: checkbox, name, due date picker, engineer dropdown
- Milestone threshold settings
- Scan threshold override field
- "Acknowledge alerts" button if any pending

## Settings

### Project Settings

- Project name
- Default first scan threshold (%)
- Default pile rate for unstarted inverters (piles/day)
- Color thresholds:
  - Green: 7+ days remaining (or no due date)
  - Yellow: 2-6 days remaining
  - Red: <2 days or overdue
- Engineer list (names used in dropdowns)

### Per-Inverter Settings (in expanded card)

- Scan threshold override (null = use project default)
- Milestone alert thresholds (array of percentages)

## ETA Calculation

**For active inverters (at least one pile driven):**
1. Calculate average time per pile: `total_time_spent / piles_installed`
2. Calculate remaining piles: `total_piles - piles_installed`
3. Estimated time remaining: `avg_time_per_pile × remaining_piles`
4. Rate is calculated from first pile driven to now (wall clock time)

**For unstarted inverters:**
- Use project's default pile rate setting
- Display "(default)" next to rate

**Display:**
- Show absolute ETA date (e.g., "Feb 3, 4:00 PM")
- Show piles/day rate alongside for sanity checking

## Error Handling

### CSV Import Errors

- Missing required columns → Show error listing which columns are missing, reject import
- Nasku row with no matching UPN → Reject entire import, show which UPNs failed to match
- Duplicate UPNs in drivelog → Warn user, keep first occurrence
- Empty file → Show "file is empty" error

### Data Edge Cases

- Inverter with 0 piles in drivelog → Allow it, show 0/0 progress, skip ETA calculation
- All piles installed but First Scan not checked → Show "Ready for First Scan" with visual emphasis
- Workflow step marked complete out of order → Allow it
- Due date set in the past → Show as red immediately

### Connection Issues

- Supabase unreachable → Show clear error banner, disable editing, allow retry
- Import fails mid-way → Roll back entire import (transaction), show error

### Multi-User

- Two users update same inverter simultaneously → Last write wins
- No locking or conflict resolution for v1

## Scope

### Version 1 (In Scope)

- Streamlit app packaged as .exe via PyInstaller
- Supabase database, multi-user, no authentication
- Import drivelog.csv (project setup) and nasku.csv (progress updates)
- Grid of inverter cards with progress bars, ETA, current step, engineer, status
- Expandable cards with full workflow checklist (11 steps)
- Per-step due dates, engineer assignments
- Color-coded status (green/yellow/red) based on configurable thresholds
- First scan triggered by pile % threshold (global default + per-inverter override)
- ETA calculation based on pile rate (actual for active, default for unstarted)
- Visual milestone alerts with acknowledgment
- Project settings panel

### Future (Out of Scope for v1)

- API source for nasku data (polling endpoint)
- External alert integrations (email, Slack, desktop notifications)
- Audit log of who changed what
- Role-based permissions
- Multiple projects

### Not Planned

- Write-back to drivelog/nasku CSVs
- ArcGIS integration (handled separately)
- Authentication/user accounts
