"""Tablero de mortalidad: cada conteo suma el peso casos del archivo agregado."""
from pathlib import Path
import os
import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output, dash_table
P=Path(__file__).resolve().parent
D=pd.read_csv(P/'data/mortalidad.csv.gz',dtype={'COD_DANE':str,'COD_DEPARTAMENTO':str})
G=pd.read_csv(P/'data/coordenadas.csv',dtype={'departamento':str})
GRUPOS=[('Neonatal',0,4),('Infantil',5,6),('Primera infancia',7,8),('Niñez',9,10),('Adolescencia',11,11),('Juventud',12,13),('Adultez temprana',14,16),('Adultez intermedia',17,19),('Vejez',20,24),('Longevidad',25,28),('Edad desconocida',29,29)]
D['edad']=D.GRUPO_EDAD1.map(lambda n:next((t for t,a,b in GRUPOS if a<=n<=b),'Fuera de referencia'))
D['sexo']=D.SEXO.map({1:'Hombre',2:'Mujer',3:'Indeterminado'}).fillna('Sin información')
app=Dash(__name__,title='Mortalidad Colombia 2019');server=app.server
app.layout=html.Main([
 html.Header([
  html.Small('UNIVERSIDAD DE LA SALLE'),
  html.H2('Maestría en Inteligencia Artificial', style={'fontSize':'24px','fontWeight':'500','margin':'12px 0 8px'}),
  html.P('Aplicaciones I · Actividad 4 · Trabajo grupal', style={'margin':'0 0 22px','color':'#c6e4e2'}),
  html.H1('Una mirada a la mortalidad'),
  html.P('Análisis interactivo de la mortalidad en Colombia · Año 2019', style={'margin':'8px 0 18px','color':'#c6e4e2'}),
  html.P('Integrantes: Eliana Pastor Merchan · Deivid Anderson Verano Fuentes', style={'marginBottom':'0'})
 ]),
 html.Div([html.Label('Departamento'),dcc.Dropdown(['Todos']+sorted(D.DEPARTAMENTO.unique()),'Todos',id='dep',clearable=False),html.Label('Sexo registrado'),dcc.Dropdown(['Todos']+sorted(D.sexo.unique()),'Todos',id='sexo',clearable=False)],className='filtros'),
 html.Div(id='total',className='indicador'),
 html.P('Conteos de defunciones del archivo suministrado. No representan tasas ni riesgo individual. Geografía según COD_DANE del anexo; no se asume residencia. X95 se usa como subconjunto de agresiones, no como totalidad de homicidios.'),
 html.Div([dcc.Graph(id=x) for x in ['mapa','mes','violencia','menor','sexo_dep','edad']],className='graficos'),
 html.H2('Las diez causas con más defunciones'),dash_table.DataTable(id='causas',columns=[{'name':'Código CIE-10','id':'COD_MUERTE'},{'name':'Causa','id':'causa'},{'name':'Casos','id':'casos'}],style_cell={'textAlign':'left','whiteSpace':'normal','height':'auto','padding':'12px'},style_header={'backgroundColor':'#dceee9','fontWeight':'bold'}),
 html.Footer('Fuente: anexos de la actividad · DANE EEVV 2019. Grupos de edad según la tabla de la consigna. Mapa de símbolos: posición media de las coordenadas municipales, no límites departamentales. El circular incluye municipios con registros positivos; porcentajes relativos a los diez seleccionados.')])
def sumar(d,cols):return d.groupby(cols,dropna=False).casos.sum().reset_index()
def figuras(dep,sexo):
 d=D[(D.DEPARTAMENTO.eq(dep) if dep!='Todos' else True)&(D.sexo.eq(sexo) if sexo!='Todos' else True)] if dep!='Todos' or sexo!='Todos' else D
 departamentos=sumar(d,['COD_DEPARTAMENTO','DEPARTAMENTO'])
 mapa=departamentos.merge(G,left_on='COD_DEPARTAMENTO',right_on='departamento',how='left').dropna(subset=['lat','lon'])
 f1=px.scatter_geo(mapa,lat='lat',lon='lon',size='casos',color='casos',hover_name='DEPARTAMENTO',size_max=40,title='Defunciones por departamento',color_continuous_scale='Teal')
 f1.update_geos(scope='south america',lataxis_range=[-5,14],lonaxis_range=[-82,-66],showcountries=True)
 meses=sumar(d,['MES']).set_index('MES').reindex(range(1,13),fill_value=0).reset_index()
 f2=px.line(meses,x='MES',y='casos',markers=True,title='Evolución mensual de las defunciones');f2.update_xaxes(dtick=1)
 top=sumar(d[d.COD_MUERTE.str.startswith('X95',na=False)],['ciudad']).sort_values(['casos','ciudad'],ascending=[False,True]).head(5)
 f3=px.bar(top,x='casos',y='ciudad',orientation='h',title='Cinco municipios con más agresiones X95');f3.update_yaxes(autorange='reversed')
 bajos=sumar(d[d.ciudad.str.startswith('Sin correspondencia')==False],['ciudad']).sort_values(['casos','ciudad']).head(10)
 f4=px.pie(bajos,names='ciudad',values='casos',hole=.55,title='Diez municipios con menos defunciones registradas')
 f5=px.bar(sumar(d,['DEPARTAMENTO','sexo']),x='DEPARTAMENTO',y='casos',color='sexo',title='Defunciones por sexo y departamento',barmode='stack')
 f6=px.histogram(d,x='edad',y='casos',histfunc='sum',category_orders={'edad':[x[0] for x in GRUPOS]+['Fuera de referencia']},title='Distribución por grupos de edad de la actividad');f6.update_layout(bargap=.04)
 for f in [f1,f2,f3,f4,f5,f6]:f.update_layout(template='plotly_white',font={'family':'Arial','size':12},margin={'l':45,'r':25,'t':65,'b':80},paper_bgcolor='white')
 tabla=sumar(d,['COD_MUERTE','causa']).sort_values(['casos','COD_MUERTE'],ascending=[False,True]).head(10)
 return f'{int(d.casos.sum()):,} defunciones en la selección',f1,f2,f3,f4,f5,f6,tabla.to_dict('records')
@app.callback([Output('total','children')]+[Output(x,'figure') for x in ['mapa','mes','violencia','menor','sexo_dep','edad']]+[Output('causas','data')],Input('dep','value'),Input('sexo','value'))
def actualizar(dep,sexo):return figuras(dep,sexo)
if __name__=='__main__':app.run(host='0.0.0.0',port=int(os.environ.get('PORT',8050)),debug=False)
