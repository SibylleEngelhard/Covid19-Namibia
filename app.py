from datetime import datetime
from datetime import timedelta
import altair as alt

import streamlit as st
from PIL import Image
import pandas as pd
import numpy as np

from sqlalchemy import create_engine
import sqlalchemy as sa
import pydeck as pdk
#import json

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
#last_date_str='2021-01-15'
last_date=datetime.strptime(last_date_str, '%Y-%m-%d').date() 
last_date_minus7=last_date-timedelta(days = 7)
last_date_minus7_str=last_date_minus7.strftime('%Y-%m-%d')
date_range = pd.date_range(start=first_date,end=last_date,name="datetime")
population_nam=2584291
population_whk=445745

#---- Title 
st.markdown('<h1 style="margin-bottom:0rem;margin-top:0rem;text-align: center">Covid19 Data - Namibia</h1>', unsafe_allow_html=True)
st.markdown(f'<h3 style="margin-bottom:0rem;margin-top:0rem;text-align: center">Last update: {last_date.strftime("%A, %d %B %Y")}</h3>', unsafe_allow_html=True)

#----menu button invisible
st.markdown(""" <style>#MainMenu {visibility: hidden;}footer {visibility: hidden;}</style> """, unsafe_allow_html=True)

# get dataframe from database tables

cases_df=pd.read_sql(sa.text("SELECT * FROM cases"), engine)
recoveries_df=pd.read_sql(sa.text("SELECT * FROM recoveries"), engine)
deaths_df=pd.read_sql(sa.text("SELECT * FROM deaths"), engine)
hospitalization_df=pd.read_sql(sa.text("SELECT * FROM hospitalization"), engine)
missing_df=pd.read_sql(sa.text("SELECT * FROM missing"), engine)
districts_regions_df=pd.read_sql(sa.text("SELECT * FROM districts"), engine)
cases_region_df=pd.merge(cases_df,districts_regions_df,how = 'left', on='district')	

#----Total Cases, Daily Cases, Tables, Cases per districts map
col3a,col3b,col3c,col3d= st.beta_columns([2,2,3,3])

with col3a:
	st.markdown('<h3 style="margin-bottom:.2rem;margin-top:0rem;text-align:center">Total Cases:</h3>', unsafe_allow_html=True)
	#Daily Total Cases
	total_all_cases=cases_df[cases_df.cases_date <= last_date_str][['new_cases']].sum()[0]
	total_all_cases_7daysago=cases_df[cases_df.cases_date <= last_date_minus7_str][['new_cases']].sum()[0]
	sevenday_incidence=int(round((total_all_cases-total_all_cases_7daysago)/population_nam*100000,0))
	st.write('Total cases: '+str(total_all_cases))
	
	#Daily Total Recoveries
	total_all_recoveries=recoveries_df[recoveries_df.recoveries_date <= last_date_str][['new_recoveries']].sum()[0]
	if not total_all_recoveries:
		total_all_recoveries=0
	st.write('Total recoveries: '+str(total_all_recoveries))   
	#Daily Total Deaths
	total_all_deaths=deaths_df[deaths_df.publish_date <= last_date_str].count()[0]
	st.write('Total deaths: '+str(total_all_deaths))   
	#Active Cases
	total_missing_cases=missing_df[missing_df.missing_date <= last_date_str][['missing_cases']].sum()[0]
	total_active_cases=total_all_cases-total_all_recoveries-total_all_deaths-total_missing_cases
	st.write('Active cases: '+str(total_active_cases)) 
	st.text('')  

with col3b:
	st.markdown('<h3 style="margin-bottom:.2rem;margin-top:0rem;text-align:center">Daily Cases:</h3>', unsafe_allow_html=True)
	#Daily New Cases
	total_new_cases=cases_df[cases_df.cases_date == last_date_str][['new_cases']].sum()[0]
	
	st.write('New cases: '+str(total_new_cases))
	
	#Daily New Recoveries
	total_new_recoveries=recoveries_df[recoveries_df.recoveries_date == last_date_str][['new_recoveries']].sum()[0]
	st.write('Recoveries: '+str(int(total_new_recoveries)))
	#Daily Neww Deaths
	total_new_deaths=deaths_df[deaths_df.publish_date == last_date_str].count()[0]
	st.write('Deaths: '+str(total_new_deaths))
	st.markdown('<style>p{margin-bottom:.1rem;margin-top:.1rem;text-align: center;}</style>',unsafe_allow_html=True)
	
	total_cases_whk=cases_df[(cases_df.cases_date <= last_date_str)&(cases_df.district=='Windhoek')][['new_cases']].sum()[0]
	total_cases_whk_7daysago=cases_df[(cases_df.cases_date <= last_date_minus7_str)&(cases_df.district=='Windhoek')][['new_cases']].sum()[0]
	sevenday_incidence_whk=int(round((total_cases_whk-total_cases_whk_7daysago)/population_whk*100000,0))
	#st.write(total_cases_whk-total_cases_whk_7daysago)
	st.write('7-Day Incidence: '+str(sevenday_incidence))
	st.write('7-Day Incidence Windhoek: '+str(sevenday_incidence_whk))

with col3c:
	st.markdown(f'<h3 style="margin-bottom:0rem;margin-top:0rem;text-align: center">{last_date.strftime("%d %B %Y")}</h3>', unsafe_allow_html=True)
	st.text('')
	new_cases=cases_region_df[cases_region_df.cases_date == last_date_str][['region','district','new_cases']]
	new_cases=new_cases.rename(columns={'region':'Region','district':'District','new_cases':'New Cases'})
	region_cases=new_cases.groupby(['Region'],as_index=False)['New Cases'].sum()
	region_cases=region_cases.rename(columns={'New Cases':'Region Cases'})
	new_cases=pd.merge(new_cases,region_cases,how = 'left', on='Region')	
	new_cases=new_cases.sort_values(['Region Cases','New Cases'], ascending = (False, False))
	new_deaths=deaths_df[deaths_df.publish_date == last_date_str][['district','sex','age','comorbidities','death_date','classification']]
	new_deaths=new_deaths.rename(columns={'district':'District','sex':'Sex','age':'Age','comorbidities':'Comorbidities','death_date':'Date of Death','classification':'Classification'})
	new_deaths=new_deaths.sort_values(['District','Date of Death'], ascending = (True, True))
	new_deaths.reset_index(drop=True, inplace=True)
	new_hospital_cases=hospitalization_df[hospitalization_df.hospital_date == last_date_str][['region','hospital_cases','icu_cases','high_care']].sort_values('hospital_cases', ascending=False)
	new_hospital_cases=new_hospital_cases.rename(columns={'region':'Region','hospital_cases':'Hospital Cases','icu_cases':'ICU','high_care':'High Care'})
	
	new_hospital_cases.reset_index(drop=True, inplace=True)
	expander1 = st.beta_expander('New Cases')
	expander1.write(new_cases[['Region','District','New Cases']])
	expander2 = st.beta_expander('Hospital Cases')
	expander2.write(new_hospital_cases[['Region','Hospital Cases','ICU']])
	#expander3 = st.beta_expander('Deaths')
	#expander3.write(new_deaths)

with col3d:
	st.markdown('<h3 style="margin-bottom:.2rem;margin-top:0rem;text-align: left">New Cases per District:</h3>', unsafe_allow_html=True)
	districts_df = pd.read_csv('./csv/districts.csv')
	new_cases_districts_df=cases_df[cases_df.cases_date == last_date_str][['district','new_cases']]
	new_cases_districts_df=pd.merge(new_cases_districts_df,districts_df,how = 'right', on='district')	
	new_cases_districts_df=new_cases_districts_df.fillna(0)
	if total_new_cases==0:
		new_cases_districts_df['normal']=0.1
	else:
		new_cases_districts_df['normal']=new_cases_districts_df['new_cases']/new_cases_districts_df['new_cases'].max()
	# create conditions for classification
	conditions = [
	    (new_cases_districts_df['new_cases'] == 0),
	    (new_cases_districts_df['new_cases'] > 0) & (new_cases_districts_df['new_cases'] < 100),
	    (new_cases_districts_df['new_cases'] >= 100) & (new_cases_districts_df['new_cases'] < 200),
	    (new_cases_districts_df['new_cases'] >= 200)]
	# create a list of the values to assign for each condition
	valuesR = [88, 252,252, 255]
	valuesG = [163, 136, 136, 62]
	valuesB = [92 ,3, 3, 23]
	# create new R, G, B columns and use np.select to assign values to it using our lists as arguments
	new_cases_districts_df['R'] = np.select(conditions, valuesR)
	new_cases_districts_df['G'] = np.select(conditions, valuesG)
	new_cases_districts_df['B'] = np.select(conditions, valuesB)
	circles=pdk.Layer(
				'ScatterplotLayer',
				data=new_cases_districts_df,
				get_position=['longitude', 'latitude'],
				#get_color='[0, 0, 255,160]',
				#opacity=0.3,
        		pickable=False,
        		stroked=True,
        		filled=True,
        		radius_scale=150000,
        		radius_min_pixels=3,
        		line_width_min_pixels=1,
       			get_radius='normal',
        		get_fill_color=['R', 'G', 'B', 150],
        		get_line_color=['R', 'G', 'B', 200],)
	st.pydeck_chart(pdk.Deck(
		map_style='mapbox://styles/mapbox/streets-v11',
		initial_view_state=pdk.ViewState(
			latitude=-23.2,
			longitude=18.2,
			zoom=3.7,
			width=250,
			height=250,
			pitch=0,
			bearing=0,),
		layers=[circles]))

col4a, col4b,col4c= st.beta_columns([1,1,2])
with col4a:
	st.markdown('<h2 style="margin-bottom:0rem;margin-top:0rem;font-weight:bold;text-align: center">Charts</h2>', unsafe_allow_html=True)
with col4b:
	selection=st.radio ('Show',('Daily','Cumulative'),key="radio1")
with col4c:
	st.write(' ')
	st.write(' ')
	change_date = st.beta_expander('Change Date Range')
	with change_date.form("my_form"):
		start_date= st.slider("Start time", min_value=first_date, max_value=last_date, value=first_date, step=None, format="DD-MM-YYYY" , key=None, help=None)
		end_date= st.slider("End time", min_value=first_date, max_value=last_date, value=last_date, step=None, format=None, key=None, help=None)
		submitted = st.form_submit_button("Submit")
		start_date_str=start_date.strftime('%Y-%m-%d')
		end_date_str=end_date.strftime('%Y-%m-%d')


col5a, col5b= st.beta_columns([1,1])
#---------Daily and Cumulative  Cases-----------------------
with col5a:
	d_df=cases_df.groupby(['cases_date'],as_index=False)['new_cases'].sum()
	daily_df=date_range.to_frame()
	daily_df.reset_index(drop=True, inplace=True)
	daily_df['cases_date']=daily_df['datetime'].dt.strftime('%Y-%m-%d')
	daily_df=pd.merge(daily_df,d_df,how = 'outer', on='cases_date')	
	daily_df=daily_df.fillna(0)
	daily_df['cumulative_cases'] = daily_df['new_cases'].cumsum()
	daily_df['7day_average'] = daily_df['new_cases'].rolling(window=7).mean()
	daily_range_df=daily_df.loc[(daily_df['cases_date'] >= start_date_str) & (daily_df['cases_date'] <= end_date_str)]
	if selection=='Daily':
		base = alt.Chart(daily_range_df,height=250).encode(x=alt.X('datetime:T',title='Date'))
		bar = base.mark_bar().encode(y=alt.Y('new_cases:Q',title='No of Cases'))
		line = base.mark_line(color='darkblue').encode(y='7day_average').properties(title='Daily New Cases and 7-Day Average')
		st.altair_chart(bar+line)
	elif selection=='Cumulative':
		chart_cumulative_cases=alt.Chart(daily_range_df,height=250).mark_area(
	    	line={'color':'darkblue'},
		    color=alt.Gradient(
		        gradient='linear',
	    	    stops=[alt.GradientStop(color='#6bcdfa', offset=0),
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
	selection_d=st.radio ('Show Deaths By',('Date Published','Death Date'),key="radio2")
	if selection_d=='Date Published':
		d_df=deaths_df.groupby(['publish_date'],as_index=False)['classification'].count()
		d_df=d_df.rename(columns={'classification':'No of Deaths'})
		#d_df=pd.read_sql(sa.text("SELECT death_date,COUNT(*) FROM deaths GROUP BY death_date"), engine)
		daily_deaths_df=date_range.to_frame()
		daily_deaths_df.reset_index(drop=True, inplace=True)
		daily_deaths_df['publish_date']=daily_deaths_df['datetime'].dt.strftime('%Y-%m-%d')#date as string
		daily_deaths_df=pd.merge(daily_deaths_df,d_df,how = 'outer', on='publish_date')	
		daily_deaths_df=daily_deaths_df.fillna(0)
		daily_deaths_df['cumulative_deaths'] = daily_deaths_df['No of Deaths'].cumsum()
		daily_deaths_df['7day_average'] = daily_deaths_df['No of Deaths'].rolling(window=7).mean()
		last_date_minus7=last_date-timedelta(days = 7)
		daily_deaths_df.loc[pd.to_datetime(daily_deaths_df['datetime']).dt.date > last_date_minus7, '7day_average'] = None
		daily_deaths_range_df=daily_deaths_df.loc[(daily_deaths_df['publish_date'] >= start_date_str) & (daily_deaths_df['publish_date'] <= end_date_str)]
		if selection=='Daily':
			#base = alt.Chart(daily_deaths_range_df,height=250).encode(x=alt.X('datetime:T',title='Date of Death'))
			base = alt.Chart(daily_deaths_range_df,height=250).encode(x=alt.X('datetime:T',title='Publish Date'))
		
			bar = base.mark_bar(color='#f76e05').encode(y=alt.Y('No of Deaths:Q',title='No of Deaths'))
			line = base.mark_line(color='#94010e').encode(y='7day_average').properties(title='Daily Deaths and 7-Day Average')
			st.altair_chart(bar+line)
			st.write("different reporting format from MoHSS from 21 July 2021")
		elif selection=='Cumulative':
			chart_cumulative_deaths=alt.Chart(daily_deaths_range_df,height=250).mark_area(
			    line={'color':'#a80202'},
		    	color=alt.Gradient(
		        	gradient='linear',
		        	stops=[alt.GradientStop(color='#ff8e14', offset=0),
		               alt.GradientStop(color='red', offset=1)],
		        	x1=1,
		        	x2=1,
		        	y1=1,
		        	y2=0)).encode(
				x=alt.X('datetime:T',title='Publish Date'),
				y=alt.Y('cumulative_deaths:Q',title='No of Deaths')).properties(title='Cumulative Deaths')
			st.altair_chart(chart_cumulative_deaths)

	else:

		d_df=deaths_df.groupby(['death_date'],as_index=False)['classification'].count()
		d_df=d_df.rename(columns={'classification':'No of Deaths'})
		#d_df=pd.read_sql(sa.text("SELECT death_date,COUNT(*) FROM deaths GROUP BY death_date"), engine)
		daily_deaths_df=date_range.to_frame()
		daily_deaths_df.reset_index(drop=True, inplace=True)
		daily_deaths_df['death_date']=daily_deaths_df['datetime'].dt.strftime('%Y-%m-%d')#date as string
		daily_deaths_df=pd.merge(daily_deaths_df,d_df,how = 'outer', on='death_date')	
		daily_deaths_df=daily_deaths_df.fillna(0)
		daily_deaths_df['cumulative_deaths'] = daily_deaths_df['No of Deaths'].cumsum()
		daily_deaths_df['7day_average'] = daily_deaths_df['No of Deaths'].rolling(window=7).mean()
		last_date_minus7=last_date-timedelta(days = 7)
		daily_deaths_df.loc[pd.to_datetime(daily_deaths_df['datetime']).dt.date > last_date_minus7, '7day_average'] = None
		daily_deaths_range_df=daily_deaths_df.loc[(daily_deaths_df['death_date'] >= start_date_str) & (daily_deaths_df['death_date'] <= end_date_str)]
		if selection=='Daily':
			#base = alt.Chart(daily_deaths_range_df,height=250).encode(x=alt.X('datetime:T',title='Date of Death'))
			base = alt.Chart(daily_deaths_range_df,height=250).encode(x=alt.X('datetime:T',title='Date of Death (correct until 20_07_2021)'))
		
			bar = base.mark_bar(color='#f76e05').encode(y=alt.Y('No of Deaths:Q',title='No of Deaths'))
			line = base.mark_line(color='#94010e').encode(y='7day_average').properties(title='Daily Deaths and 7-Day Average')
			st.altair_chart(bar+line)
			st.write("different reporting format from MoHSS from 21 July 2021")
		elif selection=='Cumulative':
			chart_cumulative_deaths=alt.Chart(daily_deaths_range_df,height=250).mark_area(
			    line={'color':'#a80202'},
		    	color=alt.Gradient(
		        	gradient='linear',
		        	stops=[alt.GradientStop(color='#ff8e14', offset=0),
		               alt.GradientStop(color='red', offset=1)],
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
	#cases already available as df, other dfs from SQL (deaths_df not to be used because: date = death_date not published_date)
	daily_cases_df=daily_df[['cases_date','new_cases']]
	daily_cases_df=daily_cases_df.rename(columns={'cases_date': 'date'})
	daily_published_deaths_df=deaths_df.groupby(['publish_date'],as_index=False)['classification'].count()
	daily_published_deaths_df=daily_published_deaths_df.rename(columns={'publish_date':'date','classification':'No of Deaths'})
	daily_recoveries_df=recoveries_df.groupby(['recoveries_date'],as_index=False)['new_recoveries'].sum()
	daily_recoveries_df=daily_recoveries_df.rename(columns={'recoveries_date':'date'})
	daily_missing_df=missing_df.rename(columns={'missing_date':'date'})
	
	active_cases_df=date_range.to_frame()
	active_cases_df.reset_index(drop=True, inplace=True)
	active_cases_df['date']=active_cases_df['datetime'].dt.strftime('%Y-%m-%d')
	active_cases_df=pd.merge(active_cases_df,daily_cases_df,how = 'outer', on='date')	
	active_cases_df=pd.merge(active_cases_df,daily_recoveries_df,how = 'outer', on='date')	
	active_cases_df=pd.merge(active_cases_df,daily_published_deaths_df,how = 'outer', on='date')	
	active_cases_df=pd.merge(active_cases_df,daily_missing_df,how = 'outer', on='date')	
	active_cases_df=active_cases_df.fillna(0)
	cols = ['new_cases', 'new_recoveries','No of Deaths','missing_cases']
	active_cases_df.loc[:, cols] = active_cases_df.loc[:, cols].cumsum()
	active_cases_df['active_cases']=active_cases_df['new_cases']-active_cases_df['new_recoveries']-active_cases_df['No of Deaths']-active_cases_df['missing_cases']

	active_cases_range_df=active_cases_df.loc[(active_cases_df['date'] >= start_date_str) & (active_cases_df['date'] <= end_date_str)]

	chart_active_cases=alt.Chart(active_cases_range_df,height=250).mark_bar(color='green').encode(
	    x=alt.X('date:T',title='Date'),
	    y=alt.Y('active_cases',title='Active Cases')
		).properties(
	    title='Daily Active Cases')
	st.altair_chart(chart_active_cases)

###-------------Hospital Cases------------------------
with col6b:
	#region='Khomas'
	total_hospital_df=hospitalization_df.groupby(['hospital_date'],as_index=False)['hospital_cases'].sum()
	total_hospital_df['Hospital Cases']='Total'
	total_hospital_df=total_hospital_df.rename(columns={'hospital_cases':'Cases'})
	total_icu_df=hospitalization_df.groupby(['hospital_date'],as_index=False)['icu_cases'].sum()
	total_icu_df['Hospital Cases']='Total ICU'
	total_icu_df=total_icu_df.rename(columns={'icu_cases':'Cases'})
	khomas_hospital_df=hospitalization_df[hospitalization_df['region'] == 'Khomas'][['hospital_date','hospital_cases']]
	khomas_hospital_df['Hospital Cases']='Khomas'
	khomas_hospital_df=khomas_hospital_df.rename(columns={'hospital_cases':'Cases'})
	khomas_icu_df=hospitalization_df[hospitalization_df['region'] == 'Khomas'][['hospital_date','icu_cases']]
	khomas_icu_df['Hospital Cases']='Khomas ICU'
	khomas_icu_df=khomas_icu_df.rename(columns={'icu_cases':'Cases'})

	hospital_df = pd.concat([total_hospital_df,total_icu_df,khomas_hospital_df,khomas_icu_df])
	hospital_df.reset_index(drop=True)
	hospital_range_df=hospital_df.loc[(hospital_df['hospital_date'] >= start_date_str) & (hospital_df['hospital_date'] <= end_date_str)]

	chart_hospital_cases=alt.Chart(hospital_range_df,height=250).mark_line().encode(
		x=alt.X('hospital_date:T',title='Date'),
		y=alt.Y('Cases',title='No of Hospital Cases'),
		color=alt.Color('Hospital Cases',
			legend=alt.Legend(
				title='Hospital Cases',
				titleFontSize=15,
				titleFont='Arial',
				orient="top"),
			sort=['Total', 'Total ICU','Khomas','Khomas ICU'],
			scale=alt.Scale(
				range=['green','red','lightgreen','darkorange'])),
		)
	#.properties(title='Hospital Cases')
	st.altair_chart(chart_hospital_cases)


st.markdown("---")

###------------Daily Cases by district------------------------------------------
col7a, col7b,col7c= st.beta_columns([1,1,2])
with col7a:
	st.markdown('<h3 style="margin-bottom:0rem;margin-top:0rem;text-align: left">Daily Cases by District:</p>', unsafe_allow_html=True)
	districts_sorted = districts_df['district'].sort_values().reset_index(drop=True)
	selected_district=st.selectbox('Choose District', districts_sorted, index=34, key=None, help=None)
	d_df=cases_df[cases_df['district'] == selected_district][['cases_date','new_cases']]
	district_daily_df=date_range.to_frame()
	district_daily_df.reset_index(drop=True, inplace=True)
	district_daily_df['cases_date']=district_daily_df['datetime'].dt.strftime('%Y-%m-%d')
	district_daily_df=pd.merge(district_daily_df,d_df,how = 'outer', on='cases_date')	
	district_daily_df=district_daily_df.fillna(0)
	district_daily_df['7day_average'] = district_daily_df['new_cases'].rolling(window=7).mean()
	#total_cases_district=cases_df[(cases_df.cases_date <= last_date_str)&(cases_df.district==selected_district)][['new_cases']].sum()[0]
	#total_cases_district_7daysago=cases_df[(cases_df.cases_date <= last_date_minus7_str)&(cases_df.district==selected_district)][['new_cases']].sum()[0]
	#still needs population per district
	#sevenday_incidence_district=int(round((total_cases_district-total_cases_district_7daysago)/population_whk*100000,0))
	if selected_district=='Windhoek':
		st.write('7-Day Incidence: '+str(sevenday_incidence_whk))

	district_daily_range_df=district_daily_df.loc[(district_daily_df['cases_date'] >= start_date_str) & (district_daily_df['cases_date'] <= end_date_str)]
	
	min_district_cases=district_daily_range_df['new_cases'].min()
	t=district_daily_range_df[['cases_date','new_cases','7day_average']]

	#st.write(t.style.format({'new_cases':'{:.0f}','7day_average':'{:.0f}'}))
	
	
	de_df=deaths_df[deaths_df['district'] == selected_district][['death_date','district']]
	de_df=de_df.groupby(['death_date'],as_index=False)['district'].count()
	de_df=de_df.rename(columns={'district':'no_deaths'})
	district_deaths_df=date_range.to_frame()
	district_deaths_df.reset_index(drop=True, inplace=True)
	district_deaths_df['death_date']=district_deaths_df['datetime'].dt.strftime('%Y-%m-%d')
	district_deaths_df=pd.merge(district_deaths_df,de_df,how = 'outer', on='death_date')	
	district_deaths_df=district_deaths_df.fillna(0)
	district_deaths_df['7day_average'] = district_deaths_df['no_deaths'].rolling(window=7).mean()
	district_deaths_df.loc[pd.to_datetime(district_deaths_df['datetime']).dt.date > last_date_minus7, '7day_average'] = None
	district_deaths_range_df=district_deaths_df.loc[(district_deaths_df['death_date'] >= start_date_str) & (district_deaths_df['death_date'] <= end_date_str)]



with col7b:
	image_filename='./images/'+selected_district+'.jpg'
	image = Image.open(image_filename)
	st.image(image, width=230)

with col7c:
	title_daily=selected_district+': Daily New Cases and 7-Day Average'
	base = alt.Chart(district_daily_range_df,height=250).encode(x=alt.X('datetime:T',title='Date'))
	bar = base.mark_bar(color='#5696db').encode(y=alt.Y('new_cases:Q',title='No of Cases'))
	line = base.mark_line(color='darkblue').encode(y='7day_average').properties(title=title_daily)
	st.altair_chart(bar+line)
	title_deaths=selected_district+': Daily Deaths and 7-Day Average'
	base2 = alt.Chart(district_deaths_range_df,height=250).encode(x=alt.X('datetime:T',title='Date'))
	bar2 = base2.mark_bar(color='#f76e05').encode(y=alt.Y('no_deaths:Q',title='No of Deaths'))
	line2 = base2.mark_line(color='#94010e').encode(y='7day_average').properties(title=title_deaths)
	#st.altair_chart(bar2+line2)


######################################################################
#---------------------------------#
# About
expander_bar = st.beta_expander('About this app')
expander_bar.markdown('''
- **Source Data:**  Facebook Page - Ministry of Health and Social Services https://www.facebook.com/MoHSSNamibia/
- **Population Data for 7-Day Incidence:**  Namibia 2021: 2584291 - https://www.worldometers.info/world-population/namibia-population/  
        Windhoek 2021: 445745 - https://worldpopulationreview.com/world-cities/windhoek-population
- No warranty is given that the information provided in this app is free of errors.
- for info contact: s.engelhard@gmx.net
- updating of the database was stopped in February 2022
''')
#---------------------------------#

