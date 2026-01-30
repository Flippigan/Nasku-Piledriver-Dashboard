import sys
from pathlib import Path

# Add project root to path for 'src' package imports
# Works for both local development and PyInstaller builds
_project_root = Path(__file__).parent.parent
if str(_project_root) not in sys.path:
    sys.path.insert(0, str(_project_root))

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from src.ui.state import init_session_state
from src.ui.dashboard import render_dashboard


st.set_page_config(
    page_title="Inverter Tracker",
    page_icon="⚡",
    layout="wide",
)


def main():
    init_session_state()

    # Check if we should show expanded card
    if st.session_state.get("selected_inverter_id"):
        from src.ui.expanded_card import render_expanded_card
        render_expanded_card(st.session_state.selected_inverter_id)
    elif st.session_state.get("show_settings"):
        from src.ui.settings import render_settings
        render_settings()
    elif st.session_state.get("show_import"):
        from src.ui.import_panel import render_import_panel
        render_import_panel()
    else:
        render_dashboard()


if __name__ == "__main__":
    main()
