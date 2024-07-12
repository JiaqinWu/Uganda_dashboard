import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt 
import numpy as np

# Import the dataset
image = "CGHPI.png"
df = pd.read_csv('final_uganda.csv', encoding='ISO-8859-1')
df['Institution'] = df['Program']
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
    col1, col2 = st.columns([1, 3])  # Adjust the width ratio as needed

    # Place the image and title in the columns
    with col1:
        st.image(image, width=230)

    with col2:
        st.title('🇺🇬  Filter Questions by Score')
        st.sidebar.title('Enter your selections here!')

    # Ensure the Score column is sorted
    sorted_unique_scores = sorted(df['Score'].unique())
    # Sidebar for selection
    program_selected = st.sidebar.selectbox('Select Institution', df['Program'].unique())
    score_selected = st.sidebar.selectbox(
        'Select Score',
        sorted_unique_scores,
        index=sorted_unique_scores.index(1))
    st.sidebar.markdown(f"#### You selected: {score_selected}")
    format_selected = st.sidebar.selectbox('Select Format',['Plot','Table'],index=0)
    search_button = st.sidebar.button("Search")

    if search_button: 
        # Filter data based on selections
        filtered_data = df[(df['Program'] == program_selected) & 
                        (df['Score'] == score_selected)]
        filtered_data = filtered_data.sort_values(['module', 'section', 'Qn'])

        # Display the data
        if not filtered_data.empty:
            st.write("")
            #st.write("### Score Comparison by Program", filtered_data[['Program', 'Score']])
            # Create and display an Altair chart
            if format_selected == 'Plot':
                chart = alt.Chart(filtered_data).mark_bar().encode(
                    y=alt.Y('Question:N', sort='ascending'),  # Now just using ascending sort
                    x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 6]),  # Using Score on the x-axis with a defined domain
                    axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])), 
                    color='Program:N',  # Optional: coloring bars by Program
                    tooltip=['Module','Part', 'Question','Score', 'Level', 'Description']  # Optional: tooltips on hover
                ).properties(
                    width=600,
                    height=600,
                    title=f'Questions with Score of {score_selected} within Institution {program_selected}'
                )

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
                filtered_data['Section'] = filtered_data['Part']
                records = filtered_data[['Institution','Module','Section','Question']].reset_index().drop(columns='index')
                st.markdown(f"#### Questions with Score of {score_selected} within Institution {program_selected} are shown below:")
                st.dataframe(records) 


        else:
            st.write("No data available for the selected criteria.")

if __name__ == "__main__":
    app()