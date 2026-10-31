from pathlib import Path
import pandas as pd
BASE=Path(__file__).resolve().parent
FUENTE=BASE/'fuentes'
def preparar():
 d=pd.read_excel(FUENTE/'Anexo1.NoFetal2019_CE_15-03-23.xlsx',sheet_name=0,dtype={'COD_DANE':str,'COD_DEPARTAMENTO':str,'COD_MUERTE':str})
 g=pd.read_excel(FUENTE/'Divipola_CE_.xlsx',sheet_name='Hoja1',dtype=str)
 g=g[['COD_DANE','DEPARTAMENTO','MUNICIPIO']].drop_duplicates('COD_DANE')
 d=d.merge(g,on='COD_DANE',how='left',validate='many_to_one')
 d['DEPARTAMENTO']=d.DEPARTAMENTO.fillna('Sin correspondencia');d['MUNICIPIO']=d.MUNICIPIO.fillna('Sin correspondencia')
 d['ciudad']=d.MUNICIPIO+' · '+d.DEPARTAMENTO
 d['COD_MUERTE']=d.COD_MUERTE.str.strip().str.upper().str.replace('.','',regex=False)
 catalogo=pd.read_excel(FUENTE/'Anexo2.CodigosDeMuerte_CE_15-03-23.xlsx',header=8)
 # Priorizar la descripción exacta de cuatro caracteres; completar con códigos de tres.
 partes=[]
 for posiciones in ([4,5],[2,3]):
  parte=catalogo.iloc[:,posiciones].copy()
  parte.columns=['COD_MUERTE','causa']
  parte=parte.dropna()
  parte['COD_MUERTE']=parte.COD_MUERTE.astype(str).str.strip().str.upper().str.replace('.','',regex=False)
  parte['causa']=parte.causa.astype(str).str.strip()
  partes.append(parte)
 c=pd.concat(partes,ignore_index=True).drop_duplicates('COD_MUERTE')
 d=d.merge(c,on='COD_MUERTE',how='left',validate='many_to_one');d['causa']=d.causa.fillna('Código sin descripción en catálogo')
 cols=['COD_DANE','COD_DEPARTAMENTO','DEPARTAMENTO','ciudad','MES','SEXO','GRUPO_EDAD1','COD_MUERTE','causa']
 d=d.groupby(cols,dropna=False).size().reset_index(name='casos');d.to_csv(BASE/'data/mortalidad.csv.gz',index=False,compression='gzip')
 geo=pd.read_excel(FUENTE/'Divipola_CE_.xlsx',sheet_name='Hoja3',header=1,dtype=str)
 geo.columns=['departamento','nombre','codigo','municipio','tipo','lon','lat']
 for x in ['lon','lat']:geo[x]=pd.to_numeric(geo[x].str.replace(',','.',regex=False),errors='coerce')
 geo.groupby('departamento')[['lon','lat']].mean().reset_index().to_csv(BASE/'data/coordenadas.csv',index=False)
 print('Total',d.casos.sum(),'sin geografía',d.loc[d.DEPARTAMENTO=='Sin correspondencia','casos'].sum())
if __name__=='__main__':preparar()
