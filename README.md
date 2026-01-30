# Inverter Tracker Dashboard

A Streamlit dashboard for VDC engineers to track pile installation progress and workflow status across solar site inverters.

## Quick Start (Demo Mode)

Run the app without any database setup to explore with sample data:

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run src/app.py
```

The app will start in **Demo Mode** with 6 sample inverters at various completion stages (0%, 5%, 25%, 50%, 75%, 90%). All features work in demo mode - you can click cards, view workflows, and explore the UI.

Demo mode is automatically enabled when no Supabase credentials are configured.

## Connecting to Supabase

To persist data with a real database:

### 1. Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and create a new project
2. Wait for the project to finish provisioning

### 2. Set Up the Database

1. In Supabase, go to **SQL Editor**
2. Copy the contents of `scripts/setup_database.sql`
3. Paste and run the SQL to create all tables

### 3. Configure Credentials

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. In Supabase, go to **Settings > API** and copy:
   - **Project URL** -> `SUPABASE_URL`
   - **anon public** key (under "Project API keys") -> `SUPABASE_KEY`

   Use the **anon public** key, NOT the secret/service_role key.

3. Edit `.env` with your credentials:
   ```env
   SUPABASE_URL=https://your-project.supabase.co
   SUPABASE_KEY=your-anon-key
   ```

### 4. Run the App

```bash
streamlit run src/app.py
```

The app will now connect to Supabase. Import a drivelog CSV to get started.

## Importing Data

### Drivelog CSV

Required columns:
- `Inverter` - Inverter name/number
- `UPN` - Unique pile number
- `Hammering_Status` - COMPLETED or INCOMPLETE
- `Hammering_Flag` - GOOD, BAD, or UNSET

### Nasku CSV

For updating pile data with drive times. Required columns:
- `name` - UPN (must match existing pile)
- `processedAt` - Timestamp
- `positioningTime` - Positioning time in milliseconds
- `hammeringTime` - Hammering time in milliseconds
- `hammeringStatus` - Status
- `hammeringFlag` - Flag

## Building an Executable

To create a standalone .exe (Windows) or app (Mac):

```bash
./scripts/build.sh
```

The executable will be at `dist/InverterTracker`.

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
src/
├── app.py                  # Streamlit entry point
├── data/
│   ├── models.py           # Pydantic data models
│   ├── repository.py       # Abstract repository interface
│   ├── supabase_repo.py    # Supabase implementation
│   └── memory_repo.py      # In-memory implementation (demo mode)
├── import_/
│   ├── csv_parser.py       # CSV parsing utilities
│   ├── drivelog_importer.py
│   └── nasku_importer.py
├── services/
│   ├── progress.py         # Progress & ETA calculations
│   ├── alerts.py           # Milestone alerts
│   └── import_service.py   # Import orchestration
└── ui/
    ├── dashboard.py        # Main grid view
    ├── expanded_card.py    # Detailed inverter view
    ├── import_panel.py     # CSV import UI
    └── settings.py         # Project settings
```
