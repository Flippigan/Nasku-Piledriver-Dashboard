import streamlit as st

from src.ui.state import get_repository


def render_settings():
    repo = get_repository()
    project = repo.get_project()

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.show_settings = False
        st.rerun()

    st.title("Project Settings")

    if not project:
        st.warning("No project loaded.")
        return

    with st.form("project_settings"):
        st.subheader("General")

        project_name = st.text_input("Project Name", value=project.name)

        st.subheader("Defaults")

        col1, col2 = st.columns(2)

        with col1:
            scan_threshold = st.number_input(
                "Default First Scan Threshold (%)",
                min_value=1,
                max_value=100,
                value=project.default_scan_threshold_pct,
                help="Percentage of piles installed before first scan is triggered",
            )

        with col2:
            pile_rate = st.number_input(
                "Default Pile Rate (piles/day)",
                min_value=1,
                max_value=500,
                value=project.default_pile_rate,
                help="Used for ETA calculation on unstarted inverters",
            )

        st.subheader("Status Color Thresholds")
        st.caption("Days remaining until due date")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.success("Green: 7+ days")
        with col2:
            st.warning("Yellow: 2-6 days")
        with col3:
            st.error("Red: <2 days or overdue")

        st.info("Color thresholds are currently fixed. Future versions may allow customization.")

        st.subheader("Engineer List")
        engineers_default = "Sarah, John, Mike, Lisa"
        engineers = st.text_input(
            "Engineers (comma-separated)",
            value=engineers_default,
            help="Names available in engineer assignment dropdowns",
        )

        submitted = st.form_submit_button("Save Settings")

        if submitted:
            project.name = project_name
            project.default_scan_threshold_pct = scan_threshold
            project.default_pile_rate = pile_rate
            repo.update_project(project)
            st.success("Settings saved!")
            st.rerun()
