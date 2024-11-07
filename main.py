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
from validationtesting.gui.views.solar_irradiation import solar_irradiation
from validationtesting.gui.views.battery_page import battery
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

def datetime_to_str(obj):
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj


def update_nested_settings(settings):
    for field in settings.model_fields:
        if hasattr(settings, field):
            value = getattr(settings, field)
            if isinstance(value, (int, float, str, bool)):
                if field in st.session_state:
                    setattr(settings, field, st.session_state[field])
            elif isinstance(value, datetime):
                if field in st.session_state:
                    setattr(settings, field, datetime_to_str(st.session_state[field]))
            elif isinstance(value, list):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    if isinstance(new_value, list):
                        setattr(settings, field, new_value)
                    else:
                        setattr(settings, field, [new_value])  # Convert single value to list
            elif isinstance(value, dict):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    if isinstance(new_value, dict):
                        current_dict = getattr(settings, field)
                        current_dict.update(new_value)
                        setattr(settings, field, current_dict)
            elif hasattr(value, 'model_fields'):
                if field == 'renewables_params':
                    setattr(settings, field, update_renewable_params(value, settings.resource_assessment.res_sources))
                elif field == 'generator_params':
                    setattr(settings, field, update_generator_params(value, settings.generator_params.gen_types))
                else:
                    setattr(settings, field, update_nested_settings(value))
    return settings

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
    st.session_state.solar_pv_model_output_scope = "Total"
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
    if st.sidebar.button("General", disabled=not buttons_enabled):
        st.session_state.page = "General"
    if st.sidebar.button("Component Selection", disabled=not buttons_enabled):
        st.session_state.page = "Component Selection"
    
    # Set default page to "Initial Page" if no page is set in session state
    if 'page' not in st.session_state:
        st.session_state.page = "Initial Page"

    # Dictionary to store frame references (views)
    pages = {
        "Initial Page": initial_page,
        "General": general,
        "Component Selection": component_selection,
        "Solar PV": solar_pv,
        "Solar Irradiation": solar_irradiation,
        "Upload Solar Model Output": lambda: upload_model_output('solar_pv'),
        "Battery": battery,
        "Upload Battery Model Output": lambda: upload_model_output('battery'),
        "Run Page": run_model,
        "Plots Page": generate_plots
    }

    # Display the selected frame
    pages[st.session_state.page]()

    # Set up expanders for each component (Solar PV, Wind, etc.)
    if "solar_pv" not in st.session_state:
        st.session_state.solar_pv = False

    if "wind" not in st.session_state:
        st.session_state.wind = False

    if "generator" not in st.session_state:
        st.session_state.generator = False

    if "battery" not in st.session_state:
        st.session_state.battery = False

    if st.session_state.solar_pv:
        with st.sidebar.expander("Solar PV", expanded=False):
            if st.button("Solar PV Specifications"):
                st.session_state.page = "Solar PV"
            if st.button("Solar Irradiation"):
                st.session_state.page = "Solar Irradiation"
            if st.button("Upload Solar PV Model Output"):
                st.session_state.page = "Upload Solar Model Output"
    if st.session_state.wind:
        with st.sidebar.expander("Wind Energy", expanded=False):
            if st.sidebar.button("Wind Energy"):
                st.session_state.page = "Wind"
    if st.session_state.generator:
        with st.sidebar.expander("Generator", expanded=False):
            if st.sidebar.button("Generator"):
                st.session_state.page = "Generator"
    if st.session_state.battery:
        with st.sidebar.expander("Battery", expanded=False):
            if st.button("Battery Specifications"):
                st.session_state.page = "Battery"
            if st.button("Upload Battery Model Output"):
                st.session_state.page = "Upload Battery Model Output"
            
    if st.sidebar.button("Run Page", disabled=not buttons_enabled):
        st.session_state.page = "Run Page"

    if st.sidebar.button("Plots Page", disabled=not buttons_enabled):
        st.session_state.page = "Plots Page"

    if st.sidebar.button("Save Settings to YAML"):
        if st.session_state.project_name:
            path_manager: PathManager = PathManager(st.session_state.project_name)
            save_settings_to_yaml(st.session_state, st.session_state.project_name, path_manager)

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