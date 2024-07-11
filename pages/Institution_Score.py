import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import altair as alt 

# Import the dataset
image = "CGHPI.png"
df = pd.read_csv('final_uganda.csv', encoding='ISO-8859-1')
df.head()
df['Module'] = df['Module'].replace('One','One: Leadership and Governance').replace('Two','Two: Program Management').replace('Three','Three: Technical Assistance').\
replace('Four','Four: Data Use').replace("Five","Five: Sustainability")
# Define conditions and choices for the text labels
conditions = [
    df['Score'] == 1,
    df['Score'] == 2,
    df['Score'] == 3,
    df['Score'] == 4,
    df['Score'] == 5
]
choices = ['Nonexistent', 'Basic', 'Adequate', 'Comprehensive', 'Exceptional']

# Apply conditions and choices
df['Level'] = np.select(conditions, choices, default='Not Applicable')

# Streamlit application
def app():
    # Main page content
    st.set_page_config(page_title = 'Dashboard -- Uganda SCORE Survey', page_icon='🇺🇬',layout='wide')

    # Use columns for side-by-side layout
    col1, col2 = st.columns([1, 6])  # Adjust the width ratio as needed

    # Place the image and title in the columns
    with col1:
        st.image(image, width=130)

    with col2:
        st.title('🇺🇬 Institution Score -- Uganda SCORE Survey')
        st.sidebar.title('Enter your selections here!')

    # Sidebar for selection
    program_selected = st.sidebar.selectbox('Select Institution', df['Program'].unique())
    module_selected = st.sidebar.selectbox('Select Module', df['Module'].unique())
    part_selected = st.sidebar.selectbox('Select Section', df[df['Module'] == module_selected]['Part'].unique())
    st.sidebar.markdown(f"#### You selected: {part_selected}")
    available_questions = df[(df['Module'] == module_selected) & (df['Part'] == part_selected)]['Question'].unique()
    
    # Button to select all questions
    if st.sidebar.button('Select All Questions'):
        st.session_state.questions_selected = available_questions
    elif 'questions_selected' not in st.session_state or module_selected != st.session_state.last_module or part_selected != st.session_state.last_part:
        # Reset to the first available question by default if not 'Select All' and if part or module has changed
        st.session_state.questions_selected = [available_questions[0]]

    # Update last viewed module and part
    st.session_state.last_module = module_selected
    st.session_state.last_part = part_selected

    # Multiselect widget with session state management
    questions_selected = st.sidebar.multiselect('Select Questions', options=available_questions, default=st.session_state.questions_selected)

    # Display selected questions
    if questions_selected:
        st.sidebar.markdown("#### You selected:")
        st.sidebar.markdown("* " + "\n* ".join(questions_selected))
    else:
        st.sidebar.write("No questions selected")

    search_button = st.sidebar.button("Search")


    if search_button: 
        # Filter data based on selections
        filtered_data = df[(df['Module'] == module_selected) & 
                        (df['Part'] == part_selected) & 
                        (df['Program'] == program_selected) &
                        (df['Question'].isin(questions_selected))]

        # Display the data
        if not filtered_data.empty:
            st.write("")
            module_selected1 = module_selected.split(':')[1]
            #st.write("### Score Comparison by Program", filtered_data[['Program', 'Score']])
            # Create and display an Altair chart for vertical comparison
            chart = alt.Chart(filtered_data).mark_bar().encode(
                y=alt.Y('Question:N', sort=alt.EncodingSortField(field='Qn', order='ascending')),
                x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 6]),
                    axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])),
                color=alt.Color('Question:N', sort=alt.EncodingSortField(field='Qn', order='ascending')),
                tooltip=['Question', 'Score', 'Level', 'Description']
            ).properties(
                width=600,
                height=600,
                title=f'Comparison of Score by Questions within {module_selected1}: {part_selected}'
            )

            # Add text labels on each bar
            text = chart.mark_text(
                align='left',  # Adjust alignment here
                baseline='middle',
                color='black'
            ).encode(
                text='Level:N',
            )

            # Combine the chart and the text
            final_chart = alt.layer(chart, text).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            ).interactive()

            # Display the chart in a Streamlit container
            st.altair_chart(final_chart, use_container_width=True)


        else:
            st.write("No data available for the selected criteria.")

if __name__ == "__main__":
    app()
