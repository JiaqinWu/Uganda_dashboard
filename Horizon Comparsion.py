import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt 

# Import the dataset
image = "CGHPI.png"
df1 = pd.read_csv('Uganda_cleaned.csv')
df = df1.melt(id_vars=["Module", "Part", "Question"], var_name="Program", value_name="Score")[:555]
df.head()
df['Module'] = df['Module'].replace('One','One: Leadership and Governance').replace('Two','Two: Program Management').replace('Three','Three: Technical Assistance').\
replace('Four','Four: Data Use').replace("Five","Five: Sustainability")



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
        st.title('🇺🇬 Horizon Comparison -- Uganda SCORE Survey')
        st.sidebar.title('Enter your selections here!')

    # Sidebar for selection
    module_selected = st.sidebar.selectbox('Select Module', df['Module'].unique())
    part_selected = st.sidebar.selectbox('Select Part', df[df['Module'] == module_selected]['Part'].unique())
    question_selected = st.sidebar.selectbox('Select Question', df[(df['Module'] == module_selected) & (df['Part'] == part_selected)]['Question'].unique())
    st.sidebar.write("You selected:", question_selected)
    search_button = st.sidebar.button("Search")

    if search_button: 
        # Filter data based on selections
        filtered_data = df[(df['Module'] == module_selected) & 
                        (df['Part'] == part_selected) & 
                        (df['Question'] == question_selected)]

        # Display the data
        if not filtered_data.empty:
            st.write("")
            #st.write("### Score Comparison by Program", filtered_data[['Program', 'Score']])
            # Create and display an Altair chart
            chart = alt.Chart(filtered_data).mark_bar().encode(
                y=alt.Y('Program:N', sort=filtered_data['Program'].unique()),  # Using :N to denote a nominal categorical field
                x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 5]),  # Using Score on the x-axis with a defined domain
                   axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])), 
                color='Program:N',  # Optional: coloring bars by Program
                tooltip=['Program', 'Score']  # Optional: tooltips on hover
            ).properties(
                width=600,
                height=300,
                title='Score Comparison by Program'
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("No data available for the selected criteria.")

if __name__ == "__main__":
    app()
