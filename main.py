import streamlit as st
from st_pages.home_page import main as home_page
from st_pages.overview_page import main as overview_page
from st_pages.chatbot_page import main as chatbot_page
from st_pages.team_page import main as team_page
from constants import CSS_STYLING

st.set_page_config(page_title="Bhopal's BRTS Chatbot", page_icon='assets/img/favicon.png', layout='wide')
st.write(CSS_STYLING, unsafe_allow_html=True)

home, overview, chatbot, team = st.tabs(['Home', 'Overview', 'Chatbot', 'Team'])

home_page(home)
overview_page(overview)
chatbot_page(chatbot)
team_page(team)