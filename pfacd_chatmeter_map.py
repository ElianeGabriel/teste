import numpy as np
import pandas as pd
import pfacd_functions
import streamlit as st
from st_pages import add_page_title
import folium
import folium.features
from folium import plugins
from jinja2 import Template
from branca.colormap import linear
import geopandas as gpd

from streamlit_folium import folium_static

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# =========================================================================================================

st.set_page_config(layout="wide")
add_page_title(layout="wide")
st.logo(image='static/640px-HD_transparent_picture.png', icon_image='static/ChatMeter_Logo_Bullet.png')
with open('style.css') as f:
    st.markdown(f'''<style>{f.read()}
                    /* Alterar a cor do slider | Fonte: https://discuss.streamlit.io/t/how-to-change-st-sidebar-slider-default-color/3900/2 */
                    div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{{
                        background-color: #175446;
                    }}

                    div.stSlider > div[data-baseweb="slider"] > div > div > div > div{{
                        color: #175446; 
                    }}

                    div.stSlider > div[data-baseweb = "slider"] > div > div {{
                        background: #175446;}}

                    div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {{
                        background: rgb(1 1 1 / 0%); }}

                    .stTabs [data-baseweb="tab"] {{
                        color: #175446;
                    }}

                    .stTabs [data-baseweb="tab-highlight"] {{
                        background-color: #175446;
                    }}
            </style>''', unsafe_allow_html=True)

st.markdown("""
De forma a enriquecer a análise geográfica dos clientes portugueses :flag-pt:, foi desenvolvido um mapa interativo que representa as regiões de Portugal, onde se pode ver a distribuição dos utilizadores por distrito, 
concelho e freguesia, contendo informações relevantes para auxiliar na tomada de decisão no negócio. :briefcase:
""")

st.divider()

# =========================================================================================================
# Import da Base de Dados dos Posts/Comments/Users
Facebook_PCU_Analysis, Facebook_Posts_Analysis = pfacd_functions.load_data()
del Facebook_Posts_Analysis
Facebook_PCU_Analysis.sort_values(by='post_date', inplace=True)


# =========================================================================================================

# Import das coordenadas de Portugal no Geopandas
# Fonte: https://public.opendatasoft.com/explore/dataset/georef-portugal-freguesia
@st.cache_resource
def load_map_dataframe():
    map_dataframe = gpd.read_file('Datasets_Vodafone/Auxiliares/georef-portugal-freguesia-simplified.geojson')
    return map_dataframe


# =========================================================================================================

# Classe para ver o Google Street View | Fonte: https://astro-geo-gis.com/open-street-view-with-python-folium-map/
class ClickForOneMarker(folium.ClickForMarker):
    """
    Description of the tool
    """
    _template = Template(u"""
        {% macro script(this, kwargs) %}
        const fontAwesomeIcon= L.divIcon({
            html: '<i class="fa-solid fa-3x fa-street-view" style="color:#F69423"></i>',
            iconSize: [0,0],
            iconAnchor: [15,0]
            });
        var new_mark = L.marker();
        function newMarker(e){
        new_mark.setLatLng(e.latlng).addTo({{this._parent.get_name()}});
        new_mark.setIcon(fontAwesomeIcon);
        new_mark.dragging.enable();
        new_mark.on('dblclick', function(e){ {{this._parent.get_name()}}.removeLayer(e.target)})
        var lat = e.latlng.lat.toFixed(4),
            lng = e.latlng.lng.toFixed(4);
        new_mark.bindPopup("<b>Latitude : </b>" + lat + "<br><b>Longitude : </b> " + lng +"<br> <a href=https://www.google.com/maps?layer=c&cbll=" + lat + "," + lng + " target=blank> <img src='https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Google_Street_View_icon.svg/768px-Google_Street_View_icon.svg.png' style='width:40px;margin:0 auto;display: block;margin-left: auto; margin-right: auto; margin-top:5px'></img></a>").openPopup();
        };
        {{this._parent.get_name()}}.on('click', newMarker);
        {% endmacro %}
    """)  # noqa

    def __init__(self, popup=None):
        super(ClickForOneMarker, self).__init__(popup)
        self._name = 'ClickForOneMarker'


# Google Earth Engine Python API and Folium Interactive Mapping
# Fonte: colab.research.google.com/github/giswqs/qgis-earthengine-examples/blob/master/Folium/ee-api-folium-setup.ipynb
basemaps = {'Google Maps': folium.TileLayer(
    tiles='https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Maps',
    overlay=False,
    control=True,
    show=False
),
    'Google Satellite': folium.TileLayer(
        tiles='https://mt1.google.com/vt/lyrs=s&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True,
        show=False
    )}


# ================================================ Mapa ================================================================
def mapa_folium_dfs(Facebook_PCU_Analysis=Facebook_PCU_Analysis, map_dataframe=load_map_dataframe()):
    # ================================================= FREGUESIAS ====================================================
    # Agrupar os dados por freguesia, concelho e distrito e contar o número de utilizadores em cada grupo
    users_freguesia_concelho_distrito = Facebook_PCU_Analysis.groupby(
        ['user_freguesia', 'user_concelho', 'user_distrito']).size().reset_index(name='Freguesia')

    # Renomear as colunas para corresponderem às colunas do map_dataframe
    users_freguesia_concelho_distrito = users_freguesia_concelho_distrito.rename(
        columns={'user_freguesia': 'fre_name', 'user_concelho': 'con_name', 'user_distrito': 'dis_name'})

    # Fazer o merge com base nas três colunas (freguesia, concelho e distrito)
    merged_dataframe_F = map_dataframe.merge(users_freguesia_concelho_distrito,
                                             on=['fre_name', 'con_name', 'dis_name'],
                                             how='outer')

    # Preencher os valores NaN com 0
    merged_dataframe_F['Freguesia'].fillna(0, inplace=True)
    merged_dataframe_F.dropna(inplace=True)
    merged_dataframe_F["Users_%"] = round(
        (merged_dataframe_F["Freguesia"] / merged_dataframe_F["Freguesia"].sum()) * 100, 2)

    # ================================================= CONCELHOS ======================================================
    # Agrupar os usuários por concelho e distrito
    users_concelho_distrito = Facebook_PCU_Analysis.groupby(['user_concelho', 'user_distrito']).size().reset_index(
        name='Concelho')

    # Fazer o merge com o dataframe map_dataframe usando as colunas 'con_name' e 'dis_name'
    merged_dataframe_C = map_dataframe.merge(users_concelho_distrito, left_on=['con_name', 'dis_name'],
                                             right_on=['user_concelho', 'user_distrito'], how='outer')

    # Preencher os valores NaN com 0
    merged_dataframe_C['Concelho'].fillna(0, inplace=True)
    merged_dataframe_C.dropna(inplace=True, subset=['con_name'])

    merged_dataframe_C["Users_%"] = round((merged_dataframe_C["Concelho"] /
                                           merged_dataframe_C.groupby('user_concelho').agg({'Concelho': 'first'})[
                                               'Concelho'].sum()) * 100, 2)

    # Preencher os valores NaN nas colunas 'user_concelho' e 'user_distrito' com os valores correspondentes nas colunas
    # 'con_name' e 'dis_name', respetivamente
    merged_dataframe_C['user_concelho'] = merged_dataframe_C['user_concelho'].fillna(merged_dataframe_C['con_name'])
    merged_dataframe_C['user_distrito'] = merged_dataframe_C['user_distrito'].fillna(merged_dataframe_C['dis_name'])

    # ------------------------------------------------------------------------------------------------------------------
    # ================================================= DISTRITOS ======================================================
    # Agrupar os users por distritos
    users_distrito = Facebook_PCU_Analysis.groupby('user_distrito').size().reset_index(name='Distrito')
    merged_dataframe_D = map_dataframe.merge(users_distrito, left_on="dis_name", right_on="user_distrito", how='outer')

    # Preencher os valores NaN com 0
    merged_dataframe_D['Distrito'].fillna(0, inplace=True)
    merged_dataframe_D.dropna(inplace=True, subset=['dis_name'])

    merged_dataframe_D["Users_%"] = round((merged_dataframe_D["Distrito"] /
                                           merged_dataframe_D.groupby('user_distrito').agg({'Distrito': 'first'})[
                                               'Distrito'].sum()) * 100, 2)

    return merged_dataframe_F, merged_dataframe_C, merged_dataframe_D


# ----------------------------------------------------------------------------------------------------------------------
# Mapa no Streamlit
def mapa_folium(merged_dataframe_F, merged_dataframe_C, merged_dataframe_D):
    # Criar um mapa com folium
    mapa = folium.Map(location=[40 - 0.2, -8], zoom_start=6, control_scale=True)
    basemaps['Google Maps'].add_to(mapa)
    basemaps['Google Satellite'].add_to(mapa)
    plugins.Fullscreen(position='topleft').add_to(mapa)  # Opção de Fullscreen
    mapa.add_child(plugins.MiniMap(toggle_display=True))  # Minimapa do lado direito
    # plugins.Draw().add_to(mapa)                         # Opções de Desenhar
    plugins.FloatImage(
        image='https://upload.wikimedia.org/wikipedia/en/archive/c/cc/20180621135549%21Vodafone_2017_logo.svg',
        bottom=8, left=2, width='40px').add_to(mapa)  # Logo Vodafone
    # mapa.add_child(ClickForOneMarker())

    # -----------------------------------------------------------------------------------------------------------------
    # ================================================= FREGUESIAS ====================================================

    # Adicionar as freguesias ao mapa como polígonos
    colormap1 = linear.OrRd_09.scale(merged_dataframe_F.Freguesia.min(), merged_dataframe_F.Freguesia.max())
    colormap1.caption = "Users por Freguesias"
    colormap1.width = 300

    popup = folium.GeoJsonPopup(
        fields=["fre_name", "con_name", "dis_name", "Freguesia", "Users_%"],
        # aliases=["Freguesia", "Concelho", "Distrito", "Nº de Users (n)", "% de Users (%)", "Sentimento Predominante", "Tópico 1", "Tópico 2"],
        aliases=["Freguesia", "Concelho", "Distrito", "Nº de Users (n)", "% de Users (%)"],
        localize=True,
        labels=True,
        style="color:black; font-family: arial; font-size: 12px;",
    )

    folium.GeoJson(
        merged_dataframe_F,
        name='Por Freguesias',
        style_function=lambda feature: {
            'fillColor': colormap1(int(feature['properties']['Freguesia'])),
            'color': 'black',
            'weight': 0.8,
            "dashArray": "5, 5",
            'fillOpacity': 0.9
        },
        popup=popup
    ).add_to(mapa)

    # Adicione o colormap à layer 'Por Freguesias'
    # colormap.add_to(mapa, name="Por Freguesias")
    mapa.add_child(colormap1, name="Por Freguesias")

    # ------------------------------------------------------------------------------------------------------------------
    # ================================================= CONCELHOS ======================================================
    colormap2 = linear.Purples_09.scale(merged_dataframe_C.Concelho.min(), merged_dataframe_C.Concelho.max())
    colormap2.caption = "Users por Concelho"
    colormap2.width = 300

    merged_dataframe_C["Users_%"] = round((merged_dataframe_C["Concelho"] /
                                           merged_dataframe_C.groupby('user_concelho').agg({'Concelho': 'first'})[
                                               'Concelho'].sum()) * 100, 2)

    # Preencher os valores NaN nas colunas 'user_concelho' e 'user_distrito' com os valores correspondentes nas colunas
    # 'con_name' e 'dis_name', respetivamente
    merged_dataframe_C['user_concelho'] = merged_dataframe_C['user_concelho'].fillna(merged_dataframe_C['con_name'])
    merged_dataframe_C['user_distrito'] = merged_dataframe_C['user_distrito'].fillna(merged_dataframe_C['dis_name'])

    popup = folium.GeoJsonPopup(
        fields=["user_concelho", "user_distrito", "Concelho", "Users_%"],
        aliases=["Concelho", "Distrito", "Nº de Users (n)", "% de Users (%)"],
        localize=True,
        labels=True,
        style="color:black; font-family: arial; font-size: 12px;",
    )

    folium.GeoJson(
        merged_dataframe_C.dissolve(by=['dis_name', 'con_name']),
        name='Por Concelho',
        style_function=lambda feature: {
            'fillColor': colormap2(feature['properties']['Concelho']),
            'color': 'black',
            'weight': 0.8,
            "dashArray": "5, 5",
            'fillOpacity': 0.9
        },
        popup=popup
    ).add_to(mapa)

    mapa.add_child(colormap2, name="Por Concelho")

    # ------------------------------------------------------------------------------------------------------------------
    # ================================================= DISTRITOS ======================================================
    colormap3 = linear.Blues_09.scale(merged_dataframe_D.Distrito.min(), merged_dataframe_D.Distrito.max())
    colormap3.caption = "Users por Distrito"
    colormap3.width = 300

    merged_dataframe_D["Users_%"] = round((merged_dataframe_D["Distrito"] /
                                           merged_dataframe_D.groupby('user_distrito').agg({'Distrito': 'first'})[
                                               'Distrito'].sum()) * 100, 2)
    popup = folium.GeoJsonPopup(
        fields=["dis_name", "Distrito", "Users_%"],
        aliases=["Distrito", "Nº de Users (n)", "% de Users (%)"],
        localize=True,
        labels=True,
        style="color:black; font-family: arial; font-size: 12px;",
    )

    folium.GeoJson(
        merged_dataframe_D.dissolve(by='user_distrito'),
        name='Por Distrito',
        style_function=lambda feature: {
            'fillColor': colormap3(feature['properties']['Distrito']),
            'color': 'black',
            'weight': 0.8,
            "dashArray": "5, 5",
            'fillOpacity': 0.9
        },
        popup=popup
    ).add_to(mapa)

    mapa.add_child(colormap3, name="Por Distrito")

    # ------------------------------------------------------------------------------------------------------------------
    # Mostrar o mapa
    mapa.add_child(folium.LayerControl(collapsed=False))  # Camadas de Diferentes Mapas

    return mapa


# =========================================================================================================
# Filtros

# Definições do botão 'Filtrar' - https://docs.streamlit.io/develop/concepts/design/buttons
if 'clicked' not in st.session_state:
    st.session_state.clicked = False


def click_button():
    st.session_state.clicked = True


if 'filtros_button' in st.session_state and st.session_state.filtros_button is True:
    st.session_state.running = True
else:
    st.session_state.running = False


# Aplicar os filtros
@st.cache_data
def apply_filters(filters=None):
    if filters is None:
        return Facebook_PCU_Analysis

    filtered_df = Facebook_PCU_Analysis.copy()

    # # Converter datas para datetime64[ns] - Execeção
    # filters['start_date'] = pd.to_datetime(filters['start_date'])
    # filters['end_date'] = pd.to_datetime(filters['end_date'])

    if filters['page'] and len(filters['page']) > 0:
        filtered_df = filtered_df[filtered_df['page'].isin(filters['page'])]

    if filters['start_date'] and filters['end_date']:
        filtered_df = filtered_df[(filtered_df['post_date'].dt.date >= filters['start_date']) & (
                filtered_df['post_date'].dt.date <= filters['end_date'])]

    if filters['sentiment-post'] and len(filters['sentiment-post']) > 0:
        filtered_df = filtered_df[filtered_df['post_sentiment_label'].isin(filters['sentiment-post'])]

    if filters['sentiment-comment'] and len(filters['sentiment-comment']) > 0:
        filtered_df = filtered_df[filtered_df['comment_sentiment_label'].isin(filters['sentiment-comment'])]

    if filters['topic-post'] and len(filters['topic-post']) > 0:
        filtered_df = filtered_df[filtered_df['mDeBERTa_post_topic_label_1'].isin(filters['topic-post'])]

    if filters['topic-comment'] and len(filters['topic-comment']) > 0:
        filtered_df = filtered_df[filtered_df['mDeBERTa_comment_topic_label_1'].isin(filters['topic-comment'])]

    return filtered_df


# =========================================================================================================
step1 = "Original"
step2 = "Com Filtros"
steps = [step1, step2]

one, two = st.tabs(steps)

# =========================================================================================================
# OBRIGADOOOOOOOOOOO! SALVASTE ISTO https://discuss.streamlit.io/t/bug-with-st-folium/50218/5

# Filtros | Esquerda
with st.sidebar:
    st.markdown("## Filtros")

    # Filtro por Página
    page_filter = st.multiselect("Página(s)", Facebook_PCU_Analysis['page'].unique(), placeholder="Escolha a Página")

    # Filtro por Data | Intervalo de Datas
    start_date, end_date = pfacd_functions.init_sidebar_dates_pickers(Facebook_PCU_Analysis['post_date'])

    # Filtro por Sentimento
    lista_sentimentos = ['Positivo', 'Tendência Positiva', 'Neutro', 'Negativo', 'Tendência Negativa']
    sentiment_post_filter = st.multiselect("Sentimento dos Posts",
                                           Facebook_PCU_Analysis['post_sentiment_label'].dropna().unique(),
                                           placeholder="Escolha o Sentimento dos Posts")
    sentiment_comment_filter = st.multiselect("Sentimento dos Comentários",
                                              Facebook_PCU_Analysis['comment_sentiment_label'].dropna().unique(),
                                              placeholder="Escolha o Sentimento dos Comentários")

    # Filtro por Tópico
    topic_post_filter = st.multiselect("Tópico dos Posts",
                                       Facebook_PCU_Analysis['mDeBERTa_post_topic_label_1'].unique(),
                                       placeholder="Escolha o Tópico dos Posts")

    topic_comment_filter = st.multiselect("Tópico dos Comentários",
                                          Facebook_PCU_Analysis['mDeBERTa_comment_topic_label_1'].unique(),
                                          placeholder="Escolha o Tópico dos Comentários")

    if st.button("Filtrar", on_click=click_button, key='filtros_button'):
        Facebook_PCU_Analysis_filtered = apply_filters({
            'page': page_filter,
            'start_date': start_date,
            'end_date': end_date,
            'sentiment-post': sentiment_post_filter,
            'sentiment-comment': sentiment_comment_filter,
            'topic-post': topic_post_filter,
            'topic-comment': topic_comment_filter
        })

        st.session_state["two"] = True

        step2 = "Com Filtros"

# Definir a palette_Mapa
palette_Mapa = [
    [(23, 84, 70), '#175446'],  # Verde Água Escuro
    [(46, 168, 140), '#2ea88c'],  # Verde Água
    [(162, 229, 214), '#a2e5d6'],  # Verde Água Claro
]

try:
    # =========================================================================================================
    # 2nd Tab
    with two:
        if "two" in st.session_state:
            # Mapa
            st.write("## Mapa de Portugal Com Filtros Aplicados")

            # Cartões com Nº de Posts, Comentários e Utilizadores Únicos
            col1, col2, col3 = st.columns(3)

            try:
                # Cartões com a função create_card() com Nº de Posts, Comentários e Utilizadores Únicos
                # Cartão 1 | Total de Posts
                pfacd_functions.create_card(col1, "fas fa-newspaper", palette_Mapa[0][0], (255, 255, 255),
                                            "Total de Posts", Facebook_PCU_Analysis_filtered['post_id'].nunique())

                # Cartão 2 | Total de Comentários
                pfacd_functions.create_card(col2, "fas fa-comments", palette_Mapa[1][0], (255, 255, 255),
                                            "Total de Comentários", Facebook_PCU_Analysis_filtered['comment_id'].nunique())

                # Cartão 3 | Total de Utilizadores Únicos
                pfacd_functions.create_card(col3, "fas fa-users", palette_Mapa[2][0], (255, 255, 255),
                                            "Total de Utilizadores Únicos",
                                            Facebook_PCU_Analysis_filtered['user_link'].nunique())

                # Top 5 Freguesias, Concelhos e Distritos com mais Utilizadores
                st.markdown("""
                    <br><br> 
                    <h2 style="color:#175446; font-family:arial; font-size: 20px; font-weight: bold;">
                        Top 5 Freguesias, Concelhos e Distritos com + Utilizadores 
                    </h2>
                    """, unsafe_allow_html=True)
                col1_F, col2_F, col3_F = st.columns(3)

                # Assumir como NA as Freguesias, Concelhos e Distritos que contêm 'USI'
                Facebook_PCU_Analysis_filtered['user_freguesia'] = Facebook_PCU_Analysis_filtered['user_freguesia'].replace(
                    'USI', np.nan)
                Facebook_PCU_Analysis_filtered['user_concelho'] = Facebook_PCU_Analysis_filtered['user_concelho'].replace(
                    'USI', np.nan)
                Facebook_PCU_Analysis_filtered['user_distrito'] = Facebook_PCU_Analysis_filtered['user_distrito'].replace(
                    'USI', np.nan)

                # Top 5 Freguesias
                top_freguesias = Facebook_PCU_Analysis_filtered['user_freguesia'].value_counts().head(5)
                top_freguesias_pct = round(
                    (top_freguesias / Facebook_PCU_Analysis_filtered['user_freguesia'].value_counts().sum()) * 100, 2)
                top_freguesias_df = pd.concat([top_freguesias, top_freguesias_pct], axis=1)
                top_freguesias_df.columns = ['Nº de Utilizadores', '% de Utilizadores']
                top_freguesias_df.index.name = 'Freguesia'
                with col1_F:
                    st.dataframe(top_freguesias_df, use_container_width=True)

                # Top 5 Concelhos
                top_concelhos = Facebook_PCU_Analysis_filtered['user_concelho'].value_counts().head(5)
                top_concelhos_pct = round(
                    (top_concelhos / Facebook_PCU_Analysis_filtered['user_concelho'].value_counts().sum()) * 100, 2)
                top_concelhos_df = pd.DataFrame({
                    'Nº de Utilizadores': top_concelhos,
                    '% de Utilizadores': top_concelhos_pct
                })
                top_concelhos_df.index.name = 'Concelho'
                with col2_F:
                    st.dataframe(top_concelhos_df, use_container_width=True)

                # Top 5 Distritos
                top_distritos = Facebook_PCU_Analysis_filtered['user_distrito'].value_counts().head(5)
                top_distritos_pct = round(
                    (top_distritos / Facebook_PCU_Analysis_filtered['user_distrito'].value_counts().sum()) * 100, 2)
                top_distritos_df = pd.concat([top_distritos, top_distritos_pct], axis=1)
                top_distritos_df.columns = ['Nº de Utilizadores', '% de Utilizadores']
                top_distritos_df.index.name = 'Distrito'
                with col3_F:
                    st.dataframe(top_distritos_df, use_container_width=True)
                    st.write("**USI =** Utilizadores Sem Informação")
                st.divider()

                # Mapa
                merged_dataframe_F, merged_dataframe_C, merged_dataframe_D = mapa_folium_dfs(Facebook_PCU_Analysis_filtered,
                                                                                             map_dataframe=load_map_dataframe())

                folium_static(mapa_folium(merged_dataframe_F, merged_dataframe_C, merged_dataframe_D), width=1420,
                              height=700)
                st.stop()

            except ValueError:  # Se não houver dados para mostrar
                st.write("Não há dados para mostrar com os filtros aplicados.")

        else:
            st.write("Filtre os dados para ver o mapa com os filtros aplicados.")

    # 1st Tab
    with one:
        st.write("## Mapa de Portugal")

        # Cartões com a função create_card() com Nº de Posts, Comentários e Utilizadores Únicos
        col1, col2, col3 = st.columns(3)
        # Cartão 1 | Total de Posts
        pfacd_functions.create_card(col1, "fas fa-newspaper", palette_Mapa[0][0], (255, 255, 255),
                                    "Total de Posts", Facebook_PCU_Analysis['post_id'].nunique())

        # Cartão 2 | Total de Comentários
        pfacd_functions.create_card(col2, "fas fa-comments", palette_Mapa[1][0], (255, 255, 255),
                                    "Total de Comentários", Facebook_PCU_Analysis['comment_id'].nunique())

        # Cartão 3 | Total de Utilizadores Únicos
        pfacd_functions.create_card(col3, "fas fa-users", palette_Mapa[2][0], (255, 255, 255),
                                    "Total de Utilizadores Únicos", Facebook_PCU_Analysis['user_link'].nunique())

        # Top 5 Freguesias, Concelhos e Distritos com mais Utilizadores
        st.markdown("""
            <br><br> 
            <h2 style="color:#175446; font-family:arial; font-size: 20px; font-weight: bold;">
                Top 5 Freguesias, Concelhos e Distritos com + Utilizadores 
            </h2>
            """, unsafe_allow_html=True)
        col1_F, col2_F, col3_F = st.columns(3)

        # Top 5 Freguesias
        top_freguesias = Facebook_PCU_Analysis['user_freguesia'].value_counts().head(5)
        top_freguesias_pct = round((top_freguesias / Facebook_PCU_Analysis['user_freguesia'].value_counts().sum()) * 100, 2)
        top_freguesias_df = pd.concat([top_freguesias, top_freguesias_pct], axis=1)
        top_freguesias_df.columns = ['Nº de Utilizadores', '% de Utilizadores']
        top_freguesias_df.index.name = 'Freguesia'
        with col1_F:
            st.dataframe(top_freguesias_df, use_container_width=True)

        # Top 5 Concelhos
        top_concelhos = Facebook_PCU_Analysis['user_concelho'].value_counts().head(5)
        top_concelhos_pct = round((top_concelhos / Facebook_PCU_Analysis['user_concelho'].value_counts().sum()) * 100, 2)
        top_concelhos_df = pd.DataFrame({
            'Nº de Utilizadores': top_concelhos,
            '% de Utilizadores': top_concelhos_pct
        })
        top_concelhos_df.index.name = 'Concelho'
        with col2_F:
            st.dataframe(top_concelhos_df, use_container_width=True)

        # Top 5 Distritos
        top_distritos = Facebook_PCU_Analysis['user_distrito'].value_counts().head(5)
        top_distritos_pct = round((top_distritos / Facebook_PCU_Analysis['user_distrito'].value_counts().sum()) * 100, 2)
        top_distritos_df = pd.concat([top_distritos, top_distritos_pct], axis=1)
        top_distritos_df.columns = ['Nº de Utilizadores', '% de Utilizadores']
        top_distritos_df.index.name = 'Distrito'
        with col3_F:
            st.dataframe(top_distritos_df, use_container_width=True)
            st.write("**USI =** Utilizadores Sem Informação")

        st.divider()

        # Mapa
        merged_dataframe_F, merged_dataframe_C, merged_dataframe_D = mapa_folium_dfs(Facebook_PCU_Analysis,
                                                                                     map_dataframe=load_map_dataframe())
        folium_static(mapa_folium(merged_dataframe_F, merged_dataframe_C, merged_dataframe_D), width=1420, height=700)

except KeyError or ValueError:
    st.warning("Não há dados para mostrar com os filtros aplicados.")
