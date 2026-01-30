import streamlit as st
from datetime import date, timedelta

from src.data.models import Inverter, WorkflowStep
from src.services.progress import calculate_progress, calculate_eta, ProgressStats, EtaStats
from src.services.alerts import get_pending_alerts
from src.ui.state import get_repository, is_demo_mode


def get_status_color(step: WorkflowStep | None, days_remaining: int | None) -> str:
    if step is None or step.due_date is None:
        return "green"

    if days_remaining is None:
        return "green"
    elif days_remaining < 2:
        return "red"
    elif days_remaining <= 6:
        return "yellow"
    else:
        return "green"


def get_current_step(steps: list[WorkflowStep]) -> WorkflowStep | None:
    for step in sorted(steps, key=lambda s: s.step_order):
        if not step.is_complete:
            return step
    return None


def days_until_due(step: WorkflowStep | None) -> int | None:
    if step is None or step.due_date is None:
        return None
    return (step.due_date - date.today()).days


def render_inverter_card(
    inverter: Inverter,
    progress: ProgressStats,
    eta: EtaStats,
    current_step: WorkflowStep | None,
    has_pending_alerts: bool,
):
    days_remaining = days_until_due(current_step)
    color = get_status_color(current_step, days_remaining)

    color_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}[color]

    with st.container(border=True):
        col1, col2 = st.columns([3, 1])

        with col1:
            st.subheader(inverter.name)

        with col2:
            if has_pending_alerts:
                st.markdown("**[!]**")

        # Progress bar
        st.progress(progress.percentage / 100)
        st.caption(f"{progress.percentage:.0f}% ({progress.installed_count}/{progress.total_count})")

        # Current step
        step_name = current_step.step_name if current_step else "Complete"
        st.markdown(f"**{step_name}**")

        # Status and engineer
        if current_step:
            due_text = ""
            if days_remaining is not None:
                if days_remaining < 0:
                    due_text = f"Overdue by {abs(days_remaining)}d"
                elif days_remaining == 0:
                    due_text = "Due today"
                else:
                    due_text = f"Due: {days_remaining}d"

            engineer = current_step.assigned_engineer or "--"
            st.caption(f"{color_emoji} {due_text} | @{engineer}")

        # ETA
        if eta.estimated_completion:
            eta_str = eta.estimated_completion.strftime("%b %d")
            rate_note = " (default)" if eta.is_using_default_rate else ""
            st.caption(f"ETA: {eta_str} | {eta.piles_per_day:.0f} piles/d{rate_note}")

        # Click to expand
        if st.button("Details", key=f"expand_{inverter.id}"):
            st.session_state.selected_inverter_id = str(inverter.id)
            st.rerun()


def render_dashboard():
    repo = get_repository()

    # Show demo mode banner
    if is_demo_mode():
        st.info(
            "**Demo Mode** - Using sample data. "
            "Configure SUPABASE_URL and SUPABASE_KEY in .env to connect to a database."
        )

    project = repo.get_project()

    if not project:
        st.warning("No project loaded. Please import a drivelog CSV to get started.")
        if st.button("Import Drivelog"):
            st.session_state.show_import = True
            st.rerun()
        return

    st.title(f"Project: {project.name}")

    # Header buttons
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        if st.button("Import CSV"):
            st.session_state.show_import = True
    with col2:
        if st.button("Settings"):
            st.session_state.show_settings = True

    st.divider()

    # Get all inverters
    inverters = repo.get_inverters(project.id)

    if not inverters:
        st.info("No inverters found. Import a drivelog to add inverters.")
        return

    # Render grid of cards (3 columns)
    cols = st.columns(3)

    for i, inverter in enumerate(sorted(inverters, key=lambda x: x.name)):
        with cols[i % 3]:
            # Get data for this inverter
            piles = repo.get_piles_for_inverter(inverter.id)
            steps = repo.get_workflow_steps(inverter.id)
            alerts = repo.get_alerts_for_inverter(inverter.id)

            progress = calculate_progress(inverter, piles)
            eta = calculate_eta(inverter, piles, project.default_pile_rate)
            current_step = get_current_step(steps)
            pending = get_pending_alerts(alerts)

            render_inverter_card(
                inverter=inverter,
                progress=progress,
                eta=eta,
                current_step=current_step,
                has_pending_alerts=len(pending) > 0,
            )
