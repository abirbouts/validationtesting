"""
This module provides the main entry point for the MicroGridsPy Streamlit application.
It sets up the main layout of the application, including the navigation menu in the sidebar and the main content area.
The application manages session state to keep track of the current page being viewed and displays the appropriate page based on user interactions.
"""

import streamlit as st

import yaml
import datetime
from config.path_manager import PathManager
from validationtesting.gui.views.utils import render_footer
from validationtesting.gui.views.utils import render_top_left_icons
from validationtesting.gui.views.initial_page import initial_page
from validationtesting.gui.views.general_page import general
from validationtesting.gui.views.component_selection_page import component_selection
from validationtesting.gui.views.upload_model_output_page import upload_model_output
from validationtesting.gui.views.solar_pv_page import solar_pv
from validationtesting.gui.views.solar_data_page import irradiation_data
from validationtesting.gui.views.battery_page import battery
from validationtesting.gui.views.wind_page import wind
from validationtesting.gui.views.wind_data_page import wind_data
from validationtesting.gui.views.generator_page import generator
from validationtesting.gui.views.run_page import run_model
from validationtesting.gui.views.plots_page import generate_plots
from validationtesting.gui.views.utils import initialize_session_state
from validationtesting.utils.savetoyaml import save_to_yaml

st.set_page_config(
    page_title="ValidationTesting User Interface",
    page_icon=":bar_chart:",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': PathManager.DOCS_URL,
        'Report a bug': f'mailto:{PathManager.MAIL_CONTACT}',
        'About': (
            "To Be Filled"
        )
    }
)

def save_settings_to_yaml(session_state, project_name, path_manager):
    """
    Save the current session state settings to a YAML file.
    Args:
        session_state (dict): The current session state.
        project_name (str): The name of the current project.
        path_manager (object): An object to manage paths, e.g., PathManager.
    save_to_yaml()
    # Prepare the directory and file path for saving the YAML
    yaml_filepath = path_manager.PROJECTS_FOLDER_PATH / project_name / f"{project_name}.yaml"
    yaml_filepath.parent.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist
    
    # Convert the session state to a dictionary that can be serialized into YAML
    session_state_dict = {key: value for key, value in session_state.items()}

    # Write the session state dictionary to a YAML file
    with open(yaml_filepath, 'w') as yaml_file:
        yaml.dump(session_state_dict, yaml_file)

    st.toast(f"Settings saved successfully to {yaml_filepath}")
    """
    save_to_yaml()


def main() -> None:
    """
    Main entry point for the Streamlit application.

    This function sets up the main layout of the application, including the navigation menu
    in the sidebar and the main content area. It manages the session state to keep track of 
    the current page being viewed and displays the appropriate page based on user interactions.
    """
    # Ensure that 'new_project_completed' flag and 'project_name' are in session state
    if 'new_project_completed' not in st.session_state:
        st.session_state.new_project_completed = False

    if 'project_name' not in st.session_state:
        st.session_state.project_name = None  # No project selected yet

    # Sidebar for navigation
    st.sidebar.title("Navigation Menu")

    # If a project is selected, display its name in the sidebar
    if st.session_state.project_name:
        st.sidebar.markdown(f"### Selected Project: **{st.session_state.project_name}**")
    else:
        st.sidebar.markdown("### No Project Selected")

    # Determine if buttons should be enabled based on project selection
    buttons_enabled = st.session_state.new_project_completed

    # Navigation buttons
    if st.sidebar.button("Initial Page", disabled=not buttons_enabled):
        st.session_state.page = "Initial Page"
        st.rerun()
    if st.sidebar.button("General", disabled=not buttons_enabled):
        st.session_state.page = "General"
        st.rerun()
    if st.sidebar.button("Component Selection", disabled=not buttons_enabled):
        st.session_state.page = "Component Selection"
        st.rerun()
    
    # Set default page to "Initial Page" if no page is set in session state
    if 'page' not in st.session_state:
        st.session_state.page = "Initial Page"
        st.rerun()

    # Dictionary to store frame references (views)
    pages = {
        "Initial Page": initial_page,
        "General": general,
        "Component Selection": component_selection,
        "Solar PV": solar_pv,
        "Irradiation Data": irradiation_data,
        "Upload Solar Model Output": lambda: upload_model_output('solar_pv'),
        "Battery": battery,
        "Upload Battery Model Output": lambda: upload_model_output('battery'),
        "Wind": wind,
        "Wind Data": wind_data,
        "Upload Wind Model Output": lambda: upload_model_output('wind'),
        "Generator": generator,
        "Upload Generator Model Output": lambda: upload_model_output('generator'),
        "Run Page": run_model,
        "Plots Page": generate_plots
    }

    # Display the selected frame
    pages[st.session_state.page]()

    if st.session_state.page != "Initial Page": 
        if st.session_state.solar_pv:
            with st.sidebar.expander("Solar PV", expanded=False):
                if st.button("Solar PV Specifications"):
                    st.session_state.page = "Solar PV"
                    st.rerun()
                if st.button("Upload Irradiation Data"):
                    st.session_state.page = "Irradiation Data"
                    st.rerun()
                if st.button("Upload Solar PV Model Output"):
                    st.session_state.page = "Upload Solar Model Output"
                    st.rerun()
        if st.session_state.wind:
            with st.sidebar.expander("Wind Energy", expanded=False):
                if st.button("Wind Specifications"):
                    st.session_state.page = "Wind"
                    st.rerun()
                if st.button("Upload Wind Data"):
                    st.session_state.page = "Wind Data"
                    st.rerun()
                if st.button("Upload Wind Model Output"):
                    st.session_state.page = "Upload Wind Model Output" 
                    st.rerun()
        if st.session_state.generator:
            with st.sidebar.expander("Generator", expanded=False):
                if st.button("Generator Specifications"):
                    st.session_state.page = "Generator"
                    st.rerun()
                if st.button("Upload Generator Model Output"):
                    st.session_state.page = "Upload Generator Model Output" 
                    st.rerun()

        if st.session_state.battery:
            with st.sidebar.expander("Battery", expanded=False):
                if st.button("Battery Specifications"):
                    st.session_state.page = "Battery"
                    #st.rerun()
                if st.button("Upload Battery Model Output"):
                    st.session_state.page = "Upload Battery Model Output"
                    st.rerun()
            
    if st.sidebar.button("Run Page", disabled=not buttons_enabled):
        st.session_state.page = "Run Page"
        st.rerun()

    if st.sidebar.button("Plots Page", disabled=not buttons_enabled):
        st.session_state.page = "Plots Page"
        st.rerun()

    if st.sidebar.button("Save Settings to YAML"):
        if st.session_state.project_name:
            path_manager: PathManager = PathManager(st.session_state.project_name)
            save_settings_to_yaml(st.session_state, st.session_state.project_name, path_manager)
    if st.session_state.page != "Initial Page":
        save_to_yaml()

    # Render the footer and icons
    render_footer()
    #render_top_left_icons()


def check_new_project_completion() -> bool:
    """
    Check if the New Project page has been completed.

    Returns:
        bool: True if the New Project page is completed, False otherwise.
    """
    return 'project_name' in st.session_state and 'default_values' in st.session_state


if __name__ == "__main__":
    main()