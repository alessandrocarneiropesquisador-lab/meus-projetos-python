import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("🛡️ ELIMINANDO RUÍDOS VISUAIS E FINALIZANDO PRODUTO...")

# 1. Carga e Purga
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
    df = df.dropna(subset=['codigo_ibge']).copy()
except FileNotFoundError:
    print("❌ ERRO: Base não encontrada.")
    exit()

# 2. Geoprocessamento
url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coords = pd.read_csv(url_coords)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 3. Base Cartográfica com Cercamento
limites_br = [[-34.5, -74.5], [5.5, -34.0]]
mapa = folium.Map(
    location=[-14.2350, -51.9253], 
    zoom_start=4, 
    tiles='cartodb positron',
    min_zoom=4,
    max_bounds=True,
    min_lat=limites_br[0][0], max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], max_lon=limites_br[1][1]
)

# --- CAMADA: POLÍGONO ANALÍTICO (SERTÃO) ---
coords_poligono = [[-8.1, -40.2], [-7.5, -39.0], [-8.0, -37.8], [-9.2, -38.0], [-9.8, -39.5], [-9.2, -40.8]]
folium.Polygon(
    locations=coords_poligono,
    color="orange", weight=1,
    fill=True, fill_color="yellow", fill_opacity=0.1,
    tooltip="Polígono da Maconha"
).add_to(mapa)

# 4. Configuração do Cluster (SEM O POLÍGONO AZUL)
icon_url = "https://img.icons8.com/color/48/marijuana-leaf.png"

icon_create_func = """
    function(cluster) {
        var childCount = cluster.getChildCount(); 
        return L.divIcon({ 
            html: '<div style="background-image: url(' + '""" + icon_url + """' + '); background-size: cover; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;">' + childCount + '</div>', 
            className: 'marker-cluster-custom', 
            iconSize: L.point(40, 40) 
        });
    }
"""

# AQUI ESTÁ O AJUSTE: showCoverageOnHover=False elimina o polígono azul ao passar o mouse
marker_cluster = MarkerCluster(
    icon_create_function=icon_create_func,
    showCoverageOnHover=False, 
    zoomToBoundsOnClick=True
).add_to(mapa)

# 5. Marcadores com Ficha Técnica
for index, row in df_mapa.iterrows():
    inst = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'N/I'
    pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    pren = str(row['quantidade prensada (embalada)']) if pd.notna(row['quantidade prensada (embalada)']) else '0'
    armas = str(row['armas apreendidas']) if pd.notna(row['armas apreendidas']) else '0'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'

    html_layout = f"""
    <div style="width: 250px; max-height: 180px; overflow-y: auto; font-family: sans-serif; padding: 10px; border-left: 4px solid #27AE60; background-color: #fcfcfc;">
        <b style="color: #196F3D; font-size: 14px;">📍 {row['municipio_ibge']} - {row['estado_ibge']}</b><br>
        <hr style="margin: 5px 0; opacity: 0.1;">
        <p style="margin: 2px 0; font-size: 12px;"><b>Força:</b> {inst}</p>
        <p style="margin: 2px 0; font-size: 12px;"><b>Pés:</b> <span style="color: #27AE60; font-weight: bold;">{pes}</span></p>
        <p style="margin: 2px 0; font-size: 12px;"><b>Prensada:</b> {pren}</p>
        <p style="margin: 2px 0; font-size: 12px;"><b>Armas:</b> <span style="color: #C0392B;">{armas}</span></p>
        <hr style="margin: 5px 0; opacity: 0.1;">
        <a href="{link}" target="_blank" style="color: #2980B9; font-weight: bold; text-decoration: none; font-size: 11px;">🔗 VER REPORTAGEM</a>
    </div>
    """

    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(32, 32)),
        tooltip=folium.Tooltip(html_layout),
        popup=folium.Popup(html_layout, max_width=300)
    ).add_to(marker_cluster)

# 6. Salvamento
mapa.save('mapa_geocannabis_nevidh.html')
print("\n✅ MAPA LIMPO E OPERACIONAL: 'mapa_geocannabis_nevidh.html'")