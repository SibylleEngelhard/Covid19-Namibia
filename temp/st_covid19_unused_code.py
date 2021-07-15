from datetime import datetime
import altair as alt

import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import sqlalchemy as sa
import pydeck as pdk
import geopandas as gpd
import json


#-----Page Configuration
st.set_page_config(page_title='Covid19 Namibia',
    page_icon='🇳🇦',
    #page_icon='🚩',
    layout='wide',
    initial_sidebar_state='collapsed')


#----menu button invisible
#st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)

#----change padding
padding1 = 0
padding2 = 4
st.markdown(f""" <style>
    .reportview-container .main .block-container{{
        padding-top: {padding1}rem;
        padding-right: {padding2}rem;
        padding-left: {padding2}rem;
        padding-bottom: {padding1}rem;
    }} </style> """, unsafe_allow_html=True)
#change settings for header h2 subheader h3 and text
st.markdown('<style>h3{margin-bottom:0rem;margin-top:0rem;}</style>',unsafe_allow_html=True)
st.markdown('<style>h2{margin-bottom:0rem;margin-top:0rem;font-weight:bold;}</style>',unsafe_allow_html=True)
st.markdown('<style>p{margin-bottom:.1rem;margin-top:.1rem;}</style>',unsafe_allow_html=True)

#-----Database connection---SQLalchemy
engine = create_engine("sqlite:///covid19_Nam.db")

#get from database date of first and last case entry
query=pd.read_sql(sa.text("SELECT MIN(cases_date) FROM cases"), engine)
first_date_str=query.iat[0,0]
first_date=datetime.strptime(first_date_str, '%Y-%m-%d').date() 
query=pd.read_sql(sa.text("SELECT MAX(cases_date) FROM cases"), engine)
last_date_str=query.iat[0,0]
last_date=datetime.strptime(last_date_str, '%Y-%m-%d').date() 
#display date for intern use and tests
display_date=last_date
last_week_str=last_date.strftime('%G-%V')
last_weekday_str=last_date.strftime('%u')
date_range = pd.date_range(start=first_date,end=last_date,name="datetime")

#----Image and Title 2 Columns
col1a, col1b= st.beta_columns([1,6])

with col1a:
	image = Image.open('Nam.jpg')
	st.image(image,width=100)
with col1b:
	st.title('Covid19 Namibia Dashboard')

#-----Display Last Update Date ---- 
col2a, col2b= st.beta_columns([2,2])
with col2a:
	st.subheader("Last update: "+last_date.strftime("%A, %d %B %Y"))
#with col2b:
	#to change display date for tests
	#display_date = st.date_input("Change Display Date",last_date)

#----Total Cases, Daily Cases, Cases per districts map, Cases per regions map
col3a,col3b,col3c,col3d= st.beta_columns([1,1,1,1])

with col3a:
	st.subheader("Total Cases:")
	#st.text("currently displaying total on display date!!!")
	#Daily Total Cases
	q=pd.read_sql(sa.text("SELECT SUM(new_cases) FROM cases where cases_date<=:display_date"), engine, params={"display_date": display_date})
	daily_all_cases=q.iat[0,0]
	st.write('Total cases: '+str(daily_all_cases))
	#Daily Total Recoveries
	q=pd.read_sql(sa.text("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date <=:display_date"), engine, params={"display_date": display_date})
	daily_all_recoveries=q.iat[0,0]
	st.write('Total recoveries: '+str(daily_all_recoveries))   
	#Daily Total Deaths
	q=pd.read_sql(sa.text("SELECT COUNT(*) FROM deaths WHERE publish_date <=:display_date"), engine,params={"display_date":display_date})
	daily_all_deaths=q.iat[0,0]
	st.write('Total deaths: '+str(daily_all_deaths))   
	#Active Cases
	q=pd.read_sql(sa.text("SELECT SUM(missing_cases) FROM missing WHERE missing_date <=:display_date"), engine,params={"display_date":display_date})
	missing_cases=q.iat[0,0]
	daily_active_cases=daily_all_cases-daily_all_recoveries-daily_all_deaths-missing_cases
	st.write('Active cases: '+str(daily_active_cases))   
with col3b:
	st.subheader("Daily Cases:")
	#Daily New Cases
	q=pd.read_sql(sa.text("SELECT SUM(new_cases) FROM cases where cases_date=:display_date"), engine, params={"display_date": display_date})
	daily_new_cases=q.iat[0,0]
	st.write('New cases: '+str(daily_new_cases))
	#Daily New Recoveries
	q=pd.read_sql(sa.text("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date=:display_date"), engine, params={"display_date": display_date})
	daily_new_recoveries=q.iat[0,0]
	st.write('Recoveries: '+str(daily_new_recoveries))
	#Daily Neww Deaths
	q=pd.read_sql(sa.text("SELECT COUNT(*) FROM deaths WHERE publish_date=:display_date"), engine, params={"display_date": display_date})
	daily_new_deaths=q.iat[0,0]
	st.write('Deaths: '+str(daily_new_deaths))
	
	#Info about maximum number of cases per district and maximum number of deaths announced
	a=pd.read_sql(sa.text("SELECT cases_date,district,SUM(new_cases) FROM cases GROUP BY cases_date,district ORDER BY SUM(new_cases) DESC"), engine)
	max_cases=int(a['SUM(new_cases)'].iloc[0])
	#st.markdown('''**Max number of daily new cases per district:** ''')
	text1=str(a['SUM(new_cases)'].iloc[0])
	text2=str(a['cases_date'].iloc[0])
	text3=str(a['district'].iloc[0])
	#st.write(text2+' '+text3+': '+text1)

	b=pd.read_sql(sa.text("SELECT publish_date,COUNT(*) FROM deaths GROUP BY publish_date ORDER BY COUNT(*) DESC"), engine)
	#st.markdown('''**Max number of deaths published:** ''')
	text1=str(b['COUNT(*)'].iloc[0])
	text2=str(b['publish_date'].iloc[0])
	#st.write(text2+': '+text1)

with col3c:
	st.write('New Cases per District:')
	districts_df = pd.read_csv('./csv/districts.csv')
	cases_districts_df=pd.read_sql(sa.text("SELECT SUM(new_cases),district FROM cases where cases_date=:display_date GROUP BY cases_date,district"), engine, params={"display_date": display_date})
	cases_districts_df=pd.merge(cases_districts_df,districts_df,how = 'right', on='district')	
	cases_districts_df=cases_districts_df.fillna(0)
	cases_districts_df=cases_districts_df.rename(columns={'SUM(new_cases)':'cases'})
	cases_districts_df['normal']=cases_districts_df['cases']/cases_districts_df['cases'].max()
	# create conditions for classification
	conditions = [
	    (cases_districts_df['cases'] == 0),
	    (cases_districts_df['cases'] > 0) & (cases_districts_df['cases'] < 100),
	    (cases_districts_df['cases'] >= 100) & (cases_districts_df['cases'] < 200),
	    (cases_districts_df['cases'] >= 200) & (cases_districts_df['cases'] < 300),
	    (cases_districts_df['cases'] >= 300)
	    ]
	# create a list of the values to assign for each condition
	valuesR = [88, 252, 255, 255, 252]
	valuesG = [163, 174, 62, 0, 0]
	valuesB = [92 ,104, 23, 0, 130]
	# create new R, G, B columns and use np.select to assign values to it using our lists as arguments
	cases_districts_df['R'] = np.select(conditions, valuesR)
	cases_districts_df['G'] = np.select(conditions, valuesG)
	cases_districts_df['B'] = np.select(conditions, valuesB)
	#####create geodataframe for json polygon layer
	cases_districts_gdf=gpd.read_file("./shapefiles/districts/health_districts_covid.shp")[['region','health_dis','geometry']]
	cases_districts_gdf.columns=['region','district','geometry']
	cases_districts_gdf=cases_districts_gdf.merge(cases_districts_df,on='district', how='left')
	cases_districts_gdf.fillna(0,inplace=True)
	cases_districts_gdf['cases']=cases_districts_gdf['cases'].astype(int)
	cases_districts_json=json.loads(cases_districts_gdf.to_json())

	disks=pdk.Layer(
   			 "ColumnLayer",
    		data=cases_districts_df,
    		get_position=['longitude', 'latitude'],
			radius=25000,
    		get_fill_color=['R', 'G', 'B', 150],
    		extruded=False,
    		stroked=True,
    		auto_highlight=True,)
	columns=pdk.Layer(
   			 "ColumnLayer",
    		data=cases_districts_df,
    		get_position=['longitude', 'latitude'],
    		get_elevation='normal',
    		elevation_scale=400000,
    		radius=25000,
    		get_fill_color=['R', 'G', 'B', 150],
    		extruded=True,
    		stroked=True,
    		auto_highlight=True,)
	polygons=pdk.Layer(
			'GeoJsonLayer',
			cases_districts_json,
			#pickable=True,
			opacity=0.3,
			stroke=True,
			filled=False,
	   		#get_fill_color=[255, 255, 0],
			get_fill_color='[255, (1-properties.normal) * 255, properties.normal * 255]',
    		get_line_color=[0, 0, 0],
			get_line_width=2000,)
	st.pydeck_chart(pdk.Deck(
		map_style='mapbox://styles/mapbox/streets-v11',
		initial_view_state=pdk.ViewState(
		latitude=-24,
		longitude=17.7,
		zoom=4,
		height=250,
		pitch=50,
		bearing=0,),
		layers=[polygons,disks,columns]
		))

with col3d:
	st.write('New Cases per Region:')
	regions_df = pd.read_csv('./csv/regions.csv')
	cases_regions_df=pd.read_sql(sa.text("SELECT SUM(new_cases),region FROM cases JOIN districts on cases.district =districts.district where cases_date=:display_date GROUP BY cases_date,region"), engine, params={"display_date": display_date})
	cases_regions_df=pd.merge(cases_regions_df,regions_df,how = 'right', on='region')	
	cases_regions_df=cases_regions_df.fillna(0)
	cases_regions_df=cases_regions_df.rename(columns={'SUM(new_cases)':'cases'})
	cases_regions_df['normal']=cases_regions_df['cases']/cases_regions_df['cases'].max()
	# create conditions for classification
	conditions = [
	    (cases_regions_df['cases'] == 0),
	    (cases_regions_df['cases'] > 0) & (cases_regions_df['cases'] < 100),
	    (cases_regions_df['cases'] >= 100) & (cases_regions_df['cases'] < 200),
	    (cases_regions_df['cases'] >= 200) & (cases_regions_df['cases'] < 300),
	    (cases_regions_df['cases'] >= 300)
	    ]
	# create a list of the values to assign for each condition
	valuesR = [88, 252, 252, 255, 252]
	valuesG = [163, 231, 92, 0, 0]
	valuesB = [92 ,171, 43, 0, 130]
	# create new R, G, B columns and use np.select to assign values to it using our lists as arguments
	cases_regions_df['R'] = np.select(conditions, valuesR)
	cases_regions_df['G'] = np.select(conditions, valuesG)
	cases_regions_df['B'] = np.select(conditions, valuesB)
	#####create geodataframe for json polygon layer
	cases_regions_gdf=gpd.read_file("./shapefiles/regions/regions.shp")[['region_nam','geometry']]
	cases_regions_gdf.columns=['region','geometry']
	cases_regions_gdf=cases_regions_gdf.merge(cases_regions_df,on='region', how='left')
	cases_regions_gdf.fillna(0,inplace=True)
	cases_regions_gdf['cases']=cases_regions_gdf['cases'].astype(int)
	#st.write(cases_regions_gdf)
	cases_regions_json=json.loads(cases_regions_gdf.to_json())
	polygons=pdk.Layer(
			'GeoJsonLayer',
			cases_regions_json,
			#pickable=True,
			opacity=1,
			stroke=True,
			filled=True,
	   		get_fill_color='[properties.R, properties.G, properties.B,150]',
    		get_line_color=[0, 0, 0],
			get_line_width=2000,)
	st.pydeck_chart(pdk.Deck(
		#map_provider=None,
		map_style='mapbox://styles/mapbox/light-v9',
		initial_view_state=pdk.ViewState(
		latitude=-23.4,
		longitude=17.7,
		zoom=3.5,
		height=250,
		pitch=0,
		bearing=0,),
		layers=[polygons]
		))


#----Defining columns
col4a, col4b,col4c= st.beta_columns([1,1,4])
col5a, col5b= st.beta_columns([1,1])
col6a, col6b= st.beta_columns([1,1])
col7a, col7b= st.beta_columns([1,1])


with col4a:
	st.header("Graphs")
with col4b:
	show=st.radio ('Show',('Daily','Weekly'),key="test1")
with col4c:
	st.write(' ')
	st.write(' ')
	expander_bar = st.beta_expander('Change date range')
	with expander_bar.form("my_form"):
		start_date= st.slider("Start time", min_value=first_date, max_value=last_date, value=first_date, step=None, format="DD-MM-YYYY" , key=None, help=None)
		end_date= st.slider("End time", min_value=first_date, max_value=last_date, value=last_date, step=None, format=None, key=None, help=None)
		submitted = st.form_submit_button("Submit")
		start_date_str=start_date.strftime('%Y-%m-%d')
		end_date_str=end_date.strftime('%Y-%m-%d')

#---------Daily and Weekly Cases-----------------------
with col5a:
	d_df=pd.read_sql(sa.text("SELECT cases_date,SUM(new_cases) FROM cases GROUP BY cases_date"), engine)
	daily_df=date_range.to_frame()
	daily_df.reset_index(drop=True, inplace=True)
	daily_df['cases_date']=daily_df['datetime'].dt.strftime('%Y-%m-%d')
	daily_df=pd.merge(daily_df,d_df,how = 'outer', on='cases_date')	
	daily_df=daily_df.fillna(0)
	daily_df['cases_week']=daily_df['datetime'].dt.strftime('%G-%V')
	daily_df['middle_weekday']=daily_df['cases_week']+'-4'
	daily_df['date_middle_weekday']=pd.to_datetime(daily_df['middle_weekday'],format='%G-%V-%u')
	daily_df['week_date']=daily_df['date_middle_weekday'].dt.strftime('%Y-%m-%d')
	daily_df['cumulative_cases'] = daily_df['SUM(new_cases)'].cumsum()
	daily_df['7day_average'] = daily_df['SUM(new_cases)'].rolling(window=7).mean()
	weekly_df=daily_df.groupby('cases_week',as_index=False).agg({"SUM(new_cases)": "sum","date_middle_weekday":"last","week_date":"last"})

	daily_range_df=daily_df.loc[(daily_df['cases_date'] >= start_date_str) & (daily_df['cases_date'] <= end_date_str)]
	weekly_range_df=weekly_df.loc[(weekly_df['week_date'] >= start_date_str) & (weekly_df['week_date'] <= end_date_str)]

	if show=='Daily':
		chart_cases=alt.Chart(daily_range_df,height=250).mark_bar().encode(
		x=alt.X('datetime:T',title='Date'),
		y=alt.Y('SUM(new_cases):Q',title='No of Cases')).properties(
		title='Daily New Cases')

	elif show=='Weekly':
		chart_cases=alt.Chart(weekly_range_df,height=250).mark_bar().encode(
		x=alt.X('date_middle_weekday:T',title='Date'),
		y=alt.Y('SUM(new_cases):Q',title='No of Cases')).properties(
		title='Weekly New Cases')

	st.altair_chart(chart_cases, use_container_width=True)

with col5b:
	chart_cumulative_cases=alt.Chart(daily_range_df,height=250).mark_area(
	    line={'color':'darkblue'},
	    color=alt.Gradient(
	        gradient='linear',
	        stops=[alt.GradientStop(color='white', offset=0),
	               alt.GradientStop(color='darkblue', offset=1)],
	        x1=1,
	        x2=1,
	        y1=1,
	        y2=0
	    )).encode(
	    x=alt.X('datetime:T',title='Date'),
	    y=alt.Y('cumulative_cases:Q',title='No of Cases')).properties(
	    title='Cumulative Cases')
	st.altair_chart(chart_cumulative_cases, use_container_width=True)


#---------Daily and Weekly Deaths-----------------------
with col6a:
	d_df=pd.read_sql(sa.text("SELECT death_date,COUNT(*) FROM deaths GROUP BY death_date"), engine)
	daily_deaths_df=date_range.to_frame()
	daily_deaths_df.reset_index(drop=True, inplace=True)
	daily_deaths_df['death_date']=daily_deaths_df['datetime'].dt.strftime('%Y-%m-%d')
	daily_deaths_df=pd.merge(daily_deaths_df,d_df,how = 'outer', on='death_date')	
	daily_deaths_df=daily_deaths_df.fillna(0)
	daily_deaths_df['deaths_datetime']= pd.to_datetime(daily_deaths_df['death_date'],format='%Y-%m-%d')
	daily_deaths_df['deaths_week']=daily_deaths_df['deaths_datetime'].dt.strftime('%G-%V')
	daily_deaths_df['middle_weekday']=daily_deaths_df['deaths_week']+'-4'
	daily_deaths_df['date_middle_weekday']=pd.to_datetime(daily_deaths_df['middle_weekday'],format='%G-%V-%u')
	daily_deaths_df['week_date']=daily_deaths_df['date_middle_weekday'].dt.strftime('%Y-%m-%d')
	daily_deaths_df['cumulative_deaths'] = daily_deaths_df['COUNT(*)'].cumsum()
	weekly_deaths_df=daily_deaths_df.groupby('deaths_week',as_index=False).agg({"COUNT(*)": "sum","date_middle_weekday":"last","week_date":"last"})

	daily_deaths_range_df=daily_deaths_df.loc[(daily_deaths_df['death_date'] >= start_date_str) & (daily_deaths_df['death_date'] <= end_date_str)]
	weekly_deaths_range_df=weekly_deaths_df.loc[(weekly_deaths_df['week_date'] >= start_date_str) & (weekly_deaths_df['week_date'] <= end_date_str)]

	if show=='Daily':
		chart_deaths=alt.Chart(daily_deaths_range_df,height=250).mark_bar(color='brown').encode(
	    x=alt.X('deaths_datetime:T',title='Date'),
	    y=alt.Y('COUNT(*):Q',title='No of Deaths')).properties(
	    title='Daily New Deaths')
	elif show=='Weekly':
		chart_deaths=alt.Chart(weekly_deaths_range_df,height=250).mark_bar(color='brown').encode(
	    x=alt.X('date_middle_weekday:T',title='Date'),
	    y=alt.Y('COUNT(*):Q',title='No of Deaths')).properties(
	    title='Weekly New Deaths')
	st.altair_chart(chart_deaths, use_container_width=True)

with col6b:
	chart_cumulative_deaths=alt.Chart(daily_deaths_range_df,height=250).mark_area(
	    line={'color':'darkred'},
	    color=alt.Gradient(
	        gradient='linear',
	        stops=[alt.GradientStop(color='white', offset=0),
	               alt.GradientStop(color='darkred', offset=1)],
	        x1=1,
	        x2=1,
	        y1=1,
	        y2=0
	    )).encode(
	    x=alt.X('datetime:T',title='Date'),
	    y=alt.Y('cumulative_deaths:Q',title='No of Deaths')).properties(
	    title='Cumulative Deaths')
	st.altair_chart(chart_cumulative_deaths, use_container_width=True)


###-------------Active Cases------------------------
with col7a:

	#check!!!
	#start_date=first_date
	#end_date=last_date
	#cases already available as df, other dfs from SQL (deaths df different: date = death_date not published_date)
	d_df=daily_df[['cases_date','SUM(new_cases)']]
	d_df=d_df.rename(columns={'cases_date': 'date'})
	deaths_df=pd.read_sql(sa.text("SELECT publish_date,COUNT(*) FROM deaths where publish_date>=:first_date and publish_date<=:last_date GROUP BY publish_date"), engine, params={"first_date": first_date,"last_date": last_date})
	deaths_df=deaths_df.rename(columns={'publish_date':'date'})
	recoveries_df=pd.read_sql(sa.text("SELECT recoveries_date,SUM(new_recoveries) FROM recoveries where recoveries_date>=:first_date and recoveries_date<=:last_date GROUP BY recoveries_date"), engine, params={"first_date": first_date,"last_date": last_date})
	recoveries_df=recoveries_df.rename(columns={'recoveries_date':'date'})
	missing_df=pd.read_sql(sa.text("SELECT missing_date,SUM(missing_cases) FROM missing where missing_date>=:first_date and missing_date<=:last_date GROUP BY missing_date"), engine, params={"first_date": first_date,"last_date": last_date})
	missing_df=missing_df.rename(columns={'missing_date':'date'})

	active_cases_df=date_range.to_frame()
	active_cases_df.reset_index(drop=True, inplace=True)
	active_cases_df['date']=active_cases_df['datetime'].dt.strftime('%Y-%m-%d')
	active_cases_df=pd.merge(active_cases_df,d_df,how = 'outer', on='date')	
	active_cases_df=pd.merge(active_cases_df,recoveries_df,how = 'outer', on='date')	
	active_cases_df=pd.merge(active_cases_df,deaths_df,how = 'outer', on='date')	
	active_cases_df=pd.merge(active_cases_df,missing_df,how = 'outer', on='date')	
	active_cases_df=active_cases_df.fillna(0)
	cols = ['SUM(new_cases)', 'SUM(new_recoveries)','COUNT(*)','SUM(missing_cases)']
	active_cases_df.loc[:, cols] = active_cases_df.loc[:, cols].cumsum()
	active_cases_df['active_cases']=active_cases_df['SUM(new_cases)']-active_cases_df['SUM(new_recoveries)']-active_cases_df['COUNT(*)']-active_cases_df['SUM(missing_cases)']

	active_cases_range_df=active_cases_df.loc[(active_cases_df['date'] >= start_date_str) & (active_cases_df['date'] <= end_date_str)]

	chart_active_cases=alt.Chart(active_cases_range_df,height=250).mark_bar(color='green').encode(
	    x=alt.X('date:T',title='Date'),
	    y=alt.Y('active_cases',title='Active Cases')
		).properties(
	    title='Daily Active Cases')
	st.altair_chart(chart_active_cases, use_container_width=True)


with col7b:
	region='Khomas'
	total_hospital_df=pd.read_sql(sa.text("SELECT hospital_date,SUM(hospital_cases) FROM hospitalization GROUP BY hospital_date"), engine)
	total_hospital_df['Hospital Cases']='Total'
	total_hospital_df=total_hospital_df.rename(columns={'SUM(hospital_cases)':'Cases'})
	total_icu_df=pd.read_sql(sa.text("SELECT hospital_date,SUM(icu_cases) FROM hospitalization GROUP BY hospital_date"), engine)
	total_icu_df['Hospital Cases']='Total ICU'
	total_icu_df=total_icu_df.rename(columns={'SUM(icu_cases)':'Cases'})
	khomas_hospital_df=pd.read_sql(sa.text("SELECT hospital_date,hospital_cases FROM hospitalization where region=:region"), engine,params={"region": region})
	khomas_hospital_df['Hospital Cases']='Khomas'
	khomas_hospital_df=khomas_hospital_df.rename(columns={'hospital_cases':'Cases'})
	khomas_icu_df=pd.read_sql(sa.text("SELECT hospital_date,icu_cases FROM hospitalization where region=:region"), engine,params={"region": region})
	khomas_icu_df['Hospital Cases']='Khomas ICU'
	khomas_icu_df=khomas_icu_df.rename(columns={'icu_cases':'Cases'})

	hospital_df = pd.concat([total_hospital_df,total_icu_df,khomas_hospital_df,khomas_icu_df])
	hospital_df.reset_index(drop=True)
	#st.write(hospital_df)
	chart_hospital_cases=alt.Chart(hospital_df,height=250).mark_line().encode(
		x=alt.X('hospital_date:T',title='Date'),
		y='Cases',
		#color='Hospital Cases',
		color=alt.Color('Hospital Cases',
				scale=alt.Scale(
					range=['lightgreen','darkorange','green', 'red']))).properties(title='Hospital Cases')
		
	st.altair_chart(chart_hospital_cases, use_container_width=True)

st.markdown("---")
##------------Daily Cases by district------------------------------------------

col8a, col8b,col8c= st.beta_columns([1,3,3])

with col8a:
	col8a.subheader('Daily Cases by District')
	districts_sorted = districts_df['district'].sort_values().reset_index(drop=True)
	selected_district=col8a.selectbox('Choose District', districts_sorted, index=34, key=None, help=None)
	d_df=pd.read_sql(sa.text("SELECT cases_date,district,SUM(new_cases) FROM cases where district=:district GROUP BY cases_date"), engine, params={"district": selected_district})
	district_daily_df=date_range.to_frame()
	district_daily_df.reset_index(drop=True, inplace=True)
	district_daily_df['cases_date']=district_daily_df['datetime'].dt.strftime('%Y-%m-%d')
	district_daily_df=pd.merge(district_daily_df,d_df,how = 'outer', on='cases_date')	
	district_daily_df=district_daily_df.fillna(0)
	district_daily_df['cases_week']=district_daily_df['datetime'].dt.strftime('%G-%V')
	district_daily_df['middle_weekday']=district_daily_df['cases_week']+'-4'
	district_daily_df['date_middle_weekday']=pd.to_datetime(district_daily_df['middle_weekday'],format='%G-%V-%u')
	district_daily_df['week_date']=district_daily_df['date_middle_weekday'].dt.strftime('%Y-%m-%d')

	district_weekly_df=district_daily_df.groupby('cases_week',as_index=False).agg({"SUM(new_cases)": "sum","date_middle_weekday":"last","week_date":"last"})

	district_daily_range_df=district_daily_df.loc[(daily_df['cases_date'] >= start_date_str) & (district_daily_df['cases_date'] <= end_date_str)]
	district_weekly_range_df=district_weekly_df.loc[(weekly_df['week_date'] >= start_date_str) & (district_weekly_df['week_date'] <= end_date_str)]
	
with col8b:
	title_daily='Daily New Cases: District '+selected_district
	chart_cases_daily=alt.Chart(district_daily_range_df,height=250).mark_bar().encode(
		x=alt.X('datetime:T',title='Date'),
		y=alt.Y('SUM(new_cases):Q',title='No of Cases')).properties(
		title=title_daily)
	st.altair_chart(chart_cases_daily, use_container_width=True)

with col8c:
	title_weekly='Weeky New Cases: District '+selected_district
	chart_cases_weekly=alt.Chart(district_weekly_range_df,height=250).mark_bar().encode(
		x=alt.X('date_middle_weekday:T',title='Date'),
		y=alt.Y('SUM(new_cases):Q',title='No of Cases')).properties(
		title=title_weekly)
	st.altair_chart(chart_cases_weekly, use_container_width=True)



with col7b:
	ifilename='./images/'+selected_district+'.jpg'
	image = Image.open(ifilename)

	st.image(image, width=250)

	jsonfilename='./json/'+selected_district+'.json'
	with open(jsonfilename) as json_file:
		onedistrict_json = json.load(json_file)

	polygons=pdk.Layer(
			'GeoJsonLayer',
			districts_json,
			pickable=False,
			opacity=1,
			stroke=True,
			filled=False,
	   		get_line_color=[0, 0, 0],
			get_line_width=2000,)
	polygon_district=pdk.Layer(
			'GeoJsonLayer',
			onedistrict_json,
			#pickable=True,
			opacity=1,
			stroke=True,
			filled=True,
	   		get_fill_color=[255, 0, 0, 100],
			#get_fill_color='[255, (1-properties.normal) * 255, properties.normal * 255]',
    		get_line_color=[255, 0, 0,255],
			get_line_width=5000,)
	st.pydeck_chart(pdk.Deck(
		map_style='mapbox://styles/mapbox/outdoors-v11',
		initial_view_state=pdk.ViewState(
		latitude=-23.4,
		longitude=17.7,
		zoom=3.5,
		width=250,
		height=250,
		pitch=0,
		bearing=0,),
		layers=[polygons,polygon_district]
		))
		




######################################################################

#---------------------------------#
# About
expander_bar = st.beta_expander('About this app')
expander_bar.markdown('''
- **Source Data:**  Facebook Page Ministry of Health and Social Services https://www.facebook.com/MoHSSNamibia/
- **by:** Sibylle Engelhard - African Geomatics  https://www.africangeomatics.com
''')

#---------------------------------#
#-----Close database
#connection.close()









with col8a:
	st.pydeck_chart(pdk.Deck(
		map_style='mapbox://styles/mapbox/outdoors-v11',
		initial_view_state=pdk.ViewState(
		latitude=-23,
		longitude=18,
		zoom=4),
		layers=[pdk.Layer(
				'ScatterplotLayer',
				data=cases_districts_df,
				get_position=['longitude', 'latitude'],
				#get_color='[0, 0, 255,160]',
				opacity=0.3,
        		stroked=True,
        		filled=True,
        		radius_scale=100000,
        		radius_min_pixels=2,
        		radius_max_pixels=60,
        		line_width_min_pixels=1,
       			get_radius='normal',
        		get_fill_color=[252, 136, 3,255],
        		get_line_color=[255,0,0],),
				]
			))

with col8b:
	disks=pdk.Layer(
   			 "ColumnLayer",
    		data=cases_districts_df,
    		get_position=['longitude', 'latitude'],
			radius=25000,
    		get_fill_color=['R', 'G', 'B', 150],
    		extruded=False,
    		stroked=True,
    		auto_highlight=True,
    		)
	columns=pdk.Layer(
   			 "ColumnLayer",
    		data=cases_districts_df,
    		get_position=['longitude', 'latitude'],
    		get_elevation='normal',
    		elevation_scale=300000,
    		radius=25000,
    		#get_fill_color='[255, 0, 0,180]',
    		get_fill_color=['R', 'G', 'B', 150],
    		#get_fill_color=[255, 'normal'*255,0, 255],
    		extruded=True,
    		stroked=True,
    		auto_highlight=True,
    		)
	polygons=pdk.Layer(
			'GeoJsonLayer',
			cases_districts_json,
			#pickable=True,
			opacity=0.3,
			stroke=True,
			filled=False,
	   		#get_fill_color=[255, 255, 0],
			get_fill_color='[255, (1-properties.normal) * 255, properties.normal * 255]',
    		get_line_color=[0, 0, 0],
			get_line_width=2000,
			)
	st.pydeck_chart(pdk.Deck(
		map_style='mapbox://styles/mapbox/streets-v11',
		initial_view_state=pdk.ViewState(
		latitude=-23,
		longitude=18,
		zoom=4,
		pitch=50,
		bearing=0,),
		layers=[polygons,disks,columns]
		))

with col8c:
	st.pydeck_chart(pdk.Deck(
			map_style='mapbox://styles/mapbox/outdoors-v11',
			initial_view_state=pdk.ViewState(
			latitude=-23,
			longitude=18,
			zoom=4),
			layers=[pdk.Layer(
					'GeoJsonLayer',
					cases_districts_json,
					#pickable=True,
					opacity=1,
					stroke=True,
					filled=True,
	   				#get_fill_color=[255, 255, 0],
					get_fill_color='[properties.R, properties.G, properties.B,150]',
    				get_line_color=[0, 0, 0],
					get_line_width=2000)]
			))











with col3c:
	st.markdown('<h3 style="margin-bottom:.2rem;margin-top:0rem;text-align: left">New Cases per District:</h3>', unsafe_allow_html=True)
	#st.subheader('New Cases per District:')
	districts_df = pd.read_csv('./csv/districts.csv')
	cases_districts_df=pd.read_sql(sa.text("SELECT SUM(new_cases),district FROM cases where cases_date=:display_date GROUP BY cases_date,district"), engine, params={"display_date": display_date})
	cases_districts_df=pd.merge(cases_districts_df,districts_df,how = 'right', on='district')	
	cases_districts_df=cases_districts_df.fillna(0)
	cases_districts_df=cases_districts_df.rename(columns={'SUM(new_cases)':'cases'})
	cases_districts_df['normal']=cases_districts_df['cases']/cases_districts_df['cases'].max()
	# create conditions for classification
	conditions = [
	    (cases_districts_df['cases'] == 0),
	    (cases_districts_df['cases'] > 0) & (cases_districts_df['cases'] < 50),
	    (cases_districts_df['cases'] >= 50) & (cases_districts_df['cases'] < 100),
	    (cases_districts_df['cases'] >= 100) & (cases_districts_df['cases'] < 200),
	    (cases_districts_df['cases'] >= 200)
	    ]
	# create a list of the values to assign for each condition
	valuesR = [88, 252, 255, 255, 252]
	valuesG = [163, 174, 62, 0, 0]
	valuesB = [92 ,104, 23, 0, 130]
	# create new R, G, B columns and use np.select to assign values to it using our lists as arguments
	cases_districts_df['R'] = np.select(conditions, valuesR)
	cases_districts_df['G'] = np.select(conditions, valuesG)
	cases_districts_df['B'] = np.select(conditions, valuesB)
	#####create geodataframe for json polygon layer
	cases_districts_gdf=gpd.read_file("health_districts_covid.shp")[['region','health_dis','geometry']]
	cases_districts_gdf.columns=['region','district','geometry']
	cases_districts_gdf=cases_districts_gdf.merge(cases_districts_df,on='district', how='left')
	cases_districts_gdf.fillna(0,inplace=True)
	cases_districts_gdf['cases']=cases_districts_gdf['cases'].astype(int)
	cases_districts_json=json.loads(cases_districts_gdf.to_json())

	circles=pdk.Layer(
				'ScatterplotLayer',
				data=cases_districts_df,
				get_position=['longitude', 'latitude'],
				#get_color='[0, 0, 255,160]',
				#opacity=0.3,
        		stroked=True,
        		filled=True,
        		radius_scale=200000,
        		radius_min_pixels=3,
        		radius_max_pixels=60,
        		line_width_min_pixels=1,
       			get_radius='normal',
        		get_fill_color=['R', 'G', 'B', 150],
        		get_line_color=['R', 'G', 'B', 255],)
	polygons=pdk.Layer(
			'GeoJsonLayer',
			cases_districts_json,
			#pickable=True,
			opacity=0.3,
			stroke=True,
			filled=False,
			#get_fill_color='[255, (1-properties.normal) * 255, properties.normal * 255]',
    		get_line_color=[0, 0, 0],
			get_line_width=3000,)
	st.pydeck_chart(pdk.Deck(
		map_style='mapbox://styles/mapbox/streets-v11',
		initial_view_state=pdk.ViewState(
		latitude=-23.4,
		longitude=17.7,
		zoom=3.5,
		width=250,
		height=250,
		pitch=0,
		bearing=0,),
		layers=[polygons,circles]
		))


with col7a:
	st.markdown('<h3 style="margin-bottom:0rem;margin-top:0rem;text-align: left">Daily Cases by District:</p>', unsafe_allow_html=True)
	districts_sorted = districts_df['district'].sort_values().reset_index(drop=True)
	selected_district=st.selectbox('Choose District', districts_sorted, index=34, key=None, help=None)
	d_df=pd.read_sql(sa.text("SELECT cases_date,district,SUM(new_cases) FROM cases where district=:district GROUP BY cases_date"), engine, params={"district": selected_district})
	district_daily_df=date_range.to_frame()
	district_daily_df.reset_index(drop=True, inplace=True)
	district_daily_df['cases_date']=district_daily_df['datetime'].dt.strftime('%Y-%m-%d')
	district_daily_df=pd.merge(district_daily_df,d_df,how = 'outer', on='cases_date')	
	district_daily_df=district_daily_df.fillna(0)
	district_daily_df['7day_average'] = district_daily_df['SUM(new_cases)'].rolling(window=7).mean()
	
	district_daily_range_df=district_daily_df.loc[(daily_df['cases_date'] >= start_date_str) & (district_daily_df['cases_date'] <= end_date_str)]
	
with col7b:
	district_gdf=cases_districts_gdf[cases_districts_gdf['district'] == selected_district]
	district_json=json.loads(district_gdf.to_json())
	polygons=pdk.Layer(
			'GeoJsonLayer',
			cases_districts_json,
			#pickable=True,
			opacity=1,
			stroke=True,
			filled=False,
	   		get_line_color=[0, 0, 0],
			get_line_width=2000,)
	polygon_district=pdk.Layer(
			'GeoJsonLayer',
			district_json,
			#pickable=True,
			opacity=1,
			stroke=True,
			filled=True,
	   		get_fill_color=[255, 0, 0, 100],
			#get_fill_color='[255, (1-properties.normal) * 255, properties.normal * 255]',
    		get_line_color=[255, 0, 0,255],
			get_line_width=5000,)
	st.pydeck_chart(pdk.Deck(
		map_style='mapbox://styles/mapbox/outdoors-v11',
		initial_view_state=pdk.ViewState(
		latitude=-23.4,
		longitude=17.7,
		zoom=3.5,
		width=250,
		height=250,
		pitch=0,
		bearing=0,),
		layers=[polygons,polygon_district]
		))

with col7c:
	title_daily=selected_district+': Daily New Cases and 7-Day Average'
	
	base = alt.Chart(district_daily_range_df,height=250).encode(x=alt.X('datetime:T',title='Date'))
	bar = base.mark_bar(color='#5696db').encode(y=alt.Y('SUM(new_cases):Q',title='No of Cases'))
	line = base.mark_line(color='darkblue').encode(y='7day_average').properties(title=title_daily)
	st.altair_chart(bar+line)




   

placeholder_button=st.empty()
button1=placeholder_button.button('Weekly',key='initial_state')
button2=False
	
if button1:
	placeholder_button.empty()
	button2=placeholder_button.button('Daily',key='initial_state')
		
if button2:
	placeholder_button.empty()
	button1=placeholder_button.button('Weekly',key='initial_state')
		


st.markdown("""---""")

districts_df=pd.read_sql(sa.text("SELECT DISTINCT district FROM districts ORDER BY district"), engine)
regions_df=pd.read_sql(sa.text("SELECT DISTINCT region FROM districts ORDER BY region"), engine)
#districts_df
#regions_df
#regions=st.sidebar.multiselect("Select Regions",regions_df['region'].unique())


"""
cases_df=pd.read_sql(sa.text("SELECT region,cases_date,new_cases FROM cases JOIN districts ON cases.district=districts.district  where cases_date>=:start_date and cases_date<=:end_date"), engine, params={"start_date": start_date,"end_date": end_date})
c4=alt.Chart(cases_df).mark_bar().encode(
x=alt.X('cases_date:T',axis=alt.Axis(format='%M', title='Date')),
y=alt.Y('new_cases:Q',title='No of Cases'))
st.altair_chart(c4, use_container_width=True)	
"""
#titanic[["Age", "Sex"]]

#st.markdown("""---""")