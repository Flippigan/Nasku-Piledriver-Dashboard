import streamlit as st
from datetime import date
from uuid import UUID

from src.ui.state import get_repository
from src.services.progress import calculate_progress, calculate_eta
from src.services.alerts import get_pending_alerts


def render_expanded_card(inverter_id: str):
    repo = get_repository()
    project = repo.get_project()
    inverter = repo.get_inverter(UUID(inverter_id))

    if not inverter or not project:
        st.error("Inverter not found")
        return

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.selected_inverter_id = None
        st.rerun()

    st.title(inverter.name)

    # Get data
    piles = repo.get_piles_for_inverter(inverter.id)
    steps = repo.get_workflow_steps(inverter.id)
    alerts = repo.get_alerts_for_inverter(inverter.id)

    progress = calculate_progress(inverter, piles)
    eta = calculate_eta(inverter, piles, project.default_pile_rate)
    pending_alerts = get_pending_alerts(alerts)

    # Progress summary
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Progress", f"{progress.percentage:.1f}%")
    with col2:
        st.metric("Piles", f"{progress.installed_count}/{progress.total_count}")
    with col3:
        if eta.estimated_completion:
            st.metric("ETA", eta.estimated_completion.strftime("%b %d, %Y"))
        else:
            st.metric("ETA", "Complete" if progress.percentage == 100 else "N/A")

    st.divider()

    # Alerts section
    if pending_alerts:
        st.subheader("Pending Alerts")
        for alert in pending_alerts:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.warning(f"Milestone reached: {alert.threshold_value}%")
            with col2:
                if st.button("Acknowledge", key=f"ack_{alert.id}"):
                    repo.acknowledge_alert(alert.id)
                    st.rerun()
        st.divider()

    # Workflow checklist
    st.subheader("Workflow Steps")

    # Get list of engineers for dropdown
    engineers = ["", "Sarah", "John", "Mike", "Lisa"]  # TODO: Load from project settings

    for step in sorted(steps, key=lambda s: s.step_order):
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([0.5, 2, 1.5, 1.5])

            with col1:
                new_complete = st.checkbox(
                    "",
                    value=step.is_complete,
                    key=f"step_{step.id}",
                    label_visibility="collapsed",
                )
                if new_complete != step.is_complete:
                    step.is_complete = new_complete
                    step.completed_at = date.today() if new_complete else None
                    repo.update_workflow_step(step)
                    st.rerun()

            with col2:
                st.markdown(f"**{step.step_order}. {step.step_name}**")

            with col3:
                new_due = st.date_input(
                    "Due",
                    value=step.due_date,
                    key=f"due_{step.id}",
                    label_visibility="collapsed",
                )
                if new_due != step.due_date:
                    step.due_date = new_due
                    repo.update_workflow_step(step)

            with col4:
                current_idx = engineers.index(step.assigned_engineer) if step.assigned_engineer in engineers else 0
                new_engineer = st.selectbox(
                    "Engineer",
                    options=engineers,
                    index=current_idx,
                    key=f"eng_{step.id}",
                    label_visibility="collapsed",
                )
                if new_engineer != step.assigned_engineer:
                    step.assigned_engineer = new_engineer or None
                    repo.update_workflow_step(step)

    st.divider()

    # Inverter settings
    st.subheader("Inverter Settings")

    col1, col2 = st.columns(2)

    with col1:
        new_threshold = st.number_input(
            "First Scan Threshold Override (%)",
            min_value=0,
            max_value=100,
            value=inverter.scan_threshold_override or project.default_scan_threshold_pct,
            help=f"Project default: {project.default_scan_threshold_pct}%",
        )
        use_override = st.checkbox(
            "Use custom threshold",
            value=inverter.scan_threshold_override is not None,
        )

        if use_override and new_threshold != inverter.scan_threshold_override:
            inverter.scan_threshold_override = new_threshold
            repo.update_inverter(inverter)
        elif not use_override and inverter.scan_threshold_override is not None:
            inverter.scan_threshold_override = None
            repo.update_inverter(inverter)

    with col2:
        st.text("Milestone Thresholds")
        thresholds_str = st.text_input(
            "Thresholds (comma-separated)",
            value=", ".join(str(t) for t in inverter.milestone_thresholds),
            label_visibility="collapsed",
        )
        try:
            new_thresholds = [int(t.strip()) for t in thresholds_str.split(",")]
            if new_thresholds != inverter.milestone_thresholds:
                inverter.milestone_thresholds = new_thresholds
                repo.update_inverter(inverter)
        except ValueError:
            st.error("Invalid thresholds format")
