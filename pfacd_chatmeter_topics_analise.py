import streamlit as st
from st_pages import add_page_title
import pandas as pd
import pfacd_functions
import plotly.express as px

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

# Configurações da Página
st.set_page_config(layout="wide")
add_page_title(layout="wide")
st.logo(image='static/640px-HD_transparent_picture.png', icon_image='static/ChatMeter_Logo_Bullet.png')
with open('style.css') as f:
    st.markdown(f'''<style>{f.read()}
                    /* Alterar a cor do slider | Fonte: https://discuss.streamlit.io/t/how-to-change-st-sidebar-slider-default-color/3900/2 */
                    div.stSlider > div[data-baseweb="slider"] > div > div > div[role="slider"]{{
                        background-color: #0066cc;
                    }}

                    div.stSlider > div[data-baseweb="slider"] > div > div > div > div{{
                        color: #0066cc; 
                    }}

                    div.stSlider > div[data-baseweb = "slider"] > div > div {{
                        background: #0066cc;}}

                    div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {{
                        background: rgb(1 1 1 / 0%); }}
                    
                    .stTabs [data-baseweb="tab"] {{
                        color: #003366;
                    }}
                    
                    .stTabs [data-baseweb="tab-highlight"] {{
                        background-color: #0066cc;
                    }}
                    
                    button[kind="secondary"] {{
                        border: 1px solid #0066cc;
                    }}
                    
                    button[kind="secondary"]:hover {{
                        font-weight: bold;
                        color: #0066cc;
                        border: 2px solid #0066cc;
                    }}
                    
            </style>''', unsafe_allow_html=True)
st.write("""Esta página apresenta um conjunto de gráficos que fornecem insights valiosos sobre os dados recolhidos,
         referente ao <i><b>Topic Analysis</b></i>.""", unsafe_allow_html=True)
st.divider()


# =============================================================================
# Definir Paletas de Cores das Operadoras
palette_operadoras = [
    '#FFE807',  # Digi News
    '#007E8D',  # MEO
    '#555555',  # NOS
    '#E60001'   # Vodafone
]

# Paleta de Cores para Género
colors_gender = {
    'Masculino': '#81BEF7',
    'Feminino': '#F5A9D0',
    'Indeterminado': '#BDBDBD'
}

# Definição de Paletas de Cores para Tópicos - Cartões
palette_Topicos = [
    [(0, 51, 102), '#003366'],  # Azul Escuro
    [(0, 102, 204), '#0066cc'],  # Azul Médio
    [(153, 204, 255), '#99ccff'],  # Azul Claro
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

# =============================================================================
# Import da Base de Dados com Análise
Facebook_PCU_Analysis, Facebook_Posts_Analysis = pfacd_functions.load_data()
Facebook_Posts_Analysis.loc[Facebook_Posts_Analysis['page'].str.contains('DIGI'), 'page'] = 'DIGI News'
Facebook_PCU_Analysis.loc[Facebook_PCU_Analysis['page'].str.contains('DIGI'), 'page'] = 'DIGI News'
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

    # Converter datas para datetime64[ns]
    filters['start_date'] = pd.to_datetime(filters['start_date'])
    filters['end_date'] = pd.to_datetime(filters['end_date'])

    # Filtro por Página
    if filters['page'] and len(filters['page']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['page'].isin(filters['page'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['page'].isin(filters['page'])]

    # Filtro por Data
    if filters['start_date'] and filters['end_date']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_date'] >= filters['start_date']) & (
                filtered_Post_df['post_date'] <= filters['end_date'])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_date'] >= filters['start_date']) & (
                filtered_PCU_df['post_date'] <= filters['end_date'])]

    # Filtro por Sentimento do Post
    if filters['sentiment-post'] and len(filters['sentiment-post']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['post_sentiment_label'].isin(filters['sentiment-post'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['post_sentiment_label'].isin(filters['sentiment-post'])]

    # Filtro por Sentimento do Comentário
    if filters['sentiment-comment'] and len(filters['sentiment-comment']) > 0:
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['comment_sentiment_label'].isin(filters['sentiment-comment'])]

    # Filtro por Nº de Reações
    if filters['n_reacts']:
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_PCU_df['post_reactions'] <= filters['n_reacts'][1])]
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_Post_df['post_reactions'] <= filters['n_reacts'][1])]

    # Filtro por Nº de Comentários
    if filters['n_comments']:
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_PCU_df['post_comments'] <= filters['n_comments'][1])]
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_Post_df['post_comments'] <= filters['n_comments'][1])]

    # Filtro por Nº de Partilhas
    if filters['n_shares']:
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_shares'] >= filters['n_shares'][0]) & (
                filtered_PCU_df['post_shares'] <= filters['n_shares'][1])]
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_shares'] >= filters['n_shares'][0]) & (
                filtered_Post_df['post_shares'] <= filters['n_shares'][1])]

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
pfacd_functions.create_card(col1, "fas fa-newspaper", palette_Topicos[0][0], (255, 255, 255),
                            "Total de Posts", Facebook_Posts_Analysis['post_id'].nunique())

# Cartão 2 | Total de Comentários
pfacd_functions.create_card(col2, "fas fa-comments", palette_Topicos[1][0], (255, 255, 255),
                            "Total de Comentários", Facebook_PCU_Analysis['comment_id'].nunique())

# Cartão 3 | Total de Utilizadores Únicos
pfacd_functions.create_card(col3, "fas fa-users", palette_Topicos[2][0], (255, 255, 255),
                            "Total de Utilizadores Únicos", Facebook_PCU_Analysis['user_link'].nunique())

st.markdown("<br><br>", unsafe_allow_html=True)

# ================================================================================================

# 3 Tabs com 'Posts', 'Comentários' e 'Users'
tab1, tab2, tab3 = st.tabs(["Posts", "Comentários", "Utilizadores"])

try:
    with tab1:
        # ===================================== POSTS =========================================
        # Série Temporal de Posts por Tópico
        posts_per_month = Facebook_Posts_Analysis.groupby(['mDeBERTa_post_topic_label_1', pd.Grouper(key='post_date', freq='M')])['post_id'] \
            .nunique().reset_index(name='Total de Publicações')

        fig_posts_por_mes = px.area(
            data_frame=posts_per_month,
            x='post_date',
            y='Total de Publicações',
            color='mDeBERTa_post_topic_label_1',
            title='Total de Publicações por Mês por Tópico',
            labels={'post_date': 'Mês', 'mDeBERTa_post_topic_label_1': 'Tópicos'},
            category_orders={'mDeBERTa_post_topic_label_1': posts_per_month.groupby('mDeBERTa_post_topic_label_1')['Total de Publicações'].sum().sort_values(ascending=False).index}
        )

        fig_posts_por_mes.update_traces(stackgroup=None, fill='tozeroy')
        fig_posts_por_mes.update_traces(hovertemplate='<b>Mês</b>: %{x}<br><b>Total de Publicações</b>: %{y}<br>')
        st.plotly_chart(fig_posts_por_mes, use_container_width=True)

        # -------------------------------------------------------------------------------------------
        # Matriz BCG (x=Saldo de Sentimento | y= Nº de Comentários | cores = Tópicos)
        # Tabela Tópicos com % de posts, % sentimentos positivos, negativos, NPS, Nº de Comentários e Reactions
        topicos_summary = Facebook_Posts_Analysis.groupby('mDeBERTa_post_topic_label_1').agg(
            Página=('page', 'first'),
            post_date=('post_date', 'first'),
            total_posts=('post_id', 'nunique'),
            n_comments=('post_comments', 'sum'),
            n_reactions=('post_reactions', 'sum'),
            pos_sentiment=('post_sentiment_label', lambda x: (x == 'Positivo').sum() + (x == 'Tendência Positiva').sum()),
            neg_sentiment=('post_sentiment_label', lambda x: (x == 'Negativo').sum() + (x == 'Tendência Negativa').sum()),
        ).reset_index()

        topicos_summary['%_posts'] = (topicos_summary['total_posts'] / topicos_summary['total_posts'].sum()) * 100
        topicos_summary['%_pos_sentiment'] = round((topicos_summary['pos_sentiment'] / topicos_summary['total_posts']) * 100, 2)
        topicos_summary['%_neg_sentiment'] = round((topicos_summary['neg_sentiment'] / topicos_summary['total_posts']) * 100, 2)
        topicos_summary['NPS'] = round(topicos_summary['%_pos_sentiment'] - topicos_summary['%_neg_sentiment'], 2)
        topicos_summary.index += 1

        # Ordenar os Tópicos por Número de Posts
        topicos_summary = topicos_summary.sort_values(by=['total_posts'], ascending=False)

        # 2 Colunas
        col1_P, col2_P = st.columns([0.4, 0.6])

        # Matriz da Performance dos Tópicos (Matriz BCG)
        with col2_P:
            fig_bcg_posts = px.scatter(
                data_frame=topicos_summary,
                x='NPS',
                y='n_reactions',
                size='n_comments',
                color='mDeBERTa_post_topic_label_1',
                title='Matriz de Performance dos Tópicos dos Posts',
                labels={'n_reactions': 'Nº de Reactions', 'NPS': 'Saldo de Sentimento', 'mDeBERTa_post_topic_label_1': 'Tópicos'},
                custom_data=['Página', 'post_date'],
                height=800
            )

            fig_bcg_posts.update_traces(marker=dict(line=dict(width=1, color='white')), selector=dict(mode='markers'))
            fig_bcg_posts.update_traces(hovertemplate='<b>Operadora</b>: %{customdata[0]}<br><b>Data</b>: %{customdata[1]}<br><b>Tópico</b>: %{y}<br><b>Total de Posts</b>: %{marker.size}<br><b>Nº de Comentários</b>: %{marker.size}<br><b>Nº de Reactions</b>: %{y}<br><b>Saldo de Sentimento</b>: %{x}')
            st.plotly_chart(fig_bcg_posts, use_container_width=True)

            st.markdown("#### Tabela TOP 5 Tópicos")

            # Tabela com os 5 Tópicos com mais Posts (Renomear as colunas para melhor visualização e por como index o 'mDeBERTa_post_topic_label_1')
            topicos_summary_df = topicos_summary.copy()
            topicos_summary_df = topicos_summary_df.rename(columns={'mDeBERTa_post_topic_label_1': 'Tópico', 'total_posts': 'n', '%_posts': '%',
                                                                    'n_comments': 'Nº de Comentários', 'n_reactions': 'Nº de Reações',
                                                                    'pos_sentiment': 'n Positivos', 'neg_sentiment': 'n Negativos',
                                                                    '%_pos_sentiment': '% Positivos', '%_neg_sentiment': '% Negativos',
                                                                    'NPS': 'SdS'})
            topicos_summary_df = topicos_summary_df.set_index('Tópico')
            st.dataframe(topicos_summary_df[:5][['n', '%', 'Nº de Comentários', 'Nº de Reações', 'n Positivos', 'n Negativos', '% Positivos', '% Negativos', 'SdS']], use_container_width=True)

        # -------------------------------------------------------------------------------------------
        # Gráfico de Barras Horizontais de Tópicos para Posts
        fig_barras_topicos = px.bar(
            topicos_summary,
            x='total_posts',
            y='mDeBERTa_post_topic_label_1',
            orientation='h',
            color='mDeBERTa_post_topic_label_1',
            title='Contagem de Posts por Tópico',
            labels={'total_posts': 'Total de Posts', 'mDeBERTa_post_topic_label_1': 'Tópicos'},
            height=1200
        )
        fig_barras_topicos.update_traces(hovertemplate='<b>Tópico</b>: %{y}<br><b>Total de Posts</b>: %{x}')

        with col1_P:
            st.plotly_chart(fig_barras_topicos, use_container_width=True)

    with tab2:
        # ===================================== COMENTÁRIOS =========================================
        # Série Temporal de Comentários por Tópico
        comments_per_month = Facebook_PCU_Analysis.groupby(['mDeBERTa_comment_topic_label_1', pd.Grouper(key='post_date', freq='M')])['comment_id'] \
            .nunique().reset_index(name='Total de Comentários')

        fig_comments_por_mes = px.area(
            data_frame=comments_per_month,
            x='post_date',
            y='Total de Comentários',
            color='mDeBERTa_comment_topic_label_1',
            title='Total de Comentários por Mês por Tópico',
            category_orders={'mDeBERTa_comment_topic_label_1': comments_per_month.groupby('mDeBERTa_comment_topic_label_1')['Total de Comentários'].sum().sort_values(ascending=False).index},
            labels={'post_date': 'Mês', 'mDeBERTa_comment_topic_label_1': 'Tópicos'},
        )

        fig_comments_por_mes.update_traces(stackgroup=None, fill='tozeroy')
        fig_comments_por_mes.update_traces(hovertemplate='<b>Mês</b>: %{x}<br><b>Total de Comentários</b>: %{y}<br>')
        st.plotly_chart(fig_comments_por_mes, use_container_width=True)

        # -------------------------------------------------------------------------------------------
        # Matriz BCG para Comentários (Y=Nº de Reações do Comentário, X=Nº de Comentários do Post e Color='mDeBERTa_comment_topic_label_1')
        fig_bcg_comments = px.scatter(
            data_frame=Facebook_PCU_Analysis,
            x='post_comments',
            y='comment_reactions',
            color='mDeBERTa_comment_topic_label_1',
            title='Matriz de Performance dos Tópicos (Comentários)',
            labels={'post_comments': 'Nº de Comentários do Post', 'comment_reactions': 'Nº de Reações do Comentário', 'mDeBERTa_comment_topic_label_1': 'Tópicos'},
            custom_data=['page', 'post_date', 'mDeBERTa_comment_CR_label'],
            height=800
        )

        fig_bcg_comments.update_traces(marker=dict(line=dict(width=1, color='white')), selector=dict(mode='markers'))
        fig_bcg_comments.update_traces(hovertemplate='<b>Operadora</b>: %{customdata[0]}<br><b>Data</b>: %{customdata[1]}<br><b>CR</b>: %{customdata[2]}<br><b>Nº de Comentários</b>: %{x}<br><b>Nº de Reações</b>: %{y}')

        # 2 Colunas
        col1_C, col2_C = st.columns([0.6, 0.4])

        with col1_C:
            st.plotly_chart(fig_bcg_comments, use_container_width=True)

            st.markdown("#### Tabela TOP 5 Tópicos + Comentados")
            topicos_summary_comments = Facebook_PCU_Analysis.groupby('mDeBERTa_comment_topic_label_1').agg(
                Página=('page', 'first'),
                total_comments=('comment_id', 'nunique'),
                n_reactions=('comment_reactions', 'sum'),
            ).reset_index()

            topicos_summary_comments['%_comments'] = (topicos_summary_comments['total_comments'] / topicos_summary_comments['total_comments'].sum()) * 100
            topicos_summary_comments.index += 1

            # Ordenar os Tópicos por Número de Comentários
            topicos_summary_comments = topicos_summary_comments.sort_values(by=['total_comments'], ascending=False)

            # Tabela com os 5 Tópicos com mais Comentários (Renomear as colunas para melhor visualização e por como index o 'mDeBERTa_comment_topic_label_1')
            topicos_summary_comments_df = topicos_summary_comments.copy()
            topicos_summary_comments_df = topicos_summary_comments_df.rename(columns={'mDeBERTa_comment_topic_label_1': 'Tópico', 'total_comments': 'n', '%_comments': '%','n_reactions': 'Total de Reações'})
            topicos_summary_comments_df = topicos_summary_comments_df.set_index('Tópico')

            st.dataframe(topicos_summary_comments_df[:5][['n', '%', 'Total de Reações']], use_container_width=True)

        # -------------------------------------------------------------------------------------------

        # Ordenar os Tópicos por Número de Comentários
        topicos_summary_comments = topicos_summary_comments.sort_values(by=['total_comments'], ascending=False)

        fig_barras_topicos_comments = px.bar(
            topicos_summary_comments,
            x='total_comments',
            y='mDeBERTa_comment_topic_label_1',
            orientation='h',
            color='mDeBERTa_comment_topic_label_1',
            title='Contagem de Comentários por Tópico',
            labels={'total_comments': 'Total de Comentários', 'mDeBERTa_comment_topic_label_1': 'Tópicos'},
            height=1200
        )

        col2_C.plotly_chart(fig_barras_topicos_comments, use_container_width=True)

    with tab3:
        # ===================================== UTILIZADORES =========================================
        st.write("# Utilizadores")
        st.write("**USI =** Utilizadores Sem Informação")
        # Filtrar por Freguesia, Concelho e Distrito
        col1_U, col2_U, col3_U = st.columns(3)

        user_distrito = col1_U.selectbox("Distrito", sorted(list(Facebook_PCU_Analysis['user_distrito'].dropna().unique())),
                                         index=None, placeholder='Selecione um Distrito')

        if user_distrito:
            Facebook_PCU_Analysis = Facebook_PCU_Analysis[Facebook_PCU_Analysis['user_distrito'] == user_distrito]

        user_concelho = col2_U.selectbox("Concelho", sorted(list(Facebook_PCU_Analysis['user_concelho'].dropna().unique())),
                                         index=None, placeholder='Selecione um Concelho')
        if user_concelho:
            Facebook_PCU_Analysis = Facebook_PCU_Analysis[Facebook_PCU_Analysis['user_concelho'] == user_concelho]

        user_freguesia = col3_U.selectbox("Freguesia",
                                          sorted(list(Facebook_PCU_Analysis['user_freguesia'].dropna().unique())),
                                          index=None, placeholder='Selecione uma Freguesia')

        if user_freguesia:
            Facebook_PCU_Analysis = Facebook_PCU_Analysis[Facebook_PCU_Analysis['user_freguesia'] == user_freguesia]

        # -------------------------------------------------------------------------------------------------
        # Gráfico de Utilizadores por 'user_distrito' sem 'USI' (Users Sem Informação)
        users_per_distrito = Facebook_PCU_Analysis['user_distrito'].value_counts().reset_index()
        users_per_distrito = users_per_distrito[users_per_distrito['user_distrito'] != 'USI']
        fig_utilizadores_por_distrito = px.bar(
            users_per_distrito,
            x='user_distrito',
            y='count',
            title='Total de Utilizadores por Distrito',
            labels={'count': 'Total de Utilizadores', 'user_distrito': 'Distrito'},
            color='count',
            color_continuous_scale='Blues'
        )

        fig_utilizadores_por_distrito.update_traces(
            hovertemplate='<b>Distrito</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')

        col1_U.plotly_chart(fig_utilizadores_por_distrito, use_container_width=True)

        # Gráfico de Utilizadores por 'user_concelho' sem 'USI' (Users Sem Informação)
        users_per_concelho = Facebook_PCU_Analysis['user_concelho'].value_counts().reset_index()
        users_per_concelho = users_per_concelho[users_per_concelho['user_concelho'] != 'USI']
        fig_utilizadores_por_concelho = px.bar(
            users_per_concelho,
            x='user_concelho',
            y='count',
            title='Total de Utilizadores por Concelho',
            labels={'count': 'Total de Utilizadores', 'user_concelho': 'Concelho'},
            color='count',
            color_continuous_scale='Blues'
        )

        fig_utilizadores_por_concelho.update_traces(
            hovertemplate='<b>Concelho</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')

        col2_U.plotly_chart(fig_utilizadores_por_concelho, use_container_width=True)

        # Gráfico de Utilizadores por 'user_freguesia' sem 'USI' (Users Sem Informação)
        users_per_freguesia = Facebook_PCU_Analysis['user_freguesia'].value_counts().reset_index()
        users_per_freguesia = users_per_freguesia[users_per_freguesia['user_freguesia'] != 'USI']
        fig_utilizadores_por_freguesia = px.bar(
            users_per_freguesia,
            x='user_freguesia',
            y='count',
            text_auto=True,
            title='Total de Utilizadores por Freguesia',
            labels={'count': 'Total de Utilizadores', 'user_freguesia': 'Freguesia'},
            color='count',
            color_continuous_scale='Blues'
        )

        fig_utilizadores_por_freguesia.update_traces(
            hovertemplate='<b>Freguesia</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')

        col3_U.plotly_chart(fig_utilizadores_por_freguesia, use_container_width=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # -------------------------------------------------------------------------------------------------
        # Gráfico de Utilizadores Únicos por 'mDeBERTa_comment_topic_label_1'

        # Tabela com os Utilizadores Únicos por Tópico ('mDeBERTa_comment_topic_label_1') por Género ('user_predicted_genre')
        users_per_topic = Facebook_PCU_Analysis.groupby(['mDeBERTa_comment_topic_label_1', 'user_predicted_genre'])['user_link'].nunique().reset_index(name='Total de Utilizadores')
        users_per_topic = users_per_topic.sort_values(by='Total de Utilizadores', ascending=False)

        # Gráfico de Barras Horizontais
        fig_users_per_topic = px.bar(
            users_per_topic,
            x='mDeBERTa_comment_topic_label_1',
            y='Total de Utilizadores',
            color='user_predicted_genre',
            title='Total de Utilizadores por Tópico e Género',
            labels={'Total de Utilizadores': 'Total de Utilizadores', 'mDeBERTa_comment_topic_label_1': 'Tópico', 'user_predicted_genre': 'Género'},
            color_discrete_map=colors_gender,
            category_orders={'mDeBERTa_comment_topic_label_1': users_per_topic.groupby('mDeBERTa_comment_topic_label_1')['Total de Utilizadores'].sum().sort_values(ascending=False).index},
            height=600
        )

        fig_users_per_topic.update_traces(hovertemplate='<b>Tópico</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')
        st.plotly_chart(fig_users_per_topic, use_container_width=True)

        # -------------------------------------------------------------------------------------------------

except KeyError or ValueError:
    st.warning("Não existem dados para apresentar.")
