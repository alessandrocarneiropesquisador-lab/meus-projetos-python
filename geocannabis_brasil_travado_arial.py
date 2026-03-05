import pandas as pd
import folium
from folium.plugins import MarkerCluster

print("📏 EXECUTANDO PROTOCOLO DE TRAVAMENTO GEOGRÁFICO DEFINITIVO...")

# 1. CARGA E CRUZAMENTO DE DADOS
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
    url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
    coords = pd.read_csv(url_coords)
    df['codigo_ibge'] = df['codigo_ibge'].astype(int)
    coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
    df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')
except Exception as e:
    print(f"Erro na carga: {e}")
    exit()

# 2. CONFIGURAÇÃO DO MAPA - CERCAMENTO REFORÇADO (ABNT)
# Coordenadas dos limites do Brasil com margem de segurança
limites_br = [[-34.0, -74.0], [6.0, -34.5]]

mapa = folium.Map(
    location=[-14.2350, -51.9253], 
    zoom_start=4, 
    tiles='cartodb positron', 
    control_scale=True, 
    min_zoom=4,               # Impede ver o globo inteiro
    max_bounds=True,          # Ativa o travamento nas bordas
    min_lat=limites_br[0][0], 
    max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], 
    max_lon=limites_br[1][1]
)

# 3. POLÍGONO DO SERTÃO
folium.Polygon(
    locations=[[-8.1, -40.2], [-7.5, -39.0], [-8.0, -37.8], [-9.2, -38.0], [-9.8, -39.5], [-9.2, -40.8]],
    color="orange", weight=1, fill=True, fill_color="yellow", fill_opacity=0.1,
    tooltip="Polígono da Maconha"
).add_to(mapa)

# 4. ICONOGRAFIA (FOLHA)
icon_leaf = "https://img.icons8.com/color/48/marijuana-leaf.png"
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

# 5. MARCADORES (HOVER E CLICK)
for _, row in df_mapa.iterrows():
    html_card = f"""
    <div style="width: 210px; max-height: 180px; overflow-y: auto; font-family: Arial, sans-serif; font-size: 11px; padding: 10px; line-height: 1.5;">
        <b style="color: #1B5E20; font-size: 13px;">📍 {row['municipio_ibge']} - {row['estado_ibge']}</b><br>
        <hr style="margin: 5px 0; border: 0.1px solid #ddd;">
        <b>Data:</b> {row['data']}<br>
        <b>Força:</b> {row['Instituição que efetuou a apreensao']}<br>
        <b>Pés:</b> {row['Quantidade de pés encontrados']}<br>
        <b>Prensada:</b> {row['quantidade prensada (embalada)']}<br>
        <b>Armas:</b> {row['armas apreendidas']}<br>
        <hr style="margin: 5px 0;">
        <a href="{row['Link de acesso']}" target="_blank" style="color: #2980B9; font-weight: bold; text-decoration: none;">🔗 Ver Notícia Completa</a>
    </div>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_leaf, icon_size=(25, 25)),
        tooltip=folium.Tooltip(html_card),
        popup=folium.Popup(html_card, max_width=250)
    ).add_to(marker_cluster)

# 6. INTERFACE: ESCALA À ESQUERDA | LEGENDA E CRÉDITOS À DIREITA
layout_css = f"""
    <style>
        /* ESCALA À ESQUERDA - Ajustada para dentro da margem */
        .leaflet-control-scale {{ 
            left: 50px !important; 
            bottom: 20px !important; 
            font-family: Arial, sans-serif !important; 
        }}
    </style>

    <div style="position: fixed; top: 15px; left: 50%; transform: translateX(-50%); z-index: 9999; text-align: center;">
        <h1 style="font-family: Arial, sans-serif; font-size: 14px; font-weight: bold; background: white; padding: 5px 20px; border: 1px solid #ccc; border-radius: 4px;">
            GEOCANABIS BR
        </h1>
    </div>

    <div style="position: fixed; top: 20px; right: 20px; z-index: 9999;">
        <img src="https://upload.wikimedia.org/wikipedia/commons/9/99/Compass_rose_simple.svg" width="50" style="opacity: 0.8;">
    </div>

    <div style="position: fixed; bottom: 20px; right: 20px; z-index: 9999; text-align: right;">
        <div style="background: white; padding: 10px; border: 1px solid black; font-family: Arial, sans-serif; font-size: 10px; display: inline-block; text-align: left; margin-bottom: 5px;">
            <b style="font-size: 11px;">LEGENDA</b><hr style="margin: 3px 0;">
            <i style="background:rgba(255, 165, 0, 0.1); width:12px; height:12px; display:inline-block; border:1px solid orange;"></i> Polígono da Maconha<br>
            <img src="{icon_leaf}" width="12"> Local de Apreensão
        </div>
        <div style="font-family: Arial, sans-serif; font-size: 11px; line-height: 0.8; color: black; background: rgba(255,255,255,0.7); padding: 5px; border-radius: 3px;">
            Produzido por: Alessandro Carneiro<br>
            Dados: Dr. Paulo Fraga
        </div>
    </div>
"""
mapa.get_root().html.add_child(folium.Element(layout_html))

mapa.save('GEOCANABIS_BR_CIENTIFICO_TRAVADO.html')
print("✅ OPERAÇÃO CONCLUÍDA. MAPA TRAVADO E NORMATIZADO.")