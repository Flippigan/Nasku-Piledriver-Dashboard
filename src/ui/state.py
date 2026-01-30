import streamlit as st
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.data.repository import Repository


def init_session_state():
    if "selected_inverter_id" not in st.session_state:
        st.session_state.selected_inverter_id = None
    if "show_settings" not in st.session_state:
        st.session_state.show_settings = False


def get_repository() -> "Repository":
    from src.data.supabase_repo import SupabaseRepository

    if "repository" not in st.session_state:
        st.session_state.repository = SupabaseRepository()
    return st.session_state.repository
