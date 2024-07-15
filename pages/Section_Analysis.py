import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import altair as alt 
import plotly.express as px


# Import the dataset
image = "CGHPI.png"
df = pd.read_csv('final_uganda.csv', encoding='ISO-8859-1')
df['Institution'] = df['Program']
df['question'] = df['Qn']
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
        st.title('🇺🇬  Comparison of Scores of Questions Within One Section Within the Selected Institution')
        st.sidebar.title('Enter your selections here!')

    # Sidebar for selection
    #sorted_unique_scores = sorted(df['Score'].unique())
    program_selected = st.sidebar.selectbox('Select Institution', df['Program'].unique())
    module_selected = st.sidebar.selectbox('Select Module', df['Module'].unique())
    part_selected = st.sidebar.selectbox('Select Section', df[df['Module'] == module_selected]['Part'].unique())
    st.sidebar.markdown(f"#### You selected: {part_selected}")
    available_questions = df[(df['Module'] == module_selected) & (df['Part'] == part_selected)]['Question'].unique()
    available_scores = df[(df['Program'] == program_selected) & (df['Module'] == module_selected) & (df['Part'] == part_selected)]['Score'].unique()
    sorted_unique_scores = sorted(available_scores)

    # Button to select all questions
    if st.sidebar.button('Select All Scores'):
        st.session_state.scores_selected = list(sorted_unique_scores)
    elif 'scores_selected' not in st.session_state or module_selected != st.session_state.last_module \
        or program_selected != st.session_state.last_program or part_selected != st.session_state.last_part:
        # Reset to the first available question by default if not 'Select All' and if part or module has changed
        st.session_state.scores_selected = [sorted_unique_scores[0]]
    

    scores_selected = st.sidebar.multiselect(
        'Select Score(s)',
        sorted_unique_scores,
        default=st.session_state.scores_selected) #sorted_unique_scores

    st.session_state.scores_selected = scores_selected
    
    # Displaying the selected options in the sidebar
    scores_selected1 = [str(score) for score in scores_selected]
    if scores_selected:  # Checks if any score is selected
        st.sidebar.markdown(f"#### You selected: {', '.join(scores_selected1)}")
    else:
        st.sidebar.markdown("#### No score selected")
    
    # Button to select all questions
    if st.sidebar.button('Select All Questions'):
        st.session_state.questions_selected = available_questions
    elif 'questions_selected' not in st.session_state or module_selected != st.session_state.last_module \
        or program_selected != st.session_state.last_program or part_selected != st.session_state.last_part:
        # Reset to the first available question by default if not 'Select All' and if part or module has changed
        st.session_state.questions_selected = [available_questions[0]]

    # Multiselect widget with session state management
    questions_selected = st.sidebar.multiselect('Select Questions', options=available_questions, default=st.session_state.questions_selected)

    st.session_state.questions_selected = questions_selected

    # Display selected questions
    if questions_selected:
        st.sidebar.markdown("#### You selected:")
        st.sidebar.markdown("* " + "\n* ".join(questions_selected))
    else:
        st.sidebar.write("#### No questions selected")
    
    # Update last viewed module and part
    st.session_state.last_program = program_selected
    st.session_state.last_module = module_selected
    st.session_state.last_part = part_selected
    
    plot_selected = st.sidebar.selectbox('Select Chart Type',['Bar','Pie','Radar'],index=0)
    search_button = st.sidebar.button("Search")


    if search_button: 
        # Filter data based on selections
        filtered_data = df[(df['Module'] == module_selected) & 
                        (df['Part'] == part_selected) & 
                        (df['Program'] == program_selected) &
                        (df['Question'].isin(questions_selected))&
                        (df['Score'].isin(scores_selected))]

        # Display the data
        if not filtered_data.empty:
            module_selected1 = module_selected.split(':')[1]
            #st.write("### Score Comparison by Program", filtered_data[['Program', 'Score']])
            # Create and display an Altair chart for vertical comparison
            if plot_selected == 'Bar':
                st.write("")
                chart = alt.Chart(filtered_data).mark_bar().encode(
                    y=alt.Y('Question:N', sort=alt.EncodingSortField(field='Qn', order='ascending')),
                    x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 6]),
                        axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])),
                    color=alt.Color('Question:N', sort=alt.EncodingSortField(field='Qn', order='ascending')),
                    tooltip=['Question', 'Score', 'Level', 'Description']
                ).properties(
                    width=600,
                    height=600,
                    title=f'Bar Chart of Scores by Question within {module_selected1}: {part_selected}'
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

            elif plot_selected == 'Pie':
                st.write("")
                base = alt.Chart(filtered_data).mark_arc().encode(
                    theta=alt.Theta('Score:Q').stack(True),  
                    color=alt.Color('Question:N',sort=alt.EncodingSortField(field='Qn', order='ascending')),
                    tooltip=['Question', 'Score', 'Level', 'Description'] 
                )

                pie = base.mark_arc(outerRadius = 120)
                text1 = base.mark_text(radius=150, size=12).encode(text="Level:N")

                # Combine the chart and the text
                final_chart1 = alt.layer(pie, text1).properties(
                    width=600,
                    height=400,
                    title=f'Pie Chart of of Scores by Question within {module_selected1}: {part_selected}'
                ).configure_axis(
                    labelFontSize=12,
                    titleFontSize=14
                ).interactive()

                # Display the chart in a Streamlit container
                st.altair_chart(final_chart1, use_container_width=True)

            
            else:
                 # Creating a radar chart
                filtered_data['Question1'] = 'Q' + filtered_data['Qn'].astype(str)
                fig = px.line_polar(filtered_data, r='Score', theta='Question1', line_close=True,
                                    text = 'Level',
                                    template="plotly_dark",
                                    title=f'Radar Chart of Scores by Question within {module_selected1}: {part_selected}',
                                    hover_data={
                                        'Question': True,
                                        'Score': True,  
                                        'Level': True,  
                                        'Description': True 
                                    })
                
                # Adjustments to improve layout
                fig.update_traces(textposition='bottom center')  # Adjust text positions to reduce overlap
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(showticklabels=True, tickangle=0),  # Adjust radial axis properties
                        angularaxis=dict(rotation=90, direction='clockwise',tickfont_size=15)  # Rotate angular axis for better label positioning
                    ),
                    font=dict(size=8)
                )

                # Displaying the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)



        else:
            st.markdown("### No data available for the selected criteria.")

if __name__ == "__main__":
    app()
