import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("🛡️ EXECUTANDO PROTOCOLO DE LIMPEZA: FOCO NO BRASIL E ESTABILIDADE...")

# 1. Carga de Dados
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
    url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
    coords = pd.read_csv(url_coords)
    df['codigo_ibge'] = df['codigo_ibge'].astype(int)
    coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
    df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')
except Exception as e:
    print(f"❌ ERRO NA CARGA: {e}")
    exit()

# 2. Mapa Cercado (Fronteira Brasileira)
limites_br = [[-34.5, -74.5], [5.5, -34.0]]
mapa = folium.Map(
    location=[-14.2350, -51.9253], zoom_start=4, 
    tiles='cartodb positron', control_scale=True,
    min_zoom=4, max_bounds=True,
    min_lat=limites_br[0][0], max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], max_lon=limites_br[1][1]
)

# 3. Ícone Padrão (Folha de Cannabis)
icon_leaf = "https://img.icons8.com/color/48/marijuana-leaf.png"

# Clusterização Segura (Sem erros de renderização)
marker_cluster = MarkerCluster(
    icon_create_function="""
        function(cluster) {
            var count = cluster.getChildCount();
            return L.divIcon({
                html: '<div style="background-image: url(' + '""" + icon_leaf + """' + '); background-size: contain; width: 35px; height: 35px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; text-shadow: 1px 1px 2px black;">' + count + '</div>',
                className: 'custom-cluster', iconSize: L.point(35, 35)
            });
        }
    """,
    showCoverageOnHover=False
).add_to(mapa)

# 4. Injeção de Dados nos Marcadores
for _, row in df_mapa.iterrows():
    # Sanitização de textos para evitar quebra do HTML
    municipio = str(row['municipio_ibge'])
    estado = str(row['estado_ibge'])
    forca = str(row['Instituição que efetuou a apreensao']) if pd.notna(row['Instituição que efetuou a apreensao']) else 'N/I'
    pes = str(row['Quantidade de pés encontrados']) if pd.notna(row['Quantidade de pés encontrados']) else '0'
    pren = str(row['quantidade prensada (embalada)']) if pd.notna(row['quantidade prensada (embalada)']) else '0'
    armas = str(row['armas apreendidas']) if pd.notna(row['armas apreendidas']) else '0'
    link = str(row['Link de acesso']) if pd.notna(row['Link de acesso']) else '#'

    # Card com Scroll Interno (Anti-Explosão)
    html_card = f"""
    <div style="width: 220px; max-height: 180px; overflow-y: auto; font-family: Arial, sans-serif; font-size: 11px; padding: 5px; line-height: 1.4;">
        <b style="color: #1B5E20; font-size: 13px;">📍 {municipio} - {estado}</b><hr style="margin: 5px 0;">
        <b>Data:</b> {row['data']}<br>
        <b>Força:</b> {forca}<br>
        <b>Pés:</b> {pes}<br>
        <b>Prensada:</b> {pren}<br>
        <b>Armas:</b> {armas}<br>
        <hr style="margin: 5px 0;">
        <a href="{link}" target="_blank" style="color: #2980B9; font-weight: bold; text-decoration: none;">🔗 Ver Notícia Completa</a>
    </div>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_leaf, icon_size=(25, 25)),
        tooltip=folium.Tooltip(html_card),
        popup=folium.Popup(html_card, max_width=250)
    ).add_to(marker_cluster)

# 5. Camada do Polígono (Sertão)
folium.Polygon(
    locations=[[-8.1, -40.2], [-7.5, -39.0], [-8.0, -37.8], [-9.2, -38.0], [-9.8, -39.5], [-9.2, -40.8]],
    color="orange", weight=1, fill=True, fill_color="yellow", fill_opacity=0.1
).add_to(mapa)

# 6. Interface (Título Arial 12, Escala Direita, Norte Superior Direito)
layout_css = f"""
    <style>
        /* Escala no canto inferior direito */
        .leaflet-control-scale {{ left: auto !important; right: 20px !important; bottom: 20px !important; }}
    </style>

    <div style="position: fixed; top: 15px; left: 50%; transform: translateX(-50%); z-index: 9999; text-align: center;">
        <h1 style="font-family: Arial, sans-serif; font-size: 12px; font-weight: bold; color: black; margin: 0; background: rgba(255,255,255,0.7); padding: 5px 15px; border-radius: 5px;">
            GEOCANABIS BR
        </h1>
    </div>

    <div style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Compass_rose_simple.svg" width="50" style="opacity: 0.7;">
    </div>

    <div style="position: fixed; bottom: 50px; left: 20px; z-index: 9999; background: white; padding: 10px; border: 1px solid #ccc; font-family: sans-serif; font-size: 10px; border-radius: 4px;">
        <b style="font-size: 11px;">LEGENDA</b><hr style="margin: 3px 0;">
        <i style="background:rgba(255, 165, 0, 0.1); width:12px; height:12px; display:inline-block; border:1px solid orange;"></i> Polígono da Maconha<br>
        <img src="{icon_leaf}" width="12"> Local de Apreensão
    </div>

    <div style="position: fixed; bottom: 15px; left: 20px; z-index: 9999; font-family: Arial; font-size: 10px; color: #444; background: rgba(255,255,255,0.6); padding: 2px 5px; border-radius: 3px;">
        Produzido por: Alessandro Carneiro | Dados: Dr. Paulo Fraga
    </div>
"""
mapa.get_root().html.add_child(folium.Element(layout_css))

mapa.save('GEOCANABIS_BR_LIMPO.html')
print("✅ OPERAÇÃO CONCLUÍDA: GEOCANABIS_BR_LIMPO.html")