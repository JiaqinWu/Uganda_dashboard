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
        st.title('🇺🇬 Vertical Comparison -- Uganda SCORE Survey')
        st.sidebar.title('Enter your selections here!')

    # Sidebar for selection
    # Sidebar for selection
    program_selected = st.sidebar.selectbox('Select Program', df['Program'].unique())
    module_selected = st.sidebar.selectbox('Select Module', df['Module'].unique())
    part_selected = st.sidebar.selectbox('Select Section', df[df['Module'] == module_selected]['Part'].unique())
    available_questions = df[(df['Module'] == module_selected) & (df['Part'] == part_selected)]['Question'].unique()
    
    # Initialize session state
    if 'questions_selected' not in st.session_state:
        st.session_state.questions_selected = [available_questions[0]]

    questions_selected = st.sidebar.multiselect('Select Questions', options=available_questions, default=st.session_state.questions_selected)

    # Update session state
    st.session_state.questions_selected = questions_selected

    if st.sidebar.button('Select All Questions'):
        # Update the multiselect widget indirectly via session state
        st.session_state.questions_selected = available_questions
        st.experimental_rerun()

    if questions_selected:
        st.sidebar.markdown("### You selected:")
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
            #st.write("### Score Comparison by Program", filtered_data[['Program', 'Score']])
            # Create and display an Altair chart for vertical comparison
            chart = alt.Chart(filtered_data).mark_bar().encode(
                y='Question:N',  # Flipped; now using Question on the y-axis
                x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 5]),  # Using Score on the x-axis with a defined domain
                   axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])), 
                color='Question:N',  # Optional: coloring bars by question
                tooltip=['Question', 'Score']  # Tooltips on hover
            ).properties(
                width=600,
                height=300,
                title='Score by Question Comparison within Part'
            ).configure_axis(
                labelFontSize=12,
                titleFontSize=14
            ).interactive()

            st.altair_chart(chart, use_container_width=True)
        else:
            st.write("No data available for the selected criteria.")

if __name__ == "__main__":
    app()
