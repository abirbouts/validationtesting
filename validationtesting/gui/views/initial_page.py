"""
This module contains the Streamlit page for creating a new project or loading an existing configuration file.
"""

import streamlit as st
from pathlib import Path
from config.path_manager import PathManager
from validationtesting.validation.parameters import ProjectParameters
from validationtesting.gui.views.utils import initialize_session_state

def create_new_project(project_name: str) -> bool:
    """Create a new project with the given name and description."""
    path_manager = PathManager(project_name)
    project_folder = path_manager.PROJECTS_FOLDER_PATH / project_name
    inputs_folder = project_folder / "inputs"
    results_folder = project_folder / "results"
    plots_folder = results_folder / "plots"
    
    if project_folder.exists():
        st.error(f"A project with the name '{project_name}' already exists. Please choose a different name.")
        return False
    
    project_folder.mkdir(parents=True, exist_ok=True)
    inputs_folder.mkdir(parents=True, exist_ok=True)
    results_folder.mkdir(parents=True, exist_ok=True)
    plots_folder.mkdir(parents=True, exist_ok=True)
    
    # Instantiate the default values and save in session state
    st.session_state.path_manager = path_manager
    st.session_state.default_values = ProjectParameters.instantiate_from_yaml(PathManager.DEFAULT_YAML_FILE_PATH)
    initialize_session_state(st.session_state.default_values, 'general_info')
    initialize_session_state(st.session_state.default_values, 'component_selection')
    initialize_session_state(st.session_state.default_values, 'upload_model_parameters')
    initialize_session_state(st.session_state.default_values, 'solar_pv_parameters')
    initialize_session_state(st.session_state.default_values, 'solar_irradiation_parameters')
    initialize_session_state(st.session_state.default_values, 'battery_parameters')
    initialize_session_state(st.session_state.default_values, 'wind_parameters')
    initialize_session_state(st.session_state.default_values, 'generator_parameters')
    initialize_session_state(st.session_state.default_values, 'generate_plots')
    
    # Create a YAML file for the project with default values
    yaml_file_path = project_folder / f"{project_name}.yaml"
    st.session_state.default_values.save_to_yaml(yaml_file_path)
    
    return True

def load_existing_project(uploaded_file) -> bool:
    """
    Load an existing project configuration file.
    This function takes an uploaded file, extracts the project name, and sets up the necessary
    folder structure for the project if it doesn't already exist. It then saves the uploaded
    file to the project folder and initializes various session state parameters from the 
    configuration file.
    """
    try:
        project_name = Path(uploaded_file.name).stem
        path_manager = PathManager(project_name)
        project_folder = path_manager.PROJECTS_FOLDER_PATH / project_name
        
        if not project_folder.exists():
            # Create subfolders for inputs
            project_folder.mkdir(parents=True, exist_ok=True)
            (project_folder / "demand").mkdir(exist_ok=True)
            (project_folder / "resource").mkdir(exist_ok=True)
            (project_folder / "technology characterization").mkdir(exist_ok=True)
            (project_folder / "grid").mkdir(exist_ok=True)
        
        # Save the uploaded file to the project folder
        yaml_file_path = project_folder / f"{project_name}.yaml"
        with open(yaml_file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        
        st.session_state.project_name = project_name
        st.session_state.path_manager = path_manager
        st.session_state.default_values = ProjectParameters.instantiate_from_yaml(yaml_file_path)
        initialize_session_state(st.session_state.default_values, 'general_info')
        initialize_session_state(st.session_state.default_values, 'component_selection')
        initialize_session_state(st.session_state.default_values, 'upload_model_parameters')
        initialize_session_state(st.session_state.default_values, 'solar_pv_parameters')
        initialize_session_state(st.session_state.default_values, 'solar_irradiation_parameters')
        initialize_session_state(st.session_state.default_values, 'battery_parameters')
        initialize_session_state(st.session_state.default_values, 'wind_parameters')
        initialize_session_state(st.session_state.default_values, 'generator_parameters')
        initialize_session_state(st.session_state.default_values, 'generate_plots')
        return True
    
    except Exception as e:
        st.error(f"Failed to load configuration: {e}")
        return False

def initial_page() -> None:
    """Streamlit page for creating a new project or loading existing configuration files."""
    st.title("Validation Testing")

    # Check if a project is already selected
    if 'project_name' in st.session_state and st.session_state.project_name:
        # Show the selected project name
        st.success(f"Project '{st.session_state.project_name}' is currently selected.")
        
        # Button to create a new project or select another one
        if st.button("Create or Select Another Project"):
            # Reset project selection and go back to initial state
            for key in st.session_state.keys():
                del st.session_state[key]

    else:
        # No project selected, show the create new project section
        st.subheader("Create a New Project")
        st.write("Enter the details below to create a new project.")
        
        # Project name input
        project_name = st.text_input("Project Name", key="new_project_name")
        # Project description input
        st.session_state.project_description = st.text_area("Project Description", key="new_project_description")
        
        # Create Project button logic
        if st.button("Create Project"):
            if project_name:
                if create_new_project(project_name):
                    st.success(f"Project '{project_name}' created successfully!")
                    st.session_state.project_name = project_name
                    st.session_state.page = "General"
                    st.session_state.new_project_completed = True
                    st.session_state.initialized = True
            else:
                st.error("Project name cannot be empty. Please enter a valid project name.")
        
        # Section for loading an existing project
        st.subheader("Load an Existing Project")
        st.write("Upload an existing project configuration file (YAML format) to load the project.")
        uploaded_file = st.file_uploader("Choose a YAML file", type="yaml")
        
        # Load Project button logic
        if uploaded_file is not None:
            if load_existing_project(uploaded_file):
                st.success(f"Project '{st.session_state.project_name}' loaded successfully!")
                st.session_state.page = "General"
                st.session_state.new_project_completed = True
                st.session_state.initialized = True