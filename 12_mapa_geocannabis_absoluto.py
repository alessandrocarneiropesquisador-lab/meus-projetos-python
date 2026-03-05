import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("⚔️ RESTAURANDO EXCELÊNCIA VISUAL E DADOS PROFUNDOS...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv')
    df = df.dropna(subset=['codigo_ibge']).copy()
except FileNotFoundError:
    print("❌ ERRO: Base de dados não encontrada.")
    exit()

# 2. Resgate de Coordenadas
url_coordenadas = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coordenadas = pd.read_csv(url_coordenadas)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coordenadas['codigo_ibge'] = coordenadas['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coordenadas[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 3. Criação do Mapa Delimitado ao Brasil
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

# --- CAMADA: POLÍGONO DA MACONHA (O DESTAQUE ANALÍTICO) ---
coords_poligono = [
    [-8.1, -40.2], [-7.5, -39.0], [-8.0, -37.8], 
    [-9.2, -38.0], [-9.8, -39.5], [-9.2, -40.8]
]
folium.Polygon(
    locations=coords_poligono,
    color="orange", weight=2,
    fill=True, fill_color="yellow", fill_opacity=0.15,
    tooltip="Polígono da Maconha: Área de Concentração Histórica"
).add_to(mapa)

# Texto flutuante
folium.map.Marker(
    [-8.1, -39.5],
    icon=folium.DivIcon(
        icon_size=(150,36),
        html='<div style="font-size: 10pt; color: #E67E22; font-weight: bold; opacity: 0.8; letter-spacing: 1px;">POLÍGONO DA MACONHA</div>',
    )
).add_to(mapa)

# 4. Customização de Ícones (Folha Verde) e Clusters
icon_url = "https://img.icons8.com/color/48/marijuana-leaf.png"

# Função para que o agrupamento (cluster) também use a folha
icon_create_function = """
    function(cluster) {
        var childCount = cluster.getChildCount(); 
        return L.divIcon({ 
            html: '<div style="background-image: url(' + '""" + icon_url + """' + '); background-size: cover; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; font-weight: bold; color: white; text-shadow: 1px 1px 2px black;">' + childCount + '</div>', 
            className: 'marker-cluster-custom', 
            iconSize: L.point(40, 40) 
        });
    }
"""
marker_cluster = MarkerCluster(icon_create_function=icon_create_function).add_to(mapa)

# 5. Injeção de Dados com Fichas Técnicas Completas
for index, row in df_mapa.iterrows():
    # Sanitização
    inst = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'N/I'
    pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    pren = str(row['quantidade prensada (embalada)']) if pd.notna(row['quantidade prensada (embalada)']) else '0'
    armas = str(row['armas apreendidas']) if pd.notna(row['armas apreendidas']) else '0'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'

    # HTML com Design NEVIDH ( largura fixa e scroll para não estourar)
    html_ficha = f"""
    <div style="width: 250px; max-height: 220px; overflow-y: auto; font-family: sans-serif; padding: 10px; border-top: 4px solid #27AE60;">
        <b style="color: #196F3D; font-size: 14px;">📍 {row['municipio_ibge']} - {row['estado_ibge']}</b><br>
        <hr style="margin: 5px 0; border: 0.2px solid #eee;">
        <p style="margin: 3px 0; font-size: 12px;"><b>🚔 Força:</b> {inst}</p>
        <p style="margin: 3px 0; font-size: 12px;"><b>🌿 Pés:</b> <span style="color: #27AE60; font-weight: bold;">{pes}</span></p>
        <p style="margin: 3px 0; font-size: 12px;"><b>📦 Prensada:</b> {pren}</p>
        <p style="margin: 3px 0; font-size: 12px;"><b>🔫 Armas:</b> <span style="color: #C0392B;">{armas}</span></p>
        <hr style="margin: 5px 0; border: 0.2px solid #eee;">
        <a href="{link}" target="_blank" style="color: #2980B9; font-weight: bold; text-decoration: none; font-size: 11px;">🔗 ABRIR REPORTAGEM</a>
    </div>
    """

    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(32, 32)),
        tooltip=folium.Tooltip(html_ficha, sticky=False),
        popup=folium.Popup(html_ficha, max_width=300)
    ).add_to(marker_cluster)

# 6. Salvamento Final
mapa.save('mapa_geocannabis_NEVIDH_FINAL.html')
print("\n✅ PRODUTO DE EXCELÊNCIA GERADO: 'mapa_geocannabis_NEVIDH_FINAL.html'")