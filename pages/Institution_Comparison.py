import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt 
import numpy as np
import re
import plotly.express as px

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

    title = 'Comparison of Scores by Institution Within the Selected Question'
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
    if 'initialized_first_page' not in st.session_state:
        st.session_state.initialized_first_page = True
        st.session_state.search_button_clicked = False
        st.session_state.module_selected = 'One: Leadership and Governance'
        st.session_state.part_selected = 'Governance'
        st.session_state.question_selected = 'Q1. Is the organization legally constituted, registered?'
        st.session_state.plot_selected = 'Bar Plot' 
        

    # Sidebar for selection
    st.sidebar.title('Enter your selections here!')
    module_selected = st.sidebar.selectbox('Select Module', df['Module'].unique())
    part_selected = st.sidebar.selectbox('Select Section', df[df['Module'] == module_selected]['Part'].unique())
    question_selected = st.sidebar.selectbox('Select Question', df[(df['Module'] == module_selected) & (df['Part'] == part_selected)]['Question'].unique())
    st.sidebar.write("You selected:", question_selected)
    plot_selected = st.sidebar.selectbox('Select Visualization Type',['Bar Plot','Pie Plot','Radar Plot', 'Table'],index=0)
    search_button = st.sidebar.button("Search")


    if search_button:
        st.session_state.search_button_clicked = True
        st.session_state.module_selected = module_selected
        st.session_state.part_selected = part_selected
        st.session_state.question_selected = question_selected
        st.session_state.plot_selected = plot_selected
    else:
        # Use session state values if the button has not been clicked
        module_selected = st.session_state.module_selected
        part_selected = st.session_state.part_selected
        question_selected = st.session_state.question_selected
        plot_selected = st.session_state.plot_selected

    

    if not st.session_state.search_button_clicked:
        # Display default bar plot
        st.markdown("#### Quantitative Analysis:")      
        filtered_data = df[(df['Module'] == 'One: Leadership and Governance') & 
                        (df['Part'] == ' Governance') & 
                        (df['Question'] == 'Q1. Is the organization legally constituted, registered?')].reset_index()

        module_selected1 = module_selected.split(':')[1]
        if question_selected == 'Q5. Relevant program documents such as the ones below are all developed and disseminated to appropriate staff during start up\n-    Theory of change/LF\n-    Risk and Mitigation plan\n-    Performance Monitoring Plan\n-    Procurement Plan\n-    IRB/ethical reviews\n-    HR Plan\n-    Communication Plan\n-    Strategic Plan':
            question_selected1 = 'Q5. Relevant program documents such as the ones below are all developed and disseminated to appropriate staff during start up'
        elif question_selected == 'Q6. There is an established process for project teams to meet regularly and evaluate project performance and challenges and minutes are archived.\n\n(Includes project management, clinical management, senior management)':
            question_selected1 = 'Q6. There is an established process for project teams to meet regularly and evaluate project performance and challenges and minutes are archived.'
        else:
            question_selected1 = question_selected

        # Create and display an Altair chart
        st.write("")
        chart = alt.Chart(filtered_data).mark_bar().encode(
            y=alt.Y('Institution:N', sort=filtered_data['Institution'].unique()),  # Using :N to denote a nominal categorical field
            x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 6]),  # Using Score on the x-axis with a defined domain
            axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])), 
            color='Institution:N',  # Optional: coloring bars by Institution
            tooltip=['Institution', 'Score', 'Level', 'Description']  # Optional: tooltips on hover
        ).properties(
            width=600,
            height=600,
            title=alt.TitleParams(
                text=[
                    f"{question_selected1}", 
                    f"Bar Plot of Scores by Institution within {module_selected1}: {part_selected}"
                ]
            ))

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
        )

        # Display the chart in a Streamlit container
        st.altair_chart(final_chart, use_container_width=True)

        
        st.markdown("#### Qualitative Analysis:")
        # Ensure that the DataFrame is not empty and the comment column exists
        if pd.notna(filtered_data['comment'].iloc[0]) and filtered_data['comment'].iloc[0].strip():
            pattern = re.compile(r'(\w+): "([^"]+)"')
            comment = filtered_data['comment'].iloc[0]
            matches = dict(pattern.findall(comment))
            for institution, comment in matches.items():
                st.markdown(f"**{institution}**: {comment}")
        else:
            st.write("No qualitative analysis for the selected question.")

    else:
        # Show data based on selections
        st.markdown("#### Quantitative Analysis:")
        # Filter data based on selections
        filtered_data = df[(df['Module'] == module_selected) & 
                            (df['Part'] == part_selected) & 
                            (df['Question'] == question_selected)].reset_index()
        if not filtered_data.empty:
            module_selected1 = module_selected.split(':')[1]
            if question_selected == 'Q5. Relevant program documents such as the ones below are all developed and disseminated to appropriate staff during start up\n-    Theory of change/LF\n-    Risk and Mitigation plan\n-    Performance Monitoring Plan\n-    Procurement Plan\n-    IRB/ethical reviews\n-    HR Plan\n-    Communication Plan\n-    Strategic Plan':
                question_selected1 = 'Q5. Relevant program documents such as the ones below are all developed and disseminated to appropriate staff during start up'
            elif question_selected == 'Q6. There is an established process for project teams to meet regularly and evaluate project performance and challenges and minutes are archived.\n\n(Includes project management, clinical management, senior management)':
                question_selected1 = 'Q6. There is an established process for project teams to meet regularly and evaluate project performance and challenges and minutes are archived.'
            else:
                question_selected1 = question_selected

            # Create and display the selected plot type
            if plot_selected == 'Bar Plot':
                st.write("")
                chart = alt.Chart(filtered_data).mark_bar().encode(
                    y=alt.Y('Institution:N', sort=filtered_data['Institution'].unique()),  # Using :N to denote a nominal categorical field
                    x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 6]),  # Using Score on the x-axis with a defined domain
                    axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])), 
                    color='Institution:N',  # Optional: coloring bars by Institution
                    tooltip=['Institution', 'Score', 'Level', 'Description']  # Optional: tooltips on hover
                ).properties(
                    width=600,
                    height=600,
                    title=alt.TitleParams(
                        text=[
                            f"{question_selected1}", 
                            f"Bar Plot of Scores by Institution within {module_selected1}: {part_selected}"
                        ]
                    ))

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
                )

                # Display the chart in a Streamlit container
                st.altair_chart(final_chart, use_container_width=True)

            elif plot_selected == 'Pie Plot':
                st.write("")
                base = alt.Chart(filtered_data).mark_arc().encode(
                    theta=alt.Theta('Score:Q').stack(True),  
                    color=alt.Color('Program:N'),
                    tooltip=['Institution', 'Score', 'Level', 'Description'] 
                )

                pie = base.mark_arc(outerRadius = 120)
                text1 = base.mark_text(radius=150, size=12).encode(text="Level:N")

                # Combine the chart and the text
                final_chart1 = alt.layer(pie, text1).properties(
                    width=600,
                    height=400,
                    title=alt.TitleParams(
                        text=[
                            f"{question_selected1}", 
                            f"Pie Plot of Scores by Institution within {module_selected1}: {part_selected}"
                        ]
                    )).configure_axis(
                    labelFontSize=12,
                    titleFontSize=14
                ).interactive()

                # Display the chart in a Streamlit container
                st.altair_chart(final_chart1, use_container_width=True)


            elif plot_selected == 'Radar Plot':
                # Creating a radar chart
                fig = px.line_polar(filtered_data, r='Score', theta='Institution', line_close=True,
                                    text='Level',
                                    template="plotly_dark",
                                    title=f"{question_selected1}<br>Radar Plot of Scores by Institution within {module_selected1}: {part_selected}",
                                    hover_data={
                                        'Institution': True,
                                        'Score': True,  
                                        'Level': True,  
                                        'Description': True 
                                    })
                
                # Adjustments to improve layout
                fig.update_traces(textposition='bottom center')  # Adjust text positions to reduce overlap
                fig.update_layout(
                    polar=dict(
                        radialaxis=dict(showticklabels=True, tickangle=0),  # Adjust radial axis properties
                        angularaxis=dict(rotation=90, direction='clockwise', tickfont_size=15)  # Rotate angular axis for better label positioning
                    ),
                    font=dict(size=8)
                )

                # Displaying the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)
            
            else:
                filtered_data['Section'] = filtered_data['Part']
                records = filtered_data[['Module', 'Section', 'Question', 'Institution', 'Score', 'Level', 'Description']].reset_index().drop(columns='index')
                st.markdown(f"#### {question_selected}\n #### Comparison of Score by Institution are shown below:")
                st.dataframe(records)

        else:
            st.write("No quantitative data available for the selected question.")

        st.markdown("#### Qualitative Analysis:")
        # Ensure that the DataFrame is not empty and the comment column exists
        if not filtered_data.empty and 'comment' in filtered_data.columns and not filtered_data['comment'].isna().all():
            # Check if the first entry of the comment column is not NaN and is not empty
            if pd.notna(filtered_data['comment'].iloc[0]) and filtered_data['comment'].iloc[0].strip():
                pattern = re.compile(r'(\w+): "([^"]+)"')
                comment = filtered_data['comment'].iloc[0]
                matches = dict(pattern.findall(comment))
                for institution, comment in matches.items():
                    st.markdown(f"**{institution}**: {comment}")
            else:
                st.write("No qualitative analysis for the selected question.")
        else:
            st.write("No qualitative analysis for the selected question.")

if __name__ == "__main__":
    app()