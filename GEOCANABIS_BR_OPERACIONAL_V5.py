import pandas as pd
import folium
from folium.plugins import MarkerCluster, FloatImage

print("🦅 RECALIBRANDO MIRA E EXECUTANDO PROTOCOLO DE INSÍGNIAS...")

# 1. Dados e Limpeza
try:
    df = pd.read_csv('geocannabis_DASHBOARD_FINAL.csv').dropna(subset=['codigo_ibge'])
except FileNotFoundError:
    print("❌ ERRO CRÍTICO: Base de dados ausente. Abortando missão.")
    exit()

url_coords = "https://raw.githubusercontent.com/kelvins/municipios-brasileiros/main/csv/municipios.csv"
coords = pd.read_csv(url_coords)
df['codigo_ibge'] = df['codigo_ibge'].astype(int)
coords['codigo_ibge'] = coords['codigo_ibge'].astype(int)
df_mapa = pd.merge(df, coords[['codigo_ibge', 'latitude', 'longitude']], on='codigo_ibge', how='inner')

# 2. Configuração do Mapa (Escala ativada no construtor)
mapa = folium.Map(
    location=[-14.2350, -51.9253], zoom_start=4, 
    tiles='cartodb positron', 
    control_scale=True, # Ativa a escala
    min_zoom=4, max_bounds=True
)

# 3. Seta Norte - Canto Superior Direito
url_norte = "https://www.svgrepo.com/show/447990/compass-north.svg"
FloatImage(url_norte, top=2, right=2).add_to(mapa)

# 4. Lógica de Ícones e Insígnias
icon_leaf = "https://img.icons8.com/color/48/marijuana-leaf.png"
icon_pistol = "https://img.icons8.com/ios-filled/50/000000/pistol.png"
icon_brick = "https://img.icons8.com/color/48/brick.png"
brasao_rep = "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/200px-Coat_of_arms_of_Brazil.svg.png"

def get_insignia(forca):
    f = str(forca).upper()
    if 'PF' in f or 'FEDERAL' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b1/Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg/200px-Bras%C3%A3o_da_Pol%C3%ADcia_Federal.svg.png"
    if 'PRF' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/8/8e/Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg/200px-Bras%C3%A3o_da_Pol%C3%ADcia_Rodovi%C3%A1ria_Federal.svg.png"
    if 'PM' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/6/62/Bras%C3%A3o_da_PMMG.png/200px-Bras%C3%A3o_da_PMMG.png"
    if 'PC' in f or 'CIVIL' in f: return "https://upload.wikimedia.org/wikipedia/commons/thumb/b/bf/Coat_of_arms_of_Brazil.svg/200px-Coat_of_arms_of_Brazil.svg.png" # Fallback para PC
    return brasao_rep

marker_cluster = MarkerCluster(showCoverageOnHover=False).add_to(mapa)

for _, row in df_mapa.iterrows():
    # Lógica de Ícones: Prioridade para Arma de Fogo
    tem_arma = pd.notna(row['armas apreendidas']) and str(row['armas apreendidas']).strip().upper() not in ['0', 'X', 'NÃO', '']
    icon_final = icon_pistol if tem_arma else icon_leaf
    
    insignia = get_insignia(row['Instituição que efetuou a apreensao'])
    
    html_card = f"""
    <div style="width: 200px; font-family: sans-serif; font-size: 11px; padding: 5px;">
        <div style="text-align:center; margin-bottom: 8px;"><img src="{insignia}" width="45"></div>
        <b style="color: #1B5E20; font-size: 13px;">📍 {row['municipio_ibge']}</b>
        <hr style="margin: 5px 0; border: 0.5px solid #ddd;">
        <img src="{icon_leaf}" width="14"> <b>Pés:</b> {row['Quantidade de pés encontrados']}<br>
        <img src="{icon_brick}" width="14"> <b>Prensada:</b> {row['quantidade prensada (embalada)']}<br>
        <img src="{icon_pistol}" width="14"> <b>Armas:</b> {row['armas apreendidas']}<br>
        <div style="margin-top: 8px; text-align: right;">
            <a href="{row['Link de acesso']}" target="_blank" style="color: #2980B9; text-decoration: none; font-weight: bold;">[FONTE]</a>
        </div>
    </div>
    """
    
    folium.Marker(
        location=[row['latitude'], row['longitude']],
        icon=folium.CustomIcon(icon_final, icon_size=(26, 26)),
        tooltip=folium.Tooltip(html_card)
    ).add_to(marker_cluster)

# 5. Interface Operacional (CSS para mover a escala e fixar Legend/Título)
# Note: Removi a menção ao NEVIDH e usei Arial Black como solicitado.
layout_final = f"""
    <style>
        .leaflet-control-scale {{ left: auto !important; right: 10px !important; bottom: 10px !important; }}
    </style>
    
    <div style="position: fixed; top: 30px; left: 50%; transform: translateX(-50%); z-index: 9999; text-align: center;">
        <h1 style="font-family: 'Arial Black', Gadget, sans-serif; font-size: 36px; color: #000; margin: 0; text-shadow: 2px 2px #fff;">GEOCANABIS BR</h1>
        <p style="font-family: Arial, sans-serif; font-size: 14px; margin: 0; font-weight: bold;">SISTEMA DE MONITORAMENTO E ERRADICAÇÃO</p>
    </div>

    <div style="position: fixed; bottom: 80px; left: 20px; z-index: 9999; background: white; padding: 12px; border: 3px solid black; font-family: sans-serif; font-size: 12px; box-shadow: 5px 5px 0px rgba(0,0,0,0.2);">
        <b style="font-size: 14px;">LEGENDA TÁTICA</b><br>
        <hr style="margin: 5px 0;">
        <img src="{icon_leaf}" width="16"> Cannabis (Cultivo)<br>
        <img src="{icon_pistol}" width="16"> Arma de Fogo (Apreensão)<br>
        <img src="{icon_brick}" width="16"> Maconha Prensada<br>
        <hr style="margin: 5px 0;">
        <img src="{brasao_rep}" width="16"> Unidade de Segurança
    </div>

    <div style="position: fixed; bottom: 20px; left: 20px; z-index: 9999; font-family: Arial, sans-serif; font-size: 10px; color: #333; background: rgba(255,255,255,0.7); padding: 5px; border-radius: 3px;">
        <b>Geoprocessamento:</b> Alessandro (PMMG/UFJF)<br>
        <b>Coordenação:</b> Prof. Dr. Paulo Fraga | 2026
    </div>
"""
mapa.get_root().html.add_child(folium.Element(layout_final))

# 6. Salvamento
mapa.save('GEOCANABIS_BR_OPERACIONAL.html')
print("\n✅ MAPA REFORMULADO E OPERACIONAL: 'GEOCANABIS_BR_OPERACIONAL.html'")