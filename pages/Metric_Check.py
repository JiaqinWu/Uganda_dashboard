import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt 
import numpy as np
import re
import plotly.express as px

# Import the dataset
image = "CGHPI.png"
df = pd.read_csv('Metric.csv', encoding='ISO-8859-1')
df = df.rename(columns={'ï»¿Module':'Module'})

# Streamlit application
def app():
    # Main page content
    st.set_page_config(page_title = 'Dashboard -- Uganda SCORE Survey', page_icon='🇺🇬',layout='wide')

    title = 'Check the metrics for each question'
    col1, col2, col3 = st.columns([4, 1, 5])

    with col1:
        st.write("")

    with col2:
        st.image(image, width=250)

    with col3:
        st.write("")

    # Center the image and title using HTML and CSS in Markdown
    st.markdown(
        f"""
        <style>
        .centered {{
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 30vh;
            text-align: center;
        }}
        </style>
        <div class="centered">
            <h2 style='text-align: center'>{title}</h2>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Initialize session state
    if 'initialized_fourth_page' not in st.session_state:
        st.session_state.initialized_fourth_page = True
        st.session_state.search_button_clicked1 = False
        st.session_state.module_selected1 = 'One: Leadership and Governance'
        st.session_state.part_selected1 = 'Governance'

        

    # Sidebar for selection
    st.sidebar.title('Enter your selections here!')
    module_selected1 = st.sidebar.selectbox('Select Module', df['Module'].unique())
    part_selected1 = st.sidebar.selectbox('Select Section', df[df['Module'] == module_selected1]['Section'].unique())
    st.sidebar.write("You selected:", part_selected1)
    search_button = st.sidebar.button("Search")


    if search_button:
        st.session_state.search_button_clicked1 = True
        st.session_state.module_selected1 = module_selected1
        st.session_state.part_selected1 = part_selected1
    else:
        # Use session state values if the button has not been clicked
        module_selected1 = st.session_state.module_selected1
        part_selected1 = st.session_state.part_selected1


    

    if not st.session_state.search_button_clicked1:
        # Display default bar plot   
        filtered_data = df[(df['Module'] == 'One: Leadership and Governance') & 
                        (df['Section'] == 'Governance')].reset_index()

        records = filtered_data[['Module', 'Section', 'Question', '1: Nonexistent', '2: Basic','3: Adequate','4: Comprehensive','5: Exceptional']].reset_index().drop(columns='index')
        st.markdown(f"#### Metrics for questions within One: Leadership and Governance: Governance are shown below:")
        st.dataframe(records)

    else:
        # Show data based on selections
        st.markdown(f"#### Metrics for questions within {module_selected1}: {part_selected1} are shown below:")
        # Filter data based on selections
        filtered_data = df[(df['Module'] == module_selected1) & 
                        (df['Section'] == part_selected1)].reset_index()

        records = filtered_data[['Module', 'Section', 'Question', '1: Nonexistent', '2: Basic','3: Adequate','4: Comprehensive','5: Exceptional']].reset_index().drop(columns='index')
        st.dataframe(records)

if __name__ == "__main__":
    app()