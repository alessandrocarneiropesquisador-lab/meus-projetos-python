import pandas as pd
import folium
from folium.plugins import MarkerCluster, FloatImage

print("🧪 REFINANDO ESTÉTICA E LIMPANDO CAMPO DE VISÃO...")

# 1. Dados
df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coords = pd.read_csv(url_coords)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 2. Mapa Base (Foco no Brasil)
limites_br = [[-34.5, -74.5], [5.5, -34.0]]
mapa = folium.Map(
    location=[-14.2350, -51.9253], zoom_start=4, 
    tiles='cartodb positron', control_scale=True,
    min_zoom=4, max_bounds=True,
    min_lat=limites_br[0][0], max_lat=limites_br[1][0],
    min_lon=limites_br[0][1], max_lon=limites_br[1][1]
)

# 3. Polígono e Bússola (URL Nova e Segura)
folium.Polygon(
    locations=[[-8.1, -40.2], [-7.5, -39.0], [-8.0, -37.8], [-9.2, -38.0], [-9.8, -39.5], [-9.2, -40.8]],
    color="orange", weight=1, fill=True, fill_color="yellow", fill_opacity=0.1
).add_to(mapa)

url_norte = "https://www.svgrepo.com/show/447990/compass-north.svg"
FloatImage(url_norte, bottom=3, left=1).add_to(mapa)

# 4. Ícones e Cluster Customizados
icon_url = "https://img.icons8.com/color/48/marijuana-leaf.png"
icon_cluster = """
    function(cluster) {
        var count = cluster.getChildCount();
        return L.divIcon({
            html: '<div style="background-image: url(' + '""" + icon_url + """' + '); background-size: contain; background-repeat: no-repeat; width: 40px; height: 40px; display: flex; align-items: center; justify-content: center; color: white; font-weight: bold; text-shadow: 2px 2px 3px black;">' + count + '</div>',
            className: 'custom-cluster',
            iconSize: L.point(40, 40)
        });
    }
"""
marker_cluster = MarkerCluster(icon_create_function=icon_cluster, showCoverageOnHover=False).add_to(mapa)

# 5. Injeção de Marcadores
for _, row in df_mapa.iterrows():
    html = f"""
    <div style="width: 220px; font-family: sans-serif; font-size: 12px;">
        <b style="color: #1B5E20;">📍 {row['municipio_ibge']}</b><br>
        <hr style="margin: 5px 0; border: 0.1px solid #eee;">
        <b>Força:</b> {row['Instituição que efetuou a apreensao']}<br>
        <b>Pés:</b> {row['Quantidade de pés encontrados']}<br>
        <b>Armas:</b> {row['armas apreendidas']}<br>
        <a href="{row['Link de acesso']}" target="_blank" style="color: #2980B9;">Notícia Original</a>
    </div>
    """
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_url, icon_size=(28, 28)),
        tooltip=folium.Tooltip(html)
    ).add_to(marker_cluster)

# 6. CSS e HTML Customizado (Limpeza de Interface)
estilo_nevidh = """
    <div style="position: fixed; top: 10px; left: 50%; transform: translateX(-50%); z-index: 9999; background: rgba(255,255,255,0.9); padding: 5px 20px; border-radius: 30px; border: 1px solid #2E7D32; font-family: 'Segoe UI', Tahoma, sans-serif; text-align: center; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">
        <span style="font-size: 18px; font-weight: bold; color: #1B5E20;">GEOCANNABIS_BR</span>
        <span style="font-size: 12px; color: #666; margin-left: 10px; font-style: italic;">NEVIDH - UFJF</span>
    </div>

    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; background: white; padding: 10px; border: 1px solid #ccc; font-size: 11px; font-family: sans-serif; border-radius: 5px;">
        <b style="color:#2E7D32;">LEGENDA</b><br>
        <i style="background:rgba(255, 165, 0, 0.2); width:12px; height:12px; display:inline-block; border:1px solid orange;"></i> Polígono da Maconha<br>
        <img src="https://img.icons8.com/color/48/marijuana-leaf.png" width="12"> Local de Apreensão
    </div>

    <div style="position: fixed; bottom: 10px; right: 10px; z-index: 9999; text-align: right; font-size: 9px; font-family: sans-serif; color: #777; background: rgba(255,255,255,0.7); padding: 2px 5px; border-radius: 3px;">
        Coordenação: Prof. Dr. Paulo Fraga | Geoprocessamento: Alessandro (UFJF)
    </div>
"""
mapa.get_root().html.add_child(folium.Element(estilo_nevidh))

mapa.save('mapa_geocannabis_nevidh_CLEAN.html')
print("\n✅ MAPA CIRÚRGICO GERADO: 'mapa_geocannabis_nevidh_CLEAN.html'")