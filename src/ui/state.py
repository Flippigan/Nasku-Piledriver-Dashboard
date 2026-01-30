import os
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
    if "repository" not in st.session_state:
        # Check if Supabase is configured
        supabase_url = os.getenv("SUPABASE_URL")
        supabase_key = os.getenv("SUPABASE_KEY")

        if supabase_url and supabase_key:
            from src.data.supabase_repo import SupabaseRepository
            st.session_state.repository = SupabaseRepository()
            st.session_state.using_demo_mode = False
        else:
            from src.data.memory_repo import MemoryRepository
            st.session_state.repository = MemoryRepository()
            st.session_state.using_demo_mode = True

    return st.session_state.repository


def is_demo_mode() -> bool:
    """Check if running in demo mode (no Supabase)."""
    return st.session_state.get("using_demo_mode", True)
