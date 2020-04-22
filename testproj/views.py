
from django.http import HttpResponse
from django.shortcuts import render
from django.utils.html import escape
import requests
import pandas as pd

def dayssincelastcaseindistrict():
    filename = 'https://api.covid19india.org/raw_data.json'
    d = requests.get(filename)
    js = d.json()
    df = pd.DataFrame(js['raw_data'])
    df = df.loc[df['dateannounced'] != ''].loc[df['detectedstate'] != 'Delhi']
    df['dateannounced'] = pd.to_datetime(df['dateannounced'],format='%d/%m/%Y')
    df['dayssincelastcase'] = (pd.datetime.now() - df['dateannounced']).astype('timedelta64[D]')
    df_countbydistrict = df.sort_values('dateannounced', ascending=False).groupby('detecteddistrict')['patientnumber'].nunique().reset_index()
    df_countbydistrict.columns = ['detecteddistrict','count']
    df_recovery = df.sort_values('dateannounced', ascending=False).drop_duplicates(['detecteddistrict'])[['detecteddistrict','dateannounced','dayssincelastcase','detectedstate']]
    df_recovery.sort_values('detecteddistrict')
    df_final = df_recovery.merge(df_countbydistrict,on='detecteddistrict')
    df_india = df_final.sort_values('dayssincelastcase',ascending=False)
    df_kerala = df_final.loc[df_final['detectedstate'].isin(['Kerala'])].sort_values('dayssincelastcase',ascending=False)
    states = df_india['detectedstate'].unique()
    districts = df_kerala['detecteddistrict'].unique()
    return df_final, df_india.to_html(), sorted(districts), sorted(states)


def home(request):
    return render(request, 'home.html', {'states': dayssincelastcaseindistrict()[3]})

def count(request):
    state = request.GET['states']

    df_final = dayssincelastcaseindistrict()[0]
    df_state = df_final.loc[df_final['detectedstate'].isin([state])].sort_values('dayssincelastcase', ascending=False)
    return render(request, 'count.html', {'statetotal': df_state.to_html(escape=False)})
