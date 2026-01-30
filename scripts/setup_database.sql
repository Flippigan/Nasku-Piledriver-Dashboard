-- Inverter Tracker Dashboard - Supabase Schema
-- Run this in the Supabase SQL Editor

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Projects table
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    default_scan_threshold_pct INTEGER NOT NULL DEFAULT 90,
    default_pile_rate INTEGER NOT NULL DEFAULT 50,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Inverters table
CREATE TABLE inverters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    project_id UUID NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    total_piles INTEGER NOT NULL,
    scan_threshold_override INTEGER,
    milestone_thresholds JSONB DEFAULT '[50, 75, 90]',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_inverters_project ON inverters(project_id);

-- Piles table
CREATE TABLE piles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inverter_id UUID NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    upn TEXT NOT NULL,
    hammering_status TEXT,
    hammering_flag TEXT,
    hammering_time_sec DOUBLE PRECISION,
    positioning_time_sec DOUBLE PRECISION,
    driven_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(inverter_id, upn)
);

CREATE INDEX idx_piles_inverter ON piles(inverter_id);
CREATE INDEX idx_piles_upn ON piles(upn);

-- Workflow steps table
CREATE TABLE workflow_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inverter_id UUID NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    step_name TEXT NOT NULL,
    step_order INTEGER NOT NULL,
    is_complete BOOLEAN DEFAULT FALSE,
    completed_at TIMESTAMP WITH TIME ZONE,
    due_date DATE,
    assigned_engineer TEXT
);

CREATE INDEX idx_workflow_inverter ON workflow_steps(inverter_id);

-- Alerts table
CREATE TABLE alerts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    inverter_id UUID NOT NULL REFERENCES inverters(id) ON DELETE CASCADE,
    alert_type TEXT NOT NULL,
    threshold_value INTEGER NOT NULL,
    acknowledged BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_alerts_inverter ON alerts(inverter_id);
CREATE INDEX idx_alerts_unacknowledged ON alerts(inverter_id) WHERE acknowledged = FALSE;

-- Row Level Security (disabled for v1 - no auth)
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
ALTER TABLE inverters ENABLE ROW LEVEL SECURITY;
ALTER TABLE piles ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE alerts ENABLE ROW LEVEL SECURITY;

-- Allow all operations for anon key (v1 - no auth)
CREATE POLICY "Allow all" ON projects FOR ALL USING (true);
CREATE POLICY "Allow all" ON inverters FOR ALL USING (true);
CREATE POLICY "Allow all" ON piles FOR ALL USING (true);
CREATE POLICY "Allow all" ON workflow_steps FOR ALL USING (true);
CREATE POLICY "Allow all" ON alerts FOR ALL USING (true);
