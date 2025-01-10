"""
This module provides the PathManager class for managing paths related to project configurations in the MicroGridsPy application.
It includes paths for default and project configurations, inputs, archetypes, assets, documentation, GitHub repository, and contact email.
"""

from pathlib import Path

class PathManager:
    """
    Class to manage the paths for project configurations.
    """
    # Define the root path
    ROOT_PATH: Path = Path(__file__).resolve().parent.parent

    # Define paths for default and project configurations
    CONFIG_FOLDER_PATH: Path = ROOT_PATH / 'config'
    PROJECTS_FOLDER_PATH: Path = ROOT_PATH / 'projects'
    DEFAULT_YAML_FILE_PATH: Path = CONFIG_FOLDER_PATH / 'default.yaml'

    # Define inputs path
    INPUTS_FOLDER_PATH: Path = ROOT_PATH / 'validationtesting' / 'inputs'
    RESULTS_FOLDER_PATH: Path = ROOT_PATH / 'validationtesting' / 'results'
    FUEL_SPECIFIC_COST_FILE_PATH: Path = INPUTS_FOLDER_PATH / 'Fuel Specific Cost.csv'
    GRID_AVAILABILITY_FILE_PATH: Path = INPUTS_FOLDER_PATH / 'Grid Availability.csv'
    BENCHMARK_RESULTS_FILE_PATH: Path = RESULTS_FOLDER_PATH / 'Benchmark Results.csv'


    # Define paths for archetypes folder
    ARCHETYPES_FOLDER_PATH: Path = ROOT_PATH / 'validationtesting' / 'utils' / 'demand_archetypes'

    # Define paths for assets
    IMAGES_PATH: Path = ROOT_PATH / 'validationtesting'/ 'gui' / 'assets' / 'images'
    ICONS_PATH: Path = ROOT_PATH / 'validationtesting'/ 'gui' / 'assets' / 'icons'

    # Define the URL for documentation and GitHub repository
    DOCS_URL: str = "https://github.com/abirbouts/validationtesting/wiki"
    GITHUB_URL: str = "https://github.com/abirbouts/validationtesting"

    # Define the contact email
    MAIL_CONTACT: str = "abirbouts@ethz.ch"

    def __init__(self, project_name: str = "default"):
        self.project_name = project_name
        self.project_file_path = self.get_project_path(project_name)

        # Ensure the projects directory exists
        self.PROJECTS_FOLDER_PATH.mkdir(parents=True, exist_ok=True)

    def get_project_path(self, project_name: str) -> Path:
        """Get the full path to a project file."""
        return self.PROJECTS_FOLDER_PATH / f"{project_name}.yaml"

    def set_project_path(self, project_name: str) -> None:
        """Set the project path based on the provided project name."""
        self.project_name = project_name
        self.project_file_path = self.get_project_path(project_name)
