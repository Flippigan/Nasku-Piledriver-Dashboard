import streamlit as st
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from uuid import UUID

from src.data.models import Inverter, WorkflowStep
from src.services.progress import calculate_progress
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


# Status color mapping to CSS colors
STATUS_COLORS = {
    "green": "#22c55e",
    "yellow": "#eab308",
    "red": "#ef4444",
}

# Darker shades for gradient effect
STATUS_COLORS_DARK = {
    "green": "#15803d",
    "yellow": "#a16207",
    "red": "#b91c1c",
}


def render_compact_card(
    inverter_id: str,
    inverter_name: str,
    percentage: float,
    status_color: str,
    step_name: str,
    has_alerts: bool,
) -> bool:
    """Render a compact inverter card. Returns True if clicked."""
    fill_color = STATUS_COLORS.get(status_color, STATUS_COLORS["green"])
    fill_color_dark = STATUS_COLORS_DARK.get(status_color, STATUS_COLORS_DARK["green"])
    pct = min(100, max(0, percentage))

    # Alert indicator HTML
    alert_badge = ""
    if has_alerts:
        alert_badge = f"""
            <div style="
                position: absolute;
                top: 6px;
                right: 6px;
                width: 8px;
                height: 8px;
                background: #ef4444;
                border-radius: 50%;
                box-shadow: 0 0 6px #ef4444;
            "></div>
        """

    # Render card HTML
    card_html = f"""
        <div style="
            position: relative;
            width: 100%;
            height: 160px;
            background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
            border: 1px solid #334155;
            border-radius: 8px;
            padding: 10px 8px;
            display: flex;
            flex-direction: column;
            align-items: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.05);
            margin-bottom: 4px;
        ">
            {alert_badge}

            <!-- Inverter Name -->
            <div style="
                font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 11px;
                font-weight: 600;
                color: #e2e8f0;
                text-transform: uppercase;
                letter-spacing: 0.5px;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                width: 100%;
                text-align: center;
                margin-bottom: 6px;
            " title="{inverter_name}">{inverter_name}</div>

            <!-- Progress Bar Container -->
            <div style="
                flex: 1;
                width: 28px;
                background: #0f172a;
                border-radius: 4px;
                position: relative;
                overflow: hidden;
                border: 1px solid #1e293b;
                box-shadow: inset 0 2px 4px rgba(0,0,0,0.5);
            ">
                <!-- Grid lines for industrial feel -->
                <div style="
                    position: absolute;
                    top: 0;
                    left: 0;
                    right: 0;
                    bottom: 0;
                    background: repeating-linear-gradient(
                        0deg,
                        transparent,
                        transparent 9px,
                        rgba(51, 65, 85, 0.3) 9px,
                        rgba(51, 65, 85, 0.3) 10px
                    );
                    pointer-events: none;
                "></div>

                <!-- Progress Fill -->
                <div style="
                    position: absolute;
                    bottom: 0;
                    left: 0;
                    right: 0;
                    height: {pct}%;
                    background: linear-gradient(180deg, {fill_color} 0%, {fill_color_dark} 100%);
                    border-radius: 3px;
                    box-shadow: 0 0 10px {fill_color}40, inset 0 1px 0 rgba(255,255,255,0.2);
                "></div>

                <!-- 50% marker -->
                <div style="
                    position: absolute;
                    top: 50%;
                    left: 0;
                    right: 0;
                    height: 1px;
                    background: rgba(148, 163, 184, 0.3);
                "></div>
            </div>

            <!-- Percentage -->
            <div style="
                font-family: 'SF Mono', 'Fira Code', 'Consolas', monospace;
                font-size: 14px;
                font-weight: 700;
                color: {fill_color};
                margin-top: 6px;
                text-shadow: 0 0 10px {fill_color}40;
            ">{pct:.0f}%</div>

            <!-- Step Name -->
            <div style="
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                font-size: 9px;
                color: #94a3b8;
                text-align: center;
                white-space: nowrap;
                overflow: hidden;
                text-overflow: ellipsis;
                width: 100%;
                margin-top: 2px;
            " title="{step_name}">{step_name}</div>
        </div>
    """

    st.html(card_html)

    # Add a small clickable button below the card
    return st.button(
        "View Details",
        key=f"select_{inverter_id}",
        use_container_width=True,
        type="secondary",
    )


def _fetch_card_data_for_inverter(inverter_id: UUID, repo) -> dict:
    """Fetch all data needed for a single inverter card."""
    inverter = repo.get_inverter(inverter_id)
    if not inverter:
        return None

    piles = repo.get_piles_for_inverter(inverter_id)
    steps = repo.get_workflow_steps(inverter_id)
    alerts = repo.get_alerts_for_inverter(inverter_id)

    progress = calculate_progress(inverter, piles)
    current_step = get_current_step(steps)
    pending = get_pending_alerts(alerts)

    days_remaining = days_until_due(current_step)
    status_color = get_status_color(current_step, days_remaining)
    step_name = current_step.step_name if current_step else "Complete"

    return {
        "inverter_id": str(inverter_id),
        "name": inverter.name,
        "percentage": progress.percentage,
        "status_color": status_color,
        "step_name": step_name,
        "has_alerts": len(pending) > 0,
    }


def _fetch_cards_sequential(_repo, inverter_ids: tuple[UUID, ...]) -> list[dict]:
    """Fetch card data sequentially (fallback for connection errors)."""
    cards = []
    for inv_id in inverter_ids:
        card = _fetch_card_data_for_inverter(inv_id, _repo)
        if card:
            cards.append(card)
    return cards


def _fetch_cards_parallel(_repo, inverter_ids: tuple[UUID, ...]) -> list[dict]:
    """Fetch card data in parallel using ThreadPoolExecutor."""
    cards = []
    # Use 4 workers to stay well under HTTP/2 stream limits (typically 100-250)
    with ThreadPoolExecutor(max_workers=4) as executor:
        futures = {
            executor.submit(_fetch_card_data_for_inverter, inv_id, _repo): inv_id
            for inv_id in inverter_ids
        }
        for future in as_completed(futures):
            card = future.result()
            if card:
                cards.append(card)
    return cards


def _fetch_all_cards_data(repo, inverter_ids: tuple[UUID, ...]) -> list[dict]:
    """
    Fetch dashboard card data for all inverters.

    Uses ThreadPoolExecutor to fetch data in parallel,
    with fallback to sequential fetching if HTTP/2 connection limits are hit.
    """
    try:
        cards = _fetch_cards_parallel(repo, inverter_ids)
    except Exception:
        # HTTP/2 connection errors - fall back to sequential
        cards = _fetch_cards_sequential(repo, inverter_ids)

    return sorted(cards, key=lambda x: x["name"])


def get_cards_data(repo, inverter_ids: tuple[UUID, ...]) -> list[dict]:
    """Get cached cards data from session_state, fetching if not present."""
    if "cards_data" not in st.session_state:
        with st.spinner("Loading inverter data..."):
            st.session_state["cards_data"] = _fetch_all_cards_data(repo, inverter_ids)
    return st.session_state["cards_data"]


def refresh_cards_data(repo, inverter_ids: tuple[UUID, ...]) -> list[dict]:
    """Force refresh cards data from the database."""
    st.session_state["cards_data"] = _fetch_all_cards_data(repo, inverter_ids)
    return st.session_state["cards_data"]


def clear_dashboard_cache():
    """Clear the cached dashboard card data. Call after data changes (imports, updates)."""
    if "cards_data" in st.session_state:
        del st.session_state["cards_data"]


def inject_compact_card_styles():
    """Inject global CSS for compact card styling."""
    st.html("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Fira+Code:wght@400;600;700&display=swap');

            /* Make buttons smaller and more compact */
            div[data-testid="column"] button[kind="secondary"] {
                font-size: 10px !important;
                padding: 2px 8px !important;
                min-height: 24px !important;
                height: 24px !important;
                background: #1e293b !important;
                border: 1px solid #334155 !important;
                color: #94a3b8 !important;
            }

            div[data-testid="column"] button[kind="secondary"]:hover {
                background: #334155 !important;
                border-color: #475569 !important;
                color: #e2e8f0 !important;
            }

            /* Compact grid container */
            .compact-grid-container {
                background: linear-gradient(180deg, #020617 0%, #0f172a 100%);
                border-radius: 12px;
                border: 1px solid #1e293b;
                padding: 16px;
                margin-top: 8px;
            }
        </style>
    """)


def render_dashboard():
    repo = get_repository()

    # Inject compact card styles
    inject_compact_card_styles()

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
    col1, col2, col3, col4, col5 = st.columns([1, 1, 1, 1, 2])
    with col1:
        if st.button("Import CSV"):
            st.session_state.show_import = True
    with col2:
        if st.button("Settings"):
            st.session_state.show_settings = True
    with col3:
        if st.button("🔄 Refresh"):
            clear_dashboard_cache()
            st.rerun()
    with col4:
        if st.button("Reset Project"):
            repo.reset_all()
            clear_dashboard_cache()
            # Clear session state
            for key in list(st.session_state.keys()):
                if key not in ["using_demo_mode"]:
                    del st.session_state[key]
            st.rerun()

    st.divider()

    # Get all inverters
    inverters = repo.get_inverters(project.id)

    if not inverters:
        st.info("No inverters found. Import a drivelog to add inverters.")
        return

    # Use session_state cached card data - click Refresh to update
    inverter_ids = tuple(inv.id for inv in inverters)
    cards_data = get_cards_data(repo, inverter_ids)

    # Open grid container
    st.html('<div class="compact-grid-container">')

    # Render grid of compact cards (8 columns for dense layout)
    num_cols = 8
    cols = st.columns(num_cols, gap="small")

    for i, card in enumerate(cards_data):
        with cols[i % num_cols]:
            clicked = render_compact_card(
                inverter_id=card["inverter_id"],
                inverter_name=card["name"],
                percentage=card["percentage"],
                status_color=card["status_color"],
                step_name=card["step_name"],
                has_alerts=card["has_alerts"],
            )
            if clicked:
                st.session_state.selected_inverter_id = card["inverter_id"]
                st.rerun()

    # Close grid container
    st.html('</div>')
