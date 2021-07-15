from datetime import datetime
from datetime import timedelta
import altair as alt

import streamlit as st
#from PIL import Image
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import sqlalchemy as sa
import pydeck as pdk
import json

#-----Page Configuration
st.set_page_config(page_title='Covid19 Data - Namibia',
    page_icon='🇳🇦',
    layout='wide',
    initial_sidebar_state='collapsed')

#-----Database connection---SQLalchemy
@st.cache(allow_output_mutation=True)
def get_database_connection():
    engine = create_engine("sqlite:///covid19_Nam.db")
    return engine
engine = get_database_connection()

#get from database date of first and last case entry
query=pd.read_sql(sa.text("SELECT MIN(cases_date) FROM cases"), engine)
first_date_str=query.iat[0,0]
first_date=datetime.strptime(first_date_str, '%Y-%m-%d').date() 
query=pd.read_sql(sa.text("SELECT MAX(cases_date) FROM cases"), engine)
last_date_str=query.iat[0,0]
last_date=datetime.strptime(last_date_str, '%Y-%m-%d').date() 

#display date for intern use and tests
display_date=last_date
#last_week_str=last_date.strftime('%G-%V')
#last_weekday_str=last_date.strftime('%u')
date_range = pd.date_range(start=first_date,end=last_date,name="datetime")

#---- Title 2
st.markdown('<h1 style="margin-bottom:0rem;margin-top:0rem;text-align: center">Covid19 Data - Namibia</h1>', unsafe_allow_html=True)
#image = Image.open('Nam.jpg')
#	st.image(image,width=50)
st.markdown(f'<h3 style="margin-bottom:0rem;margin-top:0rem;text-align: center">Last update: {last_date.strftime("%A, %d %B %Y")}</h3>', unsafe_allow_html=True)
#to change display date for tests
#display_date = st.date_input("Change Display Date",last_date)

#----menu button invisible
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)


#----Total Cases, Daily Cases, Cases per districts map
col3a,col3b,col3c,col3d= st.beta_columns([2,2,3,3])

with col3a:
	st.markdown('<h3 style="margin-bottom:.2rem;margin-top:0rem;text-align:center">Total Cases:</h3>', unsafe_allow_html=True)
	#st.text("currently displaying total on display date!!!")
	#Daily Total Cases
	q=pd.read_sql(sa.text("SELECT SUM(new_cases) FROM cases where cases_date<=:display_date"), engine, params={"display_date": display_date})
	daily_all_cases=q.iat[0,0]
	st.write('Total cases: '+str(daily_all_cases))
	#Daily Total Recoveries
	q=pd.read_sql(sa.text("SELECT SUM(new_recoveries) FROM recoveries WHERE recoveries_date <=:display_date"), engine, params={"display_date": display_date})
	daily_all_recoveries=q.iat[0,0]
	if not daily_all_recoveries:
		daily_all_recoveries=0
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
	st.text('')  

with col3b:
	st.markdown('<h3 style="margin-bottom:.2rem;margin-top:0rem;text-align:center">Daily Cases:</h3>', unsafe_allow_html=True)
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
	st.markdown('<style>p{margin-bottom:.1rem;margin-top:.1rem;text-align: center;}</style>',unsafe_allow_html=True)

with col3c:
	st.markdown(f'<h3 style="margin-bottom:0rem;margin-top:0rem;text-align: center">{last_date.strftime("%d %B %Y")}</h3>', unsafe_allow_html=True)
	st.text('')

	daily_cases=pd.read_sql(sa.text("SELECT region, cases.district,new_cases FROM cases JOIN districts ON cases.district=districts.district  where cases_date=:display_date ORDER BY region ASC,new_cases DESC"), engine, params={"display_date": display_date})
	daily_cases=daily_cases.rename(columns={'region':'Region','district':'District','new_cases':'New Cases'})
	deaths=pd.read_sql(sa.text("SELECT district,sex,age,comorbidities,death_date,classification FROM deaths WHERE publish_date=:display_date ORDER by district"), engine, params={"display_date": display_date})
	deaths=deaths.rename(columns={'district':'District','sex':'Sex','age':'Age','comorbidities':'Comorbidities','death_date':'Date of Death','classification':'Classification'})
	hospital_cases=pd.read_sql(sa.text("SELECT region,hospital_cases,icu_cases FROM hospitalization WHERE hospital_date=:display_date ORDER BY hospital_cases"), engine, params={"display_date": display_date})
	hospital_cases=hospital_cases.rename(columns={'region':'Region','hospital_cases':'Hospitalized Cases','icu_cases':'Intensive Care Unit'})
	
	expander1 = st.beta_expander('Show New Cases')
	expander1.write(daily_cases)
	expander2 = st.beta_expander('Show Hospital Cases')
	expander2.write(hospital_cases)
	expander3 = st.beta_expander('Show Deaths')
	expander3.write(deaths)

with col3d:
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
	valuesR = [88, 252, 255,255, 255]
	valuesG = [163, 174,112, 62, 0]
	valuesB = [92 ,104, 23, 23, 0]
	# create new R, G, B columns and use np.select to assign values to it using our lists as arguments
	cases_districts_df['R'] = np.select(conditions, valuesR)
	cases_districts_df['G'] = np.select(conditions, valuesG)
	cases_districts_df['B'] = np.select(conditions, valuesB)
	
	#####open json polygon layer
	with open('./json/districts.json') as json_file:
		districts_json = json.load(json_file)

	circles=pdk.Layer(
				'ScatterplotLayer',
				data=cases_districts_df,
				get_position=['longitude', 'latitude'],
				#get_color='[0, 0, 255,160]',
				#opacity=0.3,
        		pickable=False,
        		stroked=True,
        		filled=True,
        		radius_scale=200000,
        		radius_min_pixels=3,
        		#radius_max_pixels=60,
        		line_width_min_pixels=1,
       			get_radius='normal',
        		get_fill_color=['R', 'G', 'B', 150],
        		get_line_color=['R', 'G', 'B', 255],)
	polygons=pdk.Layer(
			'GeoJsonLayer',
			districts_json,
			pickable=False,
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
		views=pdk.View(
			controller=False,
			),
		layers=[polygons,circles]
		))

#q=pd.read_sql(sa.text("SELECT * FROM deaths WHERE age=:age"), engine, params={"age":0})
#st.write(q)	
col4a, col4b,col4c= st.beta_columns([1,1,2])
with col4a:
	st.markdown('<h2 style="margin-bottom:0rem;margin-top:0rem;font-weight:bold;text-align: center">Graphs</h2>', unsafe_allow_html=True)

with col4b:
	selection=st.radio ('Show',('Daily','Cumulative'),key="radio1")

with col4c:
	
	st.write(' ')
	st.write(' ')
	#st.button('Change date range')
	
		
	change_date = st.beta_expander('Change date range')
	with change_date.form("my_form"):
		start_date= st.slider("Start time", min_value=first_date, max_value=last_date, value=first_date, step=None, format="DD-MM-YYYY" , key=None, help=None)
		end_date= st.slider("End time", min_value=first_date, max_value=last_date, value=last_date, step=None, format=None, key=None, help=None)
		submitted = st.form_submit_button("Submit")
		start_date_str=start_date.strftime('%Y-%m-%d')
		end_date_str=end_date.strftime('%Y-%m-%d')


col5a, col5b= st.beta_columns([1,1])

#---------Daily and Cumulative  Cases-----------------------
with col5a:
	d_df=pd.read_sql(sa.text("SELECT cases_date,SUM(new_cases) FROM cases GROUP BY cases_date"), engine)
	daily_df=date_range.to_frame()
	daily_df.reset_index(drop=True, inplace=True)
	daily_df['cases_date']=daily_df['datetime'].dt.strftime('%Y-%m-%d')
	daily_df=pd.merge(daily_df,d_df,how = 'outer', on='cases_date')	
	daily_df=daily_df.fillna(0)
	daily_df['cumulative_cases'] = daily_df['SUM(new_cases)'].cumsum()
	daily_df['7day_average'] = daily_df['SUM(new_cases)'].rolling(window=7).mean()
	
	daily_range_df=daily_df.loc[(daily_df['cases_date'] >= start_date_str) & (daily_df['cases_date'] <= end_date_str)]
	if selection=='Daily':
		base = alt.Chart(daily_range_df,height=250).encode(x=alt.X('datetime:T',title='Date'))
		bar = base.mark_bar().encode(y=alt.Y('SUM(new_cases):Q',title='No of Cases'))
		line = base.mark_line(color='darkblue').encode(y='7day_average').properties(title='Daily New Cases and 7-Day Average')
		st.altair_chart(bar+line)
	elif selection=='Cumulative':
		chart_cumulative_cases=alt.Chart(daily_range_df,height=250).mark_area(
	    	line={'color':'darkblue'},
		    color=alt.Gradient(
		        gradient='linear',
	    	    stops=[alt.GradientStop(color='white', offset=0),
	               alt.GradientStop(color='darkblue', offset=1)],
	        	x1=1,
	        	x2=1,
	        	y1=1,
	        	y2=0)).encode(
	    	x=alt.X('datetime:T',title='Date'),
	    	y=alt.Y('cumulative_cases:Q',title='No of Cases')).properties(title='Cumulative Cases')
		st.altair_chart(chart_cumulative_cases)


#---------Daily and Cumulative Deaths-----------------------
with col5b:
	d_df=pd.read_sql(sa.text("SELECT death_date,COUNT(*) FROM deaths GROUP BY death_date"), engine)
	daily_deaths_df=date_range.to_frame()
	daily_deaths_df.reset_index(drop=True, inplace=True)
	daily_deaths_df['death_date']=daily_deaths_df['datetime'].dt.strftime('%Y-%m-%d')#date as string
	daily_deaths_df=pd.merge(daily_deaths_df,d_df,how = 'outer', on='death_date')	
	daily_deaths_df=daily_deaths_df.fillna(0)
	daily_deaths_df['cumulative_deaths'] = daily_deaths_df['COUNT(*)'].cumsum()
	daily_deaths_df['7day_average'] = daily_deaths_df['COUNT(*)'].rolling(window=7).mean()
	last_date_minus7=last_date-timedelta(days = 7)
	daily_deaths_df.loc[pd.to_datetime(daily_deaths_df['datetime']).dt.date > last_date_minus7, '7day_average'] = None
	daily_deaths_range_df=daily_deaths_df.loc[(daily_deaths_df['death_date'] >= start_date_str) & (daily_deaths_df['death_date'] <= end_date_str)]
	if selection=='Daily':
		base = alt.Chart(daily_deaths_range_df,height=250).encode(x=alt.X('datetime:T',title='Date of Death'))
		bar = base.mark_bar(color='#f76e05').encode(y=alt.Y('COUNT(*):Q',title='No of Deaths'))
		line = base.mark_line(color='#94010e').encode(y='7day_average').properties(title='Daily Deaths and 7-Day Average')
		st.altair_chart(bar+line)
	elif selection=='Cumulative':
		chart_cumulative_deaths=alt.Chart(daily_deaths_range_df,height=250).mark_area(
		    line={'color':'darkred'},
	    	color=alt.Gradient(
	        	gradient='linear',
	        	stops=[alt.GradientStop(color='white', offset=0),
	               alt.GradientStop(color='darkred', offset=1)],
	        	x1=1,
	        	x2=1,
	        	y1=1,
	        	y2=0)).encode(
			x=alt.X('datetime:T',title='Date of Death'),
			y=alt.Y('cumulative_deaths:Q',title='No of Deaths')).properties(title='Cumulative Deaths')
		st.altair_chart(chart_cumulative_deaths)
	

col6a, col6b= st.beta_columns([1,1])

###-------------Active Cases------------------------
with col6a:
	#check!!!
	#start_date=first_date
	#end_date=last_date
	#cases already available as df, other dfs from SQL (deaths_df not to be used because: date = death_date not published_date)
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
	st.altair_chart(chart_active_cases)

###-------------Hospital Cases------------------------
with col6b:
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
		
	st.altair_chart(chart_hospital_cases)

st.markdown("---")

###------------Daily Cases by district------------------------------------------
col7a, col7b,col7c= st.beta_columns([1,1,2])

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

with col7c:
	title_daily=selected_district+': Daily New Cases and 7-Day Average'
	
	base = alt.Chart(district_daily_range_df,height=250).encode(x=alt.X('datetime:T',title='Date'))
	bar = base.mark_bar(color='#5696db').encode(y=alt.Y('SUM(new_cases):Q',title='No of Cases'))
	line = base.mark_line(color='darkblue').encode(y='7day_average').properties(title=title_daily)
	st.altair_chart(bar+line)

######################################################################

#---------------------------------#
# About
expander_bar = st.beta_expander('About this app')
expander_bar.markdown('''
- **Source Data:**  Facebook Page Ministry of Health and Social Services https://www.facebook.com/MoHSSNamibia/
- for info or suggestions contact: ehasib47@gmail.com
''')
#---------------------------------#

