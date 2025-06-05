import nltk
import streamlit as st
from st_pages import add_page_title
import pandas as pd
import pfacd_functions
import plotly.express as px
from nltk.tokenize import word_tokenize
from collections import Counter

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# # Download de Recursos do NLTK se ainda não estiverem disponíveis
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

# Configurações da Página
st.set_page_config(layout="wide")
add_page_title(layout="wide")
st.logo(image='static/640px-HD_transparent_picture.png', icon_image='static/ChatMeter_Logo_Bullet.png')
with open('style.css') as f:
    st.markdown(f'''<style>{f.read()}
                    /* Alterar a cor do slider | Fonte: https://discuss.streamlit.io/t/how-to-change-st-sidebar-slider-default-color/3900/2 */
                    div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{{
                        background-color: #7068a8;
                    }}

                    div.stSlider > div[data-baseweb="slider"] > div > div > div > div{{
                        color: #7068a8; 
                    }}

                    div.stSlider > div[data-baseweb = "slider"] > div > div {{
                        background: #7068a8;}}

                    div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {{
                        background: rgb(1 1 1 / 0%); }}

                    .stTabs [data-baseweb="tab"] {{
                        color: #7068a8;
                    }}

                    .stTabs [data-baseweb="tab-highlight"] {{
                        background-color: #7068a8;
                    }}
                    
                    button[kind="secondary"] {{
                        border: 1px solid #7068a8;
                    }}
                    
                    button[kind="secondary"]:hover {{
                        font-weight: bold;
                        color: #7068a8;
                        border: 2px solid #7068a8;
                    }}
                    
            </style>''', unsafe_allow_html=True)
st.write("""Esta página apresenta um conjunto de gráficos que fornecem insights valiosos sobre os dados recolhidos,
         referente à <i><b>Word Analysis</b></i>.""", unsafe_allow_html=True)
st.divider()

# =============================================================================
# Definir Paleta de Cores para Operadoras
palette_operadoras = {
    'DIGI News': '#FFE807',  # Digi News
    'MEO': '#007E8D',        # MEO
    'NOS': '#555555',        # NOS
    'Vodafone': '#E60001'    # Vodafone
}

# Paleta de Cores para Género
colors_gender = {
    'Masculino': '#81BEF7',
    'Feminino': '#F5A9D0',
    'Indeterminado': '#BDBDBD'
}

# Definição de Paletas de Cores para Tópicos - Cartões
palette_TextAnalysis = [
    [(48, 44, 63), '#302c3f'],     # Azul Escuro
    [(112, 104, 168), '#7068a8'],  # Azul Médio
    [(212, 212, 233), '#d4d4e9'],  # Azul Claro
]

# Pallete de Cores para Tópicos - Gráficos
topic_color_mapping = {
    # Tópicos associados às Operadoras
    "Pacotes de Serviços": "#FF5733",
    "Cobertura": "#FFC300",
    "Velocidade": "#C70039",
    "Preços": "#FF3131",
    "Qualidade": "#6704D9",
    "Atendimento ao Cliente": "#FF5733",
    "Concorrência": "#FF0000",
    "5G": "#FF4A00",
    "Satisfação": "#FFD500",
    "Rede": "#005AFF",
    "Fidelização": "#3392FF",
    "Promoções": "#53F601",
    "Segurança": "#2EB025",
    "Plataformas Streaming": "#2721E1",
    "Festivais": "#FD830A",
    "Comunicação": "#2213b1",
    # Tópicos de Eventos Anuais
    "Páscoa": "#FFA600",
    "Natal": "#FF0000",
    "Ano Novo": "#03FFF5",
    "Santos Populares": "#FF3131",
    "Passatempo": "#3392FF",
    "Black Friday": "#000000",
    "Regresso às Aulas": "#7300FF",

    # Tópicos Desportivos
    "Futebol": "#2EB025",
    "Cristiano Ronaldo": "#706C6D",
    "Surf": "#075DFF",
    "Outros desportos": "#53F601",

    # Tópicos Gerais
    "Problemas da Sociedade": "#FF5733",
    "Cinema": "#8A8788",
    "Filme/Série": "#C70039",
    "Economia": "#900C3F",
    "Saúde": "#00FFCF",
    "Videojogo": "#6704D9",
    "Política": "#461F02",
    "Emprego": "#592F03",
    "Tecnologia": "#0D05EC",
    "Inteligência Artificial": "#7300FF",
    "Ambiente": "#53F601",
    "Educação": "#075DFF",
    "Cultura": "#FFD500",
    "Ciência": "#53F601",
    "Arte": "#FF4A00",
    "Religião": "#A56CD3",
    "Negócios": "#52C5B8",
    "Sustentabilidade": "#9CF53E",
    "Moda": "#DC06EC",
    "Alimentação": "#FFA600",
    "Viagens": "#0B51AD",
    "Família": "#EC05F5",
    "Guerra": "#707070",
    "Pandemia": "#3BD293",
    "Redes Sociais": "#005AFF",
    "Sociedade": "#F66527"
}

# ==============================================================================

# =============================================================================
# Import da Base de Dados com Análise
Facebook_PCU_Analysis, Facebook_Posts_Analysis = pfacd_functions.load_data()

Facebook_PCU_Analysis.loc[Facebook_PCU_Analysis['page'].str.contains('DIGI'), 'page'] = 'DIGI News'
Facebook_Posts_Analysis.loc[Facebook_Posts_Analysis['page'].str.contains('DIGI'), 'page'] = 'DIGI News'
# =============================================================================


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
        return Facebook_PCU_Analysis, Facebook_Posts_Analysis

    filtered_Post_df = Facebook_Posts_Analysis.copy()
    filtered_PCU_df = Facebook_PCU_Analysis.copy()

    # # Converter datas para datetime64[ns]
    # filters['start_date'] = pd.to_datetime(filters['start_date'])
    # filters['end_date'] = pd.to_datetime(filters['end_date'])

    # Filtros para Página
    if filters['page'] and len(filters['page']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['page'].isin(filters['page'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['page'].isin(filters['page'])]

    # Filtros para Data
    if filters['start_date'] and filters['end_date']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_date'].dt.date >= filters['start_date']) & (
                filtered_Post_df['post_date'].dt.date <= filters['end_date'])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_date'].dt.date >= filters['start_date']) & (
                filtered_PCU_df['post_date'].dt.date <= filters['end_date'])]

    # Filtros para Sentimento dos Posts
    if filters['sentiment-post'] and len(filters['sentiment-post']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['post_sentiment_label'].isin(filters['sentiment-post'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['post_sentiment_label'].isin(filters['sentiment-post'])]

    # Filtros para Sentimento dos Comentários
    if filters['sentiment-comment'] and len(filters['sentiment-comment']) > 0:
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['comment_sentiment_label'].isin(filters['sentiment-comment'])]

    if filters['n_reacts']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_Post_df['post_reactions'] <= filters['n_reacts'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_PCU_df['post_reactions'] <= filters['n_reacts'][1])]

    # Filtros para Nº de Comentários
    if filters['n_comments']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_Post_df['post_comments'] <= filters['n_comments'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_PCU_df['post_comments'] <= filters['n_comments'][1])]

    # Filtros para Nº de Partilhas
    if filters['n_shares']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_shares'] >= filters['n_shares'][0]) & (
                filtered_Post_df['post_shares'] <= filters['n_shares'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_shares'] >= filters['n_shares'][0]) & (
                filtered_PCU_df['post_shares'] <= filters['n_shares'][1])]

    return filtered_PCU_df, filtered_Post_df


# Filtros | Esquerda
st.markdown("#### Filtros")

# 3 Colunas
col1_F, col2_F, col3_F = st.columns(3)

# Filtro por Data | Intervalo de Datas
start_date, end_date = pfacd_functions.init_page_dates_pickers(Facebook_PCU_Analysis['post_date'], col1_F, col1_F)

# Filtro por Página
with col2_F:
    page_filter = st.multiselect("Página(s)", Facebook_PCU_Analysis['page'].unique(), placeholder="Escolha a Página")

# Filtro por Sentimento
with col3_F:
    lista_sentimentos = ['Positivo', 'Tendência Positiva', 'Neutro', 'Negativo', 'Tendência Negativa']
    sentiment_post_filter = st.multiselect("Sentimento dos Posts",
                                           Facebook_PCU_Analysis['post_sentiment_label'].dropna().unique(),
                                           placeholder="Escolha o Sentimento dos Posts")
    sentiment_comment_filter = st.multiselect("Sentimento dos Comentários",
                                              Facebook_PCU_Analysis['comment_sentiment_label'].dropna().unique(),
                                              placeholder="Escolha o Sentimento dos Comentários")

# 3 Colunas
col1_FF, col2_FF, col3_FF = st.columns(3)

# Filtrar po Nº de Reações
n_reacts = col1_FF.slider("Nº de Reações",
                          min_value=Facebook_PCU_Analysis['post_reactions'].min(),
                          max_value=Facebook_PCU_Analysis['post_reactions'].max(),
                          value=(Facebook_PCU_Analysis['post_reactions'].min(),
                                 Facebook_PCU_Analysis['post_reactions'].max()), format="%d")

# Filtrar por Nº de Comentários
n_comments = col2_FF.slider("Nº de Comentários",
                            min_value=Facebook_PCU_Analysis['post_comments'].min(),
                            max_value=Facebook_PCU_Analysis['post_comments'].max(),
                            value=(Facebook_PCU_Analysis['post_comments'].min(),
                                   Facebook_PCU_Analysis['post_comments'].max()), format="%d")

# Nº de Partilhas
n_shares = col3_FF.slider("Nº de Partilhas",
                          min_value=Facebook_PCU_Analysis['post_shares'].min(),
                          max_value=Facebook_PCU_Analysis['post_shares'].max(),
                          value=(Facebook_PCU_Analysis['post_shares'].min(),
                                 Facebook_PCU_Analysis['post_shares'].max()), format="%d")

if st.button("Filtrar", on_click=click_button, key='filtros_button'):
    Facebook_PCU_Analysis, Facebook_Posts_Analysis = apply_filters({
        'start_date': start_date,
        'end_date': end_date,
        'page': page_filter,
        'sentiment-post': sentiment_post_filter,
        'sentiment-comment': sentiment_comment_filter,
        'n_reacts': n_reacts,
        'n_comments': n_comments,
        'n_shares': n_shares
    })

st.divider()

# ================================================================================================
# Cartões com Nº de Posts, Comentários e Utilizadores Únicos
col1, col2, col3 = st.columns(3)

# Cartão 1 | Total de Posts
pfacd_functions.create_card(col1, "fas fa-newspaper", palette_TextAnalysis[0][0], (255, 255, 255),
                            "Total de Posts", Facebook_Posts_Analysis['post_id'].nunique())

# Cartão 2 | Total de Comentários
pfacd_functions.create_card(col2, "fas fa-comments", palette_TextAnalysis[1][0], (255, 255, 255),
                            "Total de Comentários", Facebook_PCU_Analysis['comment_id'].nunique())

# Cartão 3 | Total de Utilizadores Únicos
pfacd_functions.create_card(col3, "fas fa-users", palette_TextAnalysis[2][0], (255, 255, 255),
                            "Total de Utilizadores Únicos", Facebook_PCU_Analysis['user_link'].nunique())

st.markdown("<br><br>", unsafe_allow_html=True)

# ================================================================================================
# Converter a coluna 'post_date' para o tipo datetime, caso ainda não esteja no formato correto
df_serie_temporal = Facebook_PCU_Analysis.copy()
df_serie_temporal['post_date'] = pd.to_datetime(df_serie_temporal['post_date'])

# 2 Tabs com 'Posts' e 'Comentários'
tab1, tab2 = st.tabs(["Posts", "Comentários"])

try:
    with (tab1):
        # ===================================== POSTS =========================================
        # 3 Colunas
        # col1_P, col2_P, col3_P = st.columns(3)
        col1_P, col2_P = st.columns(2)

        # Gráfico de Barras Horizontais com o TOP 20 Unigramas por Página
        # Função para tokenizar e contar unigramas por página
        def contar_unigramas_por_pagina(df):
            contagens_por_pagina = {}
            for page, group in df.groupby('page'):
                tokens = []
                for post in group['post_text_clean']:
                    tokens.extend(word_tokenize(str(post)))
                contagem_palavras = Counter(tokens)
                contagens_por_pagina[page] = contagem_palavras
            return contagens_por_pagina


        # Contar unigramas por página
        contagens_por_pagina = contar_unigramas_por_pagina(Facebook_Posts_Analysis)

        # Criar DataFrame com as contagens de unigramas
        df_unigramas = pd.DataFrame([
            {'page': page, 'Unigrama': unigrama, 'Contagem': contagem}
            for page, contagens in contagens_por_pagina.items()
            for unigrama, contagem in contagens.items()
        ])

        # Selecionar o TOP 20 Unigramas no Total
        top20_unigramas = df_unigramas.groupby('Unigrama')['Contagem'].sum().sort_values(ascending=False).head(20).index

        # Filtrar o DataFrame para manter apenas os TOP 20 Unigramas
        df_unigramas_top20 = df_unigramas[df_unigramas['Unigrama'].isin(top20_unigramas)]

        # Calcular o total de ocorrências para cada unigrama
        total_unigramas = df_unigramas_top20.groupby('Unigrama')['Contagem'].sum().reset_index().rename(
            columns={'Contagem': 'Total_Contagem'})

        # Mergir com o DataFrame original para adicionar a coluna Total_Contagem
        df_unigramas_top20 = df_unigramas_top20.merge(total_unigramas, on='Unigrama')

        # Ordenar o DataFrame pelo número total de ocorrências
        df_unigramas_top20 = df_unigramas_top20.sort_values(by='Total_Contagem', ascending=True)

        # Gráfico de barras horizontais
        fig_unigramas = px.bar(df_unigramas_top20,
                               x='Contagem',
                               y='Unigrama',
                               orientation='h',
                               color='page',
                               color_discrete_map=palette_operadoras,
                               title="Top 20 Unigramas + Frequentes nos Posts por Página",
                               labels={'Unigrama': 'Unigrama', 'Contagem': 'Contagem'},
                               custom_data=['page'],
                               height=600)

        fig_unigramas.update_layout(
            legend_title_text='Página',
            legend_title_font_size=14,
        )

        fig_unigramas.update_traces(
            hovertemplate='''<b>%{y}</b><br><br>
                            <b>Contagem</b>: %{x}<br>
                            <b>Página</b>: %{customdata[0]}'''
        )

        # Exibir gráfico
        col1_P.plotly_chart(fig_unigramas, use_container_width=True)

        # --------------------------------------------------------------------------------------------
        # Gráfico de Barras Horizontais com o TOP 20 Bigramas por Página
        # Função para tokenizar e contar bigramas por página
        def contar_bigramas_por_pagina(df):
            contagens_por_pagina = {}
            for page, group in df.groupby('page'):
                tokens = []
                for post in group['post_text_clean']:
                    tokens.extend(word_tokenize(str(post)))
                contagem_bigramas = Counter(zip(tokens, tokens[1:]))
                contagens_por_pagina[page] = contagem_bigramas
            return contagens_por_pagina


        # Contar bigramas por página
        contagens_bigramas_por_pagina = contar_bigramas_por_pagina(Facebook_Posts_Analysis)

        # Criar DataFrame com as contagens de bigramas
        df_bigramas = pd.DataFrame([
            {'page': page, 'Bigrama': ' '.join(bigrama), 'Contagem': contagem}
            for page, contagens in contagens_bigramas_por_pagina.items()
            for bigrama, contagem in contagens.items()
        ])

        # Selecionar o TOP 20 Bigramas no Total
        top20_bigramas = df_bigramas.groupby('Bigrama')['Contagem'].sum().sort_values(ascending=False).head(20).index

        # Filtrar o DataFrame para manter apenas os TOP 20 Bigramas
        df_bigramas_top20 = df_bigramas[df_bigramas['Bigrama'].isin(top20_bigramas)]

        # Calcular o total de ocorrências para cada bigrama
        total_bigramas = df_bigramas_top20.groupby('Bigrama')['Contagem'].sum().reset_index().rename(
            columns={'Contagem': 'Total_Contagem'})

        # Mergir com o DataFrame original para adicionar a coluna Total_Contagem
        df_bigramas_top20 = df_bigramas_top20.merge(total_bigramas, on='Bigrama')

        # Ordenar o DataFrame pelo número total de ocorrências
        df_bigramas_top20 = df_bigramas_top20.sort_values(by=['Total_Contagem'], ascending=True)

        # Gráfico de barras horizontais
        fig_bigramas = px.bar(df_bigramas_top20,
                              x='Contagem',
                              y='Bigrama',
                              orientation='h',
                              color='page',
                              color_discrete_map=palette_operadoras,
                              title="Top 20 Bigramas + Frequentes nos Posts por Página",
                              labels={'Bigrama': 'Bigrama', 'Contagem': 'Contagem'},
                              custom_data=['page'],
                              height=600)

        fig_bigramas.update_layout(
            legend_title_text='Página',
            legend_title_font_size=14,
        )

        fig_bigramas.update_traces(
            hovertemplate='''<b>%{y}</b><br><br>
                            <b>Contagem</b>: %{x}<br>
                            <b>Página</b>: %{customdata[0]}''',
        )
        fig_bigramas.update_layout(yaxis={'categoryorder': 'total ascending'})
        col2_P.plotly_chart(fig_bigramas, use_container_width=True)

        # # --------------------------------------------------------------------------------------------
        # # Gráfico de Barras Horizontais com o TOP 20 Trigramas por Página
        # # Função para tokenizar e contar trigramas por página
        # def contar_trigramas_por_pagina(df):
        #     contagens_por_pagina = {}
        #     for page, group in df.groupby('page'):
        #         tokens = []
        #         for post in group['post_text_clean']:
        #             tokens.extend(word_tokenize(str(post)))
        #         contagem_trigramas = Counter(zip(tokens, tokens[1:], tokens[2:]))
        #         contagens_por_pagina[page] = contagem_trigramas
        #     return contagens_por_pagina
        #
        # # Contar trigramas por página
        # contagens_trigramas_por_pagina = contar_trigramas_por_pagina(Facebook_Posts_Analysis)
        #
        # # Criar DataFrame com as contagens de trigramas
        # df_trigramas = pd.DataFrame([
        #     {'page': page, 'Trigrama': ' '.join(trigrama), 'Contagem': contagem}
        #     for page, contagens in contagens_trigramas_por_pagina.items()
        #     for trigrama, contagem in contagens.items()
        # ])
        #
        # # Selecionar o TOP 20 Trigramas no Total
        # top20_trigramas = df_trigramas.groupby('Trigrama')['Contagem'].sum().sort_values(ascending=False).head(20).index
        #
        # # Filtrar o DataFrame para manter apenas os TOP 20 Trigramas
        # df_trigramas_top20 = df_trigramas[df_trigramas['Trigrama'].isin(top20_trigramas)]
        #
        # # Calcular o total de ocorrências para cada trigrama
        # total_trigramas = df_trigramas_top20.groupby('Trigrama')['Contagem'].sum().reset_index().rename(
        #     columns={'Contagem': 'Total_Contagem'})
        #
        # # Mergir com o DataFrame original para adicionar a coluna Total_Contagem
        # df_trigramas_top20 = df_trigramas_top20.merge(total_trigramas, on='Trigrama')
        #
        # # Ordenar o DataFrame pelo número total de ocorrências
        # df_trigramas_top20 = df_trigramas_top20.sort_values(by=['Total_Contagem'], ascending=True)
        #
        # # Gráfico de barras horizontais
        # fig_trigramas = px.bar(df_trigramas_top20,
        #                        x='Contagem',
        #                        y='Trigrama',
        #                        orientation='h',
        #                        color='page',
        #                        color_discrete_map=palette_operadoras,
        #                        title="Top 20 Trigramas + Frequentes nos Posts por Página",
        #                        labels={'Trigrama': 'Trigrama', 'Contagem': 'Contagem'},
        #                        custom_data=['page'],
        #                        height=600)
        #
        # fig_trigramas.update_layout(
        #     legend_title_text='Página',
        #     legend_title_font_size=14,
        # )
        #
        # fig_trigramas.update_traces(
        #     hovertemplate='''<b>%{y}</b><br><br>
        #                      <b>Contagem</b>: %{x}<br>
        #                      <b>Página</b>: %{customdata[0]}''',
        # )
        #
        # fig_trigramas.update_layout(yaxis={'categoryorder': 'total ascending'})
        #
        # col3_P.plotly_chart(fig_trigramas, use_container_width=True)

        # --------------------------------------------------------------------------------------------
        # Word Cloud com os Unigramas mais frequentes
        col1_P.pyplot(pfacd_functions.plot_wordcloud(df_unigramas['Unigrama'], colormap="Greens"))
        # --------------------------------------------------------------------------------------------
        # Word Cloud com os Bigramas mais frequentes
        df_bigramas['Bigrama'] = df_bigramas['Bigrama'].str.replace(' ', '_')
        wordcloud_bigramas_post_text = df_bigramas.loc[df_bigramas.index.repeat(df_bigramas['Contagem']), 'Bigrama']
        # wordcloud_bigramas_post =
        col2_P.pyplot(pfacd_functions.plot_wordcloud(wordcloud_bigramas_post_text, colormap="Blues"))
        # --------------------------------------------------------------------------------------------
        # # Word Cloud com os Trigramas mais frequentes
        # df_trigramas['Trigrama'] = df_trigramas['Trigrama'].str.replace(' ', '_')
        # wordcloud_trigramas_post_text = df_trigramas.loc[df_trigramas.index.repeat(df_trigramas['Contagem']), 'Trigrama']
        # # wordcloud_trigramas_post =
        # col3_P.pyplot(pfacd_functions.plot_wordcloud(wordcloud_trigramas_post_text, colormap="Reds"))
        # --------------------------------------------------------------------------------------------

    with tab2:
        # ===================================== COMENTÁRIOS =========================================

        # 3 Colunas
        # col1_C, col2_C, col3_C = st.columns(3)
        col1_C, col2_C = st.columns(2)

        # Gráfico de Barras Horizontais com o TOP 20 Unigramas por Página
        # Função para tokenizar e contar unigramas por página
        def contar_unigramas_por_pagina(df):
            contagens_por_pagina = {}
            for page, group in df.groupby('page'):
                tokens = []
                for post in group['comment_text_clean']:
                    tokens.extend(word_tokenize(str(post)))
                contagem_palavras = Counter(tokens)
                contagens_por_pagina[page] = contagem_palavras
            return contagens_por_pagina

        # Contar unigramas por página
        contagens_por_pagina = contar_unigramas_por_pagina(Facebook_PCU_Analysis)

        # Criar DataFrame com as contagens de unigramas
        df_unigramas = pd.DataFrame([
            {'page': page, 'Unigrama': unigrama, 'Contagem': contagem}
            for page, contagens in contagens_por_pagina.items()
            for unigrama, contagem in contagens.items()
        ])

        # Selecionar o TOP 20 Unigramas no Total
        top20_unigramas = df_unigramas.groupby('Unigrama')['Contagem'].sum().sort_values(ascending=False).head(20).index

        # Filtrar o DataFrame para manter apenas os TOP 20 Unigramas
        df_unigramas_top20 = df_unigramas[df_unigramas['Unigrama'].isin(top20_unigramas)]

        # Calcular o total de ocorrências para cada unigrama
        total_unigramas = df_unigramas_top20.groupby('Unigrama')['Contagem'].sum().reset_index().rename(
            columns={'Contagem': 'Total_Contagem'})

        # Mergir com o DataFrame original para adicionar a coluna Total_Contagem
        df_unigramas_top20 = df_unigramas_top20.merge(total_unigramas, on='Unigrama')

        # Ordenar o DataFrame pelo número total de ocorrências
        df_unigramas_top20 = df_unigramas_top20.sort_values(by='Total_Contagem', ascending=True)

        # Gráfico de barras horizontais
        fig_unigramas = px.bar(df_unigramas_top20,
                               x='Contagem',
                               y='Unigrama',
                               orientation='h',
                               color='page',
                               color_discrete_map=palette_operadoras,
                               title="Top 20 Unigramas + Frequentes nos Comentários por Página",
                               labels={'Unigrama': 'Unigrama', 'Contagem': 'Contagem'},
                               height=600)

        fig_unigramas.update_layout(
            legend_title_text='Página',
            legend_title_font_size=14,
        )

        fig_unigramas.update_traces(
            hovertemplate='''<b>%{y}</b><br><br>
                            <b>Contagem</b>: %{x}<br>
                            <b>Página</b>: %{customdata[0]}'''
        )

        col1_C.plotly_chart(fig_unigramas, use_container_width=True)

        # --------------------------------------------------------------------------------------------
        # Gráfico de Barras Horizontais com o TOP 20 Bigramas por Página
        # Função para tokenizar e contar bigramas por página
        def contar_bigramas_por_pagina(df):
            contagens_por_pagina = {}
            for page, group in df.groupby('page'):
                tokens = []
                for post in group['comment_text_clean']:
                    tokens.extend(word_tokenize(str(post)))
                contagem_bigramas = Counter(zip(tokens, tokens[1:]))
                contagens_por_pagina[page] = contagem_bigramas
            return contagens_por_pagina

        # Contar bigramas por página
        contagens_bigramas_por_pagina = contar_bigramas_por_pagina(Facebook_PCU_Analysis)

        # Criar DataFrame com as contagens de bigramas
        df_bigramas = pd.DataFrame([
            {'page': page, 'Bigrama': ' '.join(bigrama), 'Contagem': contagem}
            for page, contagens in contagens_bigramas_por_pagina.items()
            for bigrama, contagem in contagens.items()
        ])

        # Selecionar o TOP 20 Bigramas no Total
        top20_bigramas = df_bigramas.groupby('Bigrama')['Contagem'].sum().sort_values(ascending=False).head(20).index

        # Filtrar o DataFrame para manter apenas os TOP 20 Bigramas
        df_bigramas_top20 = df_bigramas[df_bigramas['Bigrama'].isin(top20_bigramas)]

        # Calcular o total de ocorrências para cada bigrama
        total_bigramas = df_bigramas_top20.groupby('Bigrama')['Contagem'].sum().reset_index().rename(
            columns={'Contagem': 'Total_Contagem'})

        # Mergir com o DataFrame original para adicionar a coluna Total_Contagem
        df_bigramas_top20 = df_bigramas_top20.merge(total_bigramas, on='Bigrama')

        # Ordenar o DataFrame pelo número total de ocorrências
        df_bigramas_top20 = df_bigramas_top20.sort_values(by=['Total_Contagem'], ascending=True)

        # Gráfico de barras horizontais
        fig_bigramas = px.bar(df_bigramas_top20,
                              x='Contagem',
                              y='Bigrama',
                              orientation='h',
                              color='page',
                              color_discrete_map=palette_operadoras,
                              title="Top 20 Bigramas + Frequentes nos Comentários por Página",
                              labels={'Bigrama': 'Bigrama', 'Contagem': 'Contagem'},
                              height=600)

        fig_bigramas.update_layout(
            legend_title_text='Página',
            legend_title_font_size=14,
        )

        fig_bigramas.update_traces(
            hovertemplate='''<b>%{y}</b><br><br>
                            <b>Contagem</b>: %{x}<br>
                            <b>Página</b>: %{customdata[0]}'''
        )

        col2_C.plotly_chart(fig_bigramas, use_container_width=True)

        # --------------------------------------------------------------------------------------------

        # # Gráfico de Barras Horizontais com o TOP 20 Trigramas por Página
        # # Função para tokenizar e contar trigramas por página
        # def contar_trigramas_por_pagina(df):
        #     contagens_por_pagina = {}
        #     for page, group in df.groupby('page'):
        #         tokens = []
        #         for post in group['comment_text_clean']:
        #             tokens.extend(word_tokenize(str(post)))
        #         contagem_trigramas = Counter(zip(tokens, tokens[1:], tokens[2:]))
        #         contagens_por_pagina[page] = contagem_trigramas
        #     return contagens_por_pagina
        #
        # # Contar trigramas por página
        # contagens_trigramas_por_pagina = contar_trigramas_por_pagina(Facebook_PCU_Analysis)
        #
        # # Criar DataFrame com as contagens de trigramas
        # df_trigramas = pd.DataFrame([
        #     {'page': page, 'Trigrama': ' '.join(trigrama), 'Contagem': contagem}
        #     for page, contagens in contagens_trigramas_por_pagina.items()
        #     for trigrama, contagem in contagens.items()
        # ])
        #
        # # Selecionar o TOP 20 Trigramas no Total
        # top20_trigramas = df_trigramas.groupby('Trigrama')['Contagem'].sum().sort_values(ascending=False).head(20).index
        #
        # # Filtrar o DataFrame para manter apenas os TOP 20 Trigramas
        # df_trigramas_top20 = df_trigramas[df_trigramas['Trigrama'].isin(top20_trigramas)]
        #
        # # Calcular o total de ocorrências para cada trigrama
        # total_trigramas = df_trigramas_top20.groupby('Trigrama')['Contagem'].sum().reset_index().rename(
        #     columns={'Contagem': 'Total_Contagem'})
        #
        # # Mergir com o DataFrame original para adicionar a coluna Total_Contagem
        # df_trigramas_top20 = df_trigramas_top20.merge(total_trigramas, on='Trigrama')
        #
        # # Ordenar o DataFrame pelo número total de ocorrências
        # df_trigramas_top20 = df_trigramas_top20.sort_values(by=['Total_Contagem'], ascending=True)
        #
        # # Gráfico de barras horizontais
        # fig_trigramas = px.bar(df_trigramas_top20,
        #                        x='Contagem',
        #                        y='Trigrama',
        #                        orientation='h',
        #                        color='page',
        #                        color_discrete_map=palette_operadoras,
        #                        title="Top 20 Trigramas + Frequentes nos Comentários por Página",
        #                        labels={'Trigrama': 'Trigrama', 'Contagem': 'Contagem'},
        #                        height=600)
        #
        # # Exibir gráfico
        # col3_C.plotly_chart(fig_trigramas, use_container_width=True)

        # --------------------------------------------------------------------------------------------
        # Word Cloud com os Unigramas mais frequentes
        col1_C.pyplot(pfacd_functions.plot_wordcloud(df_unigramas['Unigrama'], colormap="Greens"))
        # --------------------------------------------------------------------------------------------
        # Word Cloud com os Bigramas mais frequentes
        df_bigramas['Bigrama'] = df_bigramas['Bigrama'].str.replace(' ', '_')
        wordcloud_bigramas_comment_text = df_bigramas.loc[df_bigramas.index.repeat(df_bigramas['Contagem']), 'Bigrama']
        col2_C.pyplot(pfacd_functions.plot_wordcloud(wordcloud_bigramas_comment_text, colormap="Blues"))
        # --------------------------------------------------------------------------------------------
        # # Word Cloud com os Trigramas mais frequentes
        # df_trigramas['Trigrama'] = df_trigramas['Trigrama'].str.replace(' ', '_')
        # wordcloud_trigramas_comment_text = df_trigramas.loc[df_trigramas.index.repeat(df_trigramas['Contagem']), 'Trigrama']
        # col3_C.pyplot(pfacd_functions.plot_wordcloud(wordcloud_trigramas_comment_text, colormap="Reds"))
        # --------------------------------------------------------------------------------------------

        del df_unigramas, df_bigramas  # , df_trigramas

    # ================================================================================================

except KeyError or ValueError:
    st.warning("Não existem dados para apresentar.")
