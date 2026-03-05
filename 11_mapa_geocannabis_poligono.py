import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("📐 DESENHANDO O POLÍGONO DA MACONHA E FINALIZANDO PERÍMETRO...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
    df = df.dropna(subset=['codigo_ibge']).copy()
except FileNotFoundError:
    print("❌ ERRO: Base não encontrada.")
    exit()

# 2. Coordenadas e Cruzamento
url_coordenadas = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coordenadas = pd.read_csv(url_coordenadas)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coordenadas['codigo_ibge'] = coordenadas['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coordenadas[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 3. Criação do Mapa Delimitado
limites_br = [[-34.5, -74.5], [5.5, -34.0]]
mapa = folium.Map(
    location=[-8.5, -39.0], # Centralizado mais ao NE para ver o Polígono de cara
    zoom_start=6, 
    tiles='cartodb positron',
    min_zoom=4,
    max_bounds=True,
    min_lat=limites_br[0][0], max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], max_lon=limites_br[1][1]
)

# --- CAMADA: POLÍGONO DA MACONHA ---
# Coordenadas aproximadas do polígono (Sertão de PE e BA)
coords_poligono = [
    [-8.1, -40.0], [-7.5, -39.0], [-8.0, -38.0], 
    [-9.0, -38.2], [-9.5, -39.5], [-9.0, -40.5]
]

folium.Polygon(
    locations=coords_poligono,
    color="orange",
    weight=2,
    fill=True,
    fill_color="yellow",
    fill_opacity=0.2, # Transparência suave como você pediu
    tooltip="Polígono da Maconha (Área de Concentração)"
).add_to(mapa)

# Texto flutuante "Polígono da Maconha"
folium.map.Marker(
    [-8.3, -39.2],
    icon=folium.DivIcon(
        icon_size=(150,36),
        icon_anchor=(0,0),
        html='<div style="font-size: 12pt; color: orange; font-weight: bold; opacity: 0.7;">POLÍGONO DA MACONHA</div>',
    )
).add_to(mapa)

# 4. Marcadores e Clusters
icon_url = "https://img.icons8.com/color/48/marijuana-leaf.png"
marker_cluster = MarkerCluster().add_to(mapa)

for index, row in df_mapa.iterrows():
    html_content = f"<b>{row['municipio_ibge']}</b><br>Pés: {row['Quantidade de pés encontrados']}"
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(25, 25)),
        tooltip=folium.Tooltip(html_content),
        popup=folium.Popup(html_content, max_width=200)
    ).add_to(marker_cluster)

# 5. Salvar
mapa.save('mapa_geocannabis_POLIGONO.html')
print("\n✅ MAPA COM POLÍGONO GERADO: 'mapa_geocannabis_POLIGONO.html'")