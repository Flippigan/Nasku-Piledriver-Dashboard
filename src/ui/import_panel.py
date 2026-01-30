import streamlit as st

from src.ui.state import get_repository
from src.services.import_service import ImportService
from src.import_.csv_parser import MissingColumnsError
from src.import_.nasku_importer import UnmatchedUpnError


def render_import_panel():
    repo = get_repository()
    project = repo.get_project()

    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.show_import = False
        st.rerun()

    st.title("Import CSV Data")

    import_service = ImportService(repo)

    # Drivelog import (only if no project exists)
    if not project:
        st.subheader("Step 1: Import Drivelog")
        st.info("Import a drivelog CSV to set up your project with inverters and piles.")

        project_name = st.text_input("Project Name", value="Solar Site")
        drivelog_file = st.file_uploader(
            "Upload Drivelog CSV",
            type=["csv"],
            key="drivelog",
        )

        if drivelog_file and project_name:
            if st.button("Import Drivelog"):
                try:
                    with st.spinner("Importing drivelog..."):
                        project = import_service.import_drivelog(
                            drivelog_file,
                            project_name=project_name,
                        )
                    st.success(f"Project '{project.name}' created successfully!")
                    st.session_state.show_import = False
                    st.rerun()
                except MissingColumnsError as e:
                    st.error(f"Missing required columns: {', '.join(e.missing)}")
                except Exception as e:
                    st.error(f"Import failed: {str(e)}")

    else:
        st.subheader("Import Nasku Progress Update")
        st.info(f"Update pile status for project: **{project.name}**")

        nasku_file = st.file_uploader(
            "Upload Nasku CSV",
            type=["csv"],
            key="nasku",
        )

        if nasku_file:
            if st.button("Import Nasku"):
                try:
                    with st.spinner("Importing nasku data..."):
                        import_service.import_nasku(nasku_file)
                    st.success("Pile status updated successfully!")
                    st.session_state.show_import = False
                    st.rerun()
                except MissingColumnsError as e:
                    st.error(f"Missing required columns: {', '.join(e.missing)}")
                except UnmatchedUpnError as e:
                    st.error(f"Import rejected. UPNs not found in drivelog: {', '.join(sorted(e.unmatched_upns)[:10])}")
                    if len(e.unmatched_upns) > 10:
                        st.error(f"... and {len(e.unmatched_upns) - 10} more")
                except Exception as e:
                    st.error(f"Import failed: {str(e)}")

        st.divider()

        # Option to reset project
        with st.expander("Advanced: Reset Project"):
            st.warning("This will delete all data and allow re-importing a drivelog.")
            if st.button("Reset Project", type="secondary"):
                # TODO: Implement project reset
                st.info("Project reset not yet implemented")
