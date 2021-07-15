
from datetime import datetime
from pytz import timezone
import altair as alt

import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import sqlalchemy as sa
import pydeck as pdk
import geopandas as gpd
import pydeck as pkd
import json

#-----Page Configuration
st.set_page_config(page_title='Database Admin',
    page_icon='🦠',
    layout='wide',
    initial_sidebar_state='collapsed')

#-----Database connection---SQLalchemy
engine=create_engine('sqlite:///C:\\Sibylle\\Python\\Streamlit\\covid19-nam\\covid19_Nam.db')
#engine = create_engine(r'sqlite:///C:\path\to\covid19_Nam.db')
#engine = create_engine("sqlite:///./covid19-nam/covid19_Nam.db")
#districts_df=pd.read_sql(sa.text("SELECT * FROM districts"), engine)
#st.write(districts_df)

#cases_df=pd.read_sql(sa.text("SELECT * FROM cases"), engine)
#cases_df=pd.read_sql(sa.text("SELECT * FROM cases GROUP BY district"), engine)
#cases_df=pd.read_sql(sa.text("SELECT * FROM cases WHERE district=:district"), engine, params={"district": "unknown"})
#st.write(cases_df)
#users_df=pd.read_sql(sa.text("SELECT * FROM users"), engine)
h_df=pd.read_sql(sa.text("SELECT * FROM hospitalization"), engine)
st.write(h_df)

#d_df=pd.read_sql(sa.text("SELECT * FROM deaths WHERE death_date>publish_date"), engine)
#st.write(d_df)