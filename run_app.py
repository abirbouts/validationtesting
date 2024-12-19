import streamlit as st
from pathlib import Path
from config.path_manager import PathManager

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
from validationtesting.gui.views.results_page import results
from validationtesting.gui.views.utils import initialize_session_state
from validationtesting.utils.savetoyaml import save_to_yaml


if 'initialized' not in st.session_state:
    st.session_state.initialized = False

initial_page = st.Page(
    page=initial_page,
    title="Initial Page",
    icon="👋",
    default=True
)

active_pages = {}

active_pages["General"] = [initial_page]

if st.session_state.initialized:
    if st.session_state.new_project_completed:

        component_selection_page = st.Page(
            page=component_selection,
            title="Component Selection",
            icon="🔌",
        )
        active_pages["General"].append(component_selection_page)

        general_page = st.Page(
            page=general,
            title="General",
            icon="🔧",
        )
        active_pages["General"].append(general_page)

        if st.session_state.solar_pv:
            solar_pv_page = st.Page(
                page=solar_pv,
                title="Solar PV Specifications",
                icon="☀️",
            )

            active_pages["Solar PV"] = [solar_pv_page]

            if st.session_state.technical_validation:
                irradiation_data_page = st.Page(
                    page=irradiation_data,
                    title="Irradiation Data",
                    icon="📊",
                )

                def upload_solar_model_output():
                    upload_model_output('solar_pv')

                upload_solar_model_output_page = st.Page(
                    page=upload_solar_model_output,
                    title="Upload Solar Model Output",
                    icon="📤",
                )

                active_pages["Solar PV"] = [solar_pv_page, irradiation_data_page, upload_solar_model_output_page]


        if st.session_state.wind:
            wind_page = st.Page(
                page=wind,
                title="Wind Energy",
                icon="🌀",
            )

            active_pages["Wind"] = [wind_page]

            if st.session_state.technical_validation:

                wind_data_page = st.Page(
                    page=wind_data,
                    title="Wind Data",
                    icon="📊",
                )

                def upload_wind_model_output():
                    upload_model_output('wind')

                upload_wind_model_output_page = st.Page(
                    page=upload_wind_model_output,
                    title="Upload Wind Model Output",
                    icon="📤",
                )

                active_pages["Wind"] = [wind_page, wind_data_page, upload_wind_model_output_page]

        if st.session_state.generator:
            generator_page = st.Page(
                page=generator,
                title="Generator",
                icon="⚙️",
            )

            active_pages["Generator"] = [generator_page]

            if st.session_state.technical_validation:

                def upload_generator_model_output():
                    upload_model_output('generator')

                upload_generator_model_output_page = st.Page(
                    page=upload_generator_model_output,
                    title="Upload Generator Model Output",
                    icon="📤",
                )

                active_pages["Generator"] = [generator_page, upload_generator_model_output_page]

        if st.session_state.battery:
            battery_page = st.Page(
                page=battery,
                title="Battery",
                icon="🔋",
            )

            active_pages["Battery"] = [battery_page]

            if st.session_state.technical_validation:

                def upload_battery_model_output():
                    upload_model_output('battery')

                upload_battery_model_output_page = st.Page(
                    page=upload_battery_model_output,
                    title="Upload Battery Model Output",
                    icon="📤",
                )

                active_pages["Battery"] = [battery_page, upload_battery_model_output_page]

        if st.session_state.energy_balance:
            def upload_consumption():
                upload_model_output('consumption')

            upload_consumption_page = st.Page(
                page=upload_consumption,
                title="Upload Consumption Data",
                icon="📤",
            )

            active_pages["Consumption"] = [upload_consumption_page]

        run_page = st.Page(
            page=run_model,
            title="Run Page",
            icon="🏃",
        )

        results_page = st.Page(
            page=results,
            title="Results Page",
            icon="📈",
        )
        active_pages["Run"] = [run_page, results_page]



    # If a project is selected, display its name in the sidebar
    if st.session_state.project_name:
        st.sidebar.markdown(f"### Selected Project: **{st.session_state.project_name}**")
    else:
        st.sidebar.markdown("### No Project Selected")

    if st.session_state.page != "Initial Page":
        save_to_yaml()

pg = st.navigation(pages=active_pages)
pg.run()

render_footer()