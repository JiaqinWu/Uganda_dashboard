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

    # Use columns for side-by-side layout
    col1, col2 = st.columns([1, 3])  # Adjust the width ratio as needed

    # Place the image and title in the columns
    with col1:
        st.image(image, width=230)

    with col2:
        st.title('🇺🇬  Comparison of Scores by Institution Within the Selected Question')
        st.sidebar.title('Enter your selections here!')

    # Sidebar for selection
    module_selected = st.sidebar.selectbox('Select Module', df['Module'].unique())
    part_selected = st.sidebar.selectbox('Select Section', df[df['Module'] == module_selected]['Part'].unique())
    question_selected = st.sidebar.selectbox('Select Question', df[(df['Module'] == module_selected) & (df['Part'] == part_selected)]['Question'].unique())
    st.sidebar.write("You selected:", question_selected)
    plot_selected = st.sidebar.selectbox('Select Chart Type',['Bar','Pie','Radar'],index=0)
    search_button = st.sidebar.button("Search")

    if search_button: 
        # Filter data based on selections
        st.markdown("#### Quantitative Analysis:")
        filtered_data = df[(df['Module'] == module_selected) & 
                        (df['Part'] == part_selected) & 
                        (df['Question'] == question_selected)].reset_index()

        # Display the data
        if not filtered_data.empty:
            module_selected1 = module_selected.split(':')[1]
            #st.write("### Score Comparison by Program", filtered_data[['Program', 'Score']])
            # Create and display an Altair chart
            if plot_selected == 'Bar':
                st.write("")
                chart = alt.Chart(filtered_data).mark_bar().encode(
                    y=alt.Y('Program:N', sort=filtered_data['Program'].unique()),  # Using :N to denote a nominal categorical field
                    x=alt.X('Score:Q', scale=alt.Scale(domain=[0, 6]),  # Using Score on the x-axis with a defined domain
                    axis=alt.Axis(values=[0, 1, 2, 3, 4, 5])), 
                    color='Program:N',  # Optional: coloring bars by Program
                    tooltip=['Institution', 'Score', 'Level', 'Description']  # Optional: tooltips on hover
                ).properties(
                    width=600,
                    height=600,
                    title=f'Bar Chart of Scores by Institution within {module_selected1}: {part_selected}'
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

            elif plot_selected == 'Pie':
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
                    title=f'Pie Chart of Scores Distribution within {module_selected1}: {part_selected}'
                ).configure_axis(
                    labelFontSize=12,
                    titleFontSize=14
                ).interactive()

                # Display the chart in a Streamlit container
                st.altair_chart(final_chart1, use_container_width=True)

            else:
                # Creating a radar chart
                fig = px.line_polar(filtered_data, r='Score', theta='Institution', line_close=True,
                                    text = 'Level',
                                    template="plotly_dark",
                                    title=f'Radar Chart of Scores by Institution within {module_selected1}: {part_selected}',
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
                        angularaxis=dict(rotation=90, direction='clockwise',tickfont_size=15)  # Rotate angular axis for better label positioning
                    ),
                    font=dict(size=8)
                )

                # Displaying the chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)


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
