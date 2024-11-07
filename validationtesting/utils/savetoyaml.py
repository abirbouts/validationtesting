import streamlit as st
from pathlib import Path
from datetime import datetime
from validationtesting.model.parameters import ProjectParameters
from config.path_manager import PathManager

def datetime_to_str(obj):
    """Convert a datetime object to an ISO string format."""
    if isinstance(obj, datetime):
        return obj.isoformat()
    return obj

def update_nested_settings(settings):
    """Recursively update nested settings from session state."""
    for field in settings.__fields__:
        if hasattr(settings, field):
            value = getattr(settings, field)
            # Update based on the type of the value
            if isinstance(value, (int, float, str, bool)):
                if field in st.session_state:
                    setattr(settings, field, st.session_state[field])
            elif isinstance(value, datetime):
                if field in st.session_state:
                    setattr(settings, field, datetime_to_str(st.session_state[field]))
            elif isinstance(value, list):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    setattr(settings, field, new_value if isinstance(new_value, list) else [new_value])
            elif isinstance(value, dict):
                if field in st.session_state:
                    new_value = st.session_state[field]
                    if isinstance(new_value, dict):
                        current_dict = getattr(settings, field)
                        current_dict.update(new_value)
                        setattr(settings, field, current_dict)
            elif hasattr(value, '__fields__'):
                # Recursive update for nested Pydantic models
                setattr(settings, field, update_nested_settings(value))
    return settings

def save_to_yaml():
    """Load, update, and save the project parameters based on session state."""
    # Get the current project's YAML file path
    project_name = st.session_state.get('project_name')

    # Set up the path to the project's YAML file
    path_manager = PathManager(project_name)
    yaml_filepath = path_manager.PROJECTS_FOLDER_PATH / project_name / f"{project_name}.yaml"

    # Load current project parameters from YAML
    current_settings = ProjectParameters.instantiate_from_yaml(yaml_filepath)
    
    # Update current settings with values from session state
    updated_settings = update_nested_settings(current_settings)

    # Save the updated settings back to the YAML file
    updated_settings.save_to_yaml(yaml_filepath)
    st.toast(f"Settings saved successfully to {yaml_filepath}")