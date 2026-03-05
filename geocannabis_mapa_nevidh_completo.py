import pandas as pd
import folium
from folium.plugins import MarkerCluster, FloatImage

print("🦅 RENDERIZAÇÃO FINAL: INJETANDO TÍTULO CIENTÍFICO E FINALIZANDO OPERAÇÃO...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
    df = df.dropna(subset=['codigo_ibge']).copy()
except FileNotFoundError:
    print("❌ ERRO: Arquivo base não encontrado.")
    exit()

# 2. Geoprocessamento
url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coords = pd.read_csv(url_coords)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 3. Base Cartográfica Cercada
limites_br = [[-34.5, -74.5], [5.5, -34.0]]
mapa = folium.Map(
    location=[-14.2350, -51.9253], 
    zoom_start=4, 
    tiles='cartodb positron',
    control_scale=True,
    min_zoom=4,
    max_bounds=True,
    min_lat=limites_br[0][0], max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], max_lon=limites_br[1][1]
)

# 4. Elementos Cartográficos (Norte e Polígono)
url_norte = "https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Compass_rose_simple.svg/240px-Compass_rose_simple.svg.png"
FloatImage(url_norte, bottom=5, left=5).add_to(mapa)

coords_pol = [[-8.1, -40.2], [-7.5, -39.0], [-8.0, -37.8], [-9.2, -38.0], [-9.8, -39.5], [-9.2, -40.8]]
folium.Polygon(locations=coords_pol, color="orange", weight=1, fill=True, fill_color="yellow", fill_opacity=0.1).add_to(mapa)

# 5. Marcadores e Fichas Técnicas
icon_url = "https://img.icons8.com/color/48/marijuana-leaf.png"
marker_cluster = MarkerCluster(showCoverageOnHover=False).add_to(mapa)

for index, row in df_mapa.iterrows():
    inst = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'N/I'
    pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'
    
    html = f"<div style='width:200px; font-family:sans-serif;'><b style='color:#196F3D;'>📍 {row['municipio_ibge']}</b><br><hr><small><b>Força:</b> {inst}<br><b>Pés:</b> {pes}</small><br><a href='{link}' target='_blank' style='color:#2980B9;'>Notícia</a></div>"
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(28, 28)),
        tooltip=folium.Tooltip(html)
    ).add_to(marker_cluster)

# --- 6. INTERFACE DE USUÁRIO (TÍTULO, LEGENDA E CRÉDITOS) ---
elementos_html = """
    <div style="
        position: fixed; 
        top: 20px; left: 50%; transform: translateX(-50%); 
        width: 80%; max-width: 900px;
        z-index:9999; text-align: center;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 15px; border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        border-top: 5px solid #2E7D32;
        font-family: 'Times New Roman', Times, serif;
    ">
        <h1 style="margin: 0; font-size: 24px; color: #1B5E20; text-transform: uppercase; letter-spacing: 2px;">
            GeoCannabis_BR
        </h1>
        <h2 style="margin: 5px 0 0 0; font-size: 16px; font-weight: normal; color: #555; font-style: italic;">
            Dinâmica Espacial de Cultivo e Apreensão de Cannabis no Brasil (NEVIDH - UFJF)
        </h2>
    </div>

    <div style="
        position: fixed; 
        bottom: 50px; left: 50px; width: 180px; 
        background-color: white; border:1px solid #ccc; z-index:9999; font-size:11px;
        padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
        font-family: sans-serif;
    ">
        <b style="color:#2E7D32;">LEGENDA</b><br>
        <i style="background:rgba(255, 165, 0, 0.2); width:12px; height:12px; display:inline-block; border:1px solid orange;"></i>&nbsp; Polígono da Maconha<br>
        <img src="https://img.icons8.com/color/48/marijuana-leaf.png" width="12" height="12">&nbsp; Local de Apreensão
    </div>

    <div style="
        position: fixed; 
        bottom: 20px; right: 20px; 
        background-color: rgba(255,255,255,0.8); border-radius: 5px; z-index:9999; font-size:10px;
        padding: 5px 10px; font-family: sans-serif; text-align: right;
    ">
        <b>Coordenação:</b> Prof. Dr. Paulo Fraga<br>
        <b>Análise/Geoprocessamento:</b> Alessandro (PMMG/UFJF)<br>
        <b>Fonte:</b> NEVIDH/UFJF - 2026
    </div>
"""
mapa.get_root().html.add_child(folium.Element(elementos_html))

# 7. Salvamento Final
mapa.save('GeoCannabis_BR_Final.html')
print("\n✅ PRODUTO CONCLUÍDO COM EXCELÊNCIA: 'GeoCannabis_BR_Final.html'")