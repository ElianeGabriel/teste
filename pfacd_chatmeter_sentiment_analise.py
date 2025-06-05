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
                        background-color: #7201d4;
                    }}

                    div.stSlider > div[data-baseweb="slider"] > div > div > div > div{{
                        color: #7201d4; 
                    }}

                    div.stSlider > div[data-baseweb = "slider"] > div > div {{
                        background: #7201d4;}}

                    div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {{
                        background: rgb(1 1 1 / 0%); }}
                        
                    .stTabs [data-baseweb="tab"] {{
                        color: #39006a;
                    }}
                    
                    .stTabs [data-baseweb="tab-highlight"] {{
                        background-color: #7201d4;
                    }}
                    
                    button[kind="secondary"] {{
                        border: 1px solid #7201d4;
                    }}
                    
                    button[kind="secondary"]:hover {{
                        font-weight: bold;
                        color: #7201d4;
                        border: 2px solid #7201d4;
                    }}

            </style>''', unsafe_allow_html=True)
st.write("""Esta página apresenta um conjunto de gráficos que fornecem insights valiosos sobre os dados recolhidos,
         referente ao <i><b>Sentiment Analysis</b></i>.""", unsafe_allow_html=True)
st.divider()

# ================================================================================================
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

# Paleta de Cores para Sentimentos - Cartões
palette_Sentimento = [
    [(57, 0, 106), '#39006a'],  # Roxo Escuro
    [(114, 1, 212), '#7201d4'],  # Roxo
    [(200, 138, 254), '#c88afe'],  # Roxo Claro
]

# Paleta de Cores para Sentimentos - Gráficos
sentiment_colors = {'Positivo': '#64C548', 'Tendência Positiva': '#EBA722',
                    'Neutro': '#F47131',
                    'Tendência Negativa': '#F03F42', 'Negativo': '#CF213D'}

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

    # Filtrar por Página
    if filters['page'] and len(filters['page']) > 0:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['page'].isin(filters['page'])]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['page'].isin(filters['page'])]

    # Filtrar por Data
    if filters['start_date'] and filters['end_date']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_date'] >= filters['start_date']) & (
                filtered_Post_df['post_date'] <= filters['end_date'])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_date'] >= filters['start_date']) & (
                filtered_PCU_df['post_date'] <= filters['end_date'])]

    # Filtrar por Tópico
    if filters['topic-post'] and len(filters['topic-post']) > 0:
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['mDeBERTa_post_topic_label_1'].isin(filters['topic-post'])]
        filtered_Post_df = filtered_Post_df[filtered_Post_df['mDeBERTa_post_topic_label_1'].isin(filters['topic-post'])]

    # Filtrar por Tópico dos Comentários
    if filters['topic-comment'] and len(filters['topic-comment']) > 0:
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['mDeBERTa_comment_topic_label_1'].isin(filters['topic-comment'])]

    # Filtrar por Nº de Reações
    if filters['n_reacts']:
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_PCU_df['post_reactions'] <= filters['n_reacts'][1])]
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_Post_df['post_reactions'] <= filters['n_reacts'][1])]

    # Filtrar por Nº de Comentários
    if filters['n_comments']:
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_PCU_df['post_comments'] <= filters['n_comments'][1])]
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_Post_df['post_comments'] <= filters['n_comments'][1])]

    # Filtrar por Nº de Partilhas
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

# Filtros por Operadora
with col2_F:
    page_filter = st.multiselect("Página(s)", Facebook_PCU_Analysis['page'].unique(), placeholder="Escolha a Página")

with col3_F:
    # Filtro por Tópico
    topic_post_filter = st.multiselect("Tópico dos Posts",
                                       Facebook_PCU_Analysis['mDeBERTa_post_topic_label_1'].unique(),
                                       placeholder="Escolha o Tópico dos Posts")

    topic_comment_filter = st.multiselect("Tópico dos Comentários",
                                          Facebook_PCU_Analysis['mDeBERTa_comment_topic_label_1'].unique(),
                                          placeholder="Escolha o Tópico dos Comentários")

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
        'page': page_filter,
        'start_date': start_date,
        'end_date': end_date,
        'topic-post': topic_post_filter,
        'topic-comment': topic_comment_filter,
        'n_reacts': n_reacts,
        'n_comments': n_comments,
        'n_shares': n_shares
    })

st.divider()

# ================================================================================================
# Cartões com Nº de Posts, Comentários e Utilizadores Únicos
col1, col2, col3 = st.columns(3)

# Cartão 1 | Total de Posts
pfacd_functions.create_card(col1, "fas fa-newspaper", palette_Sentimento[0][0], (255, 255, 255),
                            "Total de Posts", Facebook_Posts_Analysis['post_id'].nunique())

# Cartão 2 | Total de Comentários
pfacd_functions.create_card(col2, "fas fa-comments", palette_Sentimento[1][0], (255, 255, 255),
                            "Total de Comentários", Facebook_PCU_Analysis['comment_id'].nunique())

# Cartão 3 | Total de Utilizadores Únicos
pfacd_functions.create_card(col3, "fas fa-users", palette_Sentimento[2][0], (255, 255, 255),
                            "Total de Utilizadores Únicos", Facebook_PCU_Analysis['user_link'].nunique())

st.markdown("<br><br>", unsafe_allow_html=True)

# ================================================================================================

# 3 Tabs com 'Posts', 'Comentários' e 'Users'
tab1, tab2, tab3 = st.tabs(["Posts", "Comentários", "Utilizadores"])

try:
    with tab1:
        # ===================================== POSTS =========================================
        # Série Temporal de Posts, Comments e Reactions
        # Calcular o número total de comentários por mês para cada página por sentimento
        posts_per_month = Facebook_Posts_Analysis.groupby(['post_sentiment_label', pd.Grouper(key='post_date', freq='M')])['post_id'] \
            .nunique().reset_index(name='Total de Publicações')

        fig_publicacoes_por_mes = px.area(
            data_frame=posts_per_month,
            x='post_date',
            y='Total de Publicações',
            color='post_sentiment_label',
            title='Total de Publicações por Mês por Sentimento',
            labels={'post_date': 'Mês'},
            category_orders={
                'post_sentiment_label': ['Positivo', 'Tendência Positiva', 'Neutro', 'Tendência Negativa', 'Negativo'][::-1]},
            color_discrete_map=sentiment_colors,
        )

        # Personalizar os limites do eixo Y
        # fig_publicacoes_por_mes.update_yaxes(range=[0, 50])

        # Adicionar a legenda ao topo do gráfico
        fig_publicacoes_por_mes.update_layout(legend=dict(
            title="Sentimentos",
            orientation="h",
            yanchor="bottom",
            y=0.98,
            xanchor="right",
            x=1
        ))
        fig_publicacoes_por_mes.update_traces(stackgroup=None, fill='tozeroy')
        # Adicionar mais informações a cada ponto do gráfico
        fig_publicacoes_por_mes.update_traces(hovertemplate='''<b>Mês</b>: %{x}<br><b>Total de Publicações</b>: %{y}<br>''')

        col1_g, col2_g = st.columns([0.6, 0.4])
        col1_g.plotly_chart(fig_publicacoes_por_mes, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Pie Chart com a Distribuição de Sentimentos
        fig_dist_sentimentos = px.pie(
            data_frame=Facebook_PCU_Analysis['post_sentiment_label'].value_counts().reset_index(),
            names='post_sentiment_label',
            values='count',
            title='Distribuição de Sentimentos dos Posts',
            color='post_sentiment_label',
            color_discrete_map=sentiment_colors,
            labels={'count': 'Total de Posts'},
            hole=0.5,
        )

        fig_dist_sentimentos.update_layout(legend=dict(
            title="Sentimentos",
            orientation="v",
            yanchor="bottom",
            y=0.7,
            xanchor="right",
            x=1.5
        ))

        col2_g.plotly_chart(fig_dist_sentimentos, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Scatter Plot com Matriz BCG dos Posts por Sentimento (Y=Nº de Comentários, X=Nº de Reactions e Color=Net Promoter Score)

        # Calcular o NPS (Net Promoter Score) dos Comentários do Post [NPS = % de Comentários com Label 'Positivo' e 'Tendência Positiva'
        #                                                                    % de Comentários com Label Negativo e 'Tendência Negativa']
        Facebook_PCU_Analysis['post_nps'] = Facebook_PCU_Analysis['post_sentiment_label'].apply(
            lambda x: (1 if x in ['Positivo', 'Tendência Positiva'] else (-1 if x in ['Negativo', 'Tendência Negativa'] else 0)))

        # Substituir os valores de 'post_nps' por 'Positivo', 'Neutro' e 'Negativo'
        Facebook_PCU_Analysis['post_nps'] = Facebook_PCU_Analysis['post_nps'].map({1: 'Positivo', 0: 'Neutro', -1: 'Negativo'})

        # Cores para o NPS
        nps_colors = {'Positivo': '#64C548', 'Neutro': '#F47131', 'Negativo': '#CF213D'}

        # Criar a Matriz BCG dos Posts
        fig_bcg_posts = px.scatter(
            data_frame=Facebook_PCU_Analysis,
            x='post_comments',
            y='post_reactions',
            color='post_nps',
            title='Matriz da Performance dos Posts por Sentimento',
            labels={'post_reactions': 'Nº de Reactions', 'post_comments': 'Nº de Comentários'},
            category_orders={
                'post_sentiment_label': ['Positivo', 'Neutro', 'Negativo']},
            color_discrete_map=nps_colors,
            custom_data=['page', 'post_date'],
            height=800,
            width=800,
        )
        # Adicionar a legenda ao topo do gráfico
        fig_bcg_posts.update_layout(legend=dict(
                                        title="Sentimentos",
                                        orientation="v",
                                        yanchor="bottom",
                                        y=0.7,
                                        xanchor="right",
                                        x=1
                                    ))

        # Adicionar mais informações a cada ponto do gráfico
        fig_bcg_posts.update_traces(
            hovertemplate='''<b>Operadora</b>: %{customdata[0]}<br><b>Data</b>: %{customdata[1]}<br><b>Nº de Reactions do Comentário</b>: %{x}<br><b>Nº de Comentários do Post</b>: %{y}<br>'''
        )

        # Criar uma coluna para o gráfico
        col1_sa, col2_sa = st.columns([3.5, 1.5])

        col1_sa.plotly_chart(fig_bcg_posts)

        col2_sa.markdown("""
            <br><br><br><br><br><br>
            <b>Matriz da Perfromance dos Posts por Sentimento</b><br>
            <p style="text-align: justify;">
            Esta matriz foi criada adapando a matriz BCG, sendo utilizada para analisar os posts das operadoras de telecomunicações 
            com base no Nº de Reações e Comentários, bem como no Net Promoter Score (NPS).
            </p>
            <b>Fonte:</b> <a href="https://medium.com/@viverdeblog/a-matriz-bcg-na-era-digital-o-que-%C3%A9-e-como-usar-essa-simples-mas-poderosa-ferramenta-para-28de744aadd4">Medium</a>
            <br><br>
            <b>Net Promoter Score (NPS)</b><br>
            <p style="text-align: justify;">
            O Net Promoter Score (NPS) é uma métrica de satisfação do cliente que mede a disposição dos clientes a recomendarem um produto ou serviço.
            <br>
            Adptando esta métrica para os comentários dos posts, o NPS é calculado com base na percentagem de comentários com sentimento positivo e tendência positiva,
            e a % de comentários com sentimento negativo e tendência negativa.
            </p>
            <b>Fonte:</b> <a href="https://www.qualtrics.com/experience-management/customer/net-promoter-score/">Qualtrics</a>
            <br>
            """, unsafe_allow_html=True)

        # -------------------------------------------------------------------------------------------------
        # Gráfico de Barras: Para mostrar a frequência dos principais tópicos discutidos nos posts dos utilizadores por sentimento
        posts_per_topic = Facebook_PCU_Analysis.groupby(['mDeBERTa_post_topic_label_1', 'post_sentiment_label'])[
            'post_id'].size().reset_index(name='count')
        posts_per_topic = posts_per_topic[posts_per_topic['mDeBERTa_post_topic_label_1'] != 'USI']
        posts_per_topic = posts_per_topic.sort_values(by='count', ascending=True)
        fig_topicos_posts = px.bar(
            posts_per_topic,
            x='count',
            y='mDeBERTa_post_topic_label_1',
            title='Tópicos dos Posts por Sentimento',
            labels={'count': 'Total de Posts', 'mDeBERTa_post_topic_label_1': 'Tópicos'},
            color='post_sentiment_label',
            color_discrete_map=sentiment_colors,
            orientation='h',
            height=1400,
        )

        fig_topicos_posts.update_layout(legend=dict(title="Sentimentos"))
        fig_topicos_posts.update_traces(
            hovertemplate='<b>Tópico</b>: %{y}<br><b>Total de Posts</b>: %{x}')

        fig_topicos_posts.update_layout(yaxis={'categoryorder': 'total ascending'})

        st.plotly_chart(fig_topicos_posts, use_container_width=True)

        # -------------------------------------------------------------------------------------------------

    with tab2:
        # ===================================== COMENTÁRIOS =========================================
        # -------------------------------------------------------------------------------------------------
        comments_per_month = Facebook_PCU_Analysis.groupby(['comment_sentiment_label', pd.Grouper(key='post_date', freq='M')])['comment_id'] \
            .size().reset_index(name='Total de Comentários')

        # Séries Temporais de Comentários por Sentimento
        fig_comentarios_por_mes = px.area(
            comments_per_month,
            x='post_date',
            y='Total de Comentários',
            color='comment_sentiment_label',
            title='Total de Comentários por Mês por Sentimento',
            labels={'post_date': 'Mês'},
            color_discrete_map=sentiment_colors,
            category_orders={
                'comment_sentiment_label': ['Positivo', 'Tendência Positiva', 'Neutro', 'Tendência Negativa', 'Negativo']},
            width=800,
        )

        # Adicionar a legenda ao topo do gráfico
        fig_comentarios_por_mes.update_layout(legend=dict(
            title="Sentimentos",
            orientation="h",
            yanchor="bottom",
            y=0.98,
            xanchor="right",
            x=1
        ))

        fig_comentarios_por_mes.update_traces(stackgroup=None, fill='tozeroy')
        col1_g, col2_g = st.columns([0.6, 0.4])

        col1_g.plotly_chart(fig_comentarios_por_mes)

        # -------------------------------------------------------------------------------------------------
        # Pie Chart com a Distribuição de Sentimentos
        fig_dist_sentimentos_comentarios = px.pie(
            data_frame=Facebook_PCU_Analysis['comment_sentiment_label'].value_counts().reset_index(),
            names='comment_sentiment_label',
            values='count',
            title='Distribuição de Sentimentos dos Comentários',
            color='comment_sentiment_label',
            color_discrete_map=sentiment_colors,
            labels={'count': 'Total de Comentários'},
            category_orders={
                'comment_sentiment_label': ['Positivo', 'Tendência Positiva', 'Neutro', 'Tendência Negativa', 'Negativo']},
            hole=0.5,
            width=500,
        )

        fig_dist_sentimentos_comentarios.update_layout(legend=dict(
            title="Sentimentos",
            orientation="v",
            yanchor="bottom",
            y=0.7,
            xanchor="right",
            x=1.5
        ))

        col2_g.plotly_chart(fig_dist_sentimentos_comentarios)

        # -------------------------------------------------------------------------------------------------
        # Scatter Plot com Matriz BCG dos Comentários por Sentimento (Y=Nº de Reações do Comentário, X=Nº de Comentários do Post e Color='comment_sentiment_label')

        # Criar a Matriz BCG dos Comentários
        fig_bcg_comentarios = px.scatter(
            data_frame=Facebook_PCU_Analysis,
            x='comment_reactions',
            y='post_comments',
            color='comment_sentiment_label',
            title='Matriz da Performance dos Comentários por Sentimento',
            labels={'comment_reactions': 'Nº de Reactions do Comentário', 'post_comments': 'Nº de Comentários do Post'},
            category_orders={
                'comment_sentiment_label': ['Positivo', 'Neutro', 'Negativo']},
            color_discrete_map=sentiment_colors,
            custom_data=['page', 'post_date'],
            height=800,
            width=800,
        )

        # Adicionar a legenda ao topo do gráfico
        fig_bcg_comentarios.update_layout(legend=dict(
                                        title="Sentimentos",
                                        orientation="v",
                                        yanchor="bottom",
                                        y=0.7,
                                        xanchor="right",
                                        x=1
                                    ))

        # Adicionar mais informações a cada ponto do gráfico
        fig_bcg_comentarios.update_traces(
            hovertemplate='''<b>Operadora</b>: %{customdata[0]}<br><b>Data</b>: %{customdata[1]}<br><b>Nº de Reactions</b>: %{x}<br><b>Nº de Likes</b>: %{y}<br>'''
        )

        # Criar uma coluna para o gráfico
        col1_sc, col2_sc = st.columns([0.5, 0.5])

        col1_sc.plotly_chart(fig_bcg_comentarios, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Gráfico de Barras: Para mostrar a frequência dos principais tópicos discutidos nos comentários dos utilizadores por sentimento
        comments_per_topic = Facebook_PCU_Analysis.groupby(['mDeBERTa_comment_topic_label_1', 'comment_sentiment_label'])[
            'comment_id'].size().reset_index(name='count')
        comments_per_topic = comments_per_topic[comments_per_topic['mDeBERTa_comment_topic_label_1'] != 'USI']
        comments_per_topic = comments_per_topic.sort_values(by='count', ascending=True)
        fig_topicos_comentarios = px.bar(
            comments_per_topic,
            x='count',
            y='mDeBERTa_comment_topic_label_1',
            title='Tópicos dos Comentários por Sentimento',
            labels={'count': 'Total de Comentários', 'mDeBERTa_comment_topic_label_1': 'Tópicos'},
            color='comment_sentiment_label',
            color_discrete_map=sentiment_colors,
            orientation='h',
            height=1400,
        )

        fig_topicos_comentarios.update_layout(legend=dict(title="Sentimentos"))
        fig_topicos_comentarios.update_traces(hovertemplate='<b>Tópico</b>: %{y}<br><b>Total de Comentários</b>: %{x}')
        fig_topicos_comentarios.update_layout(yaxis={'categoryorder': 'total ascending'})
        col2_sc.plotly_chart(fig_topicos_comentarios, use_container_width=True)


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
            color_continuous_scale='Purples'
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
            color_continuous_scale='Purples'
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
            color_continuous_scale='Purples'
        )

        fig_utilizadores_por_freguesia.update_traces(
            hovertemplate='<b>Freguesia</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')

        col3_U.plotly_chart(fig_utilizadores_por_freguesia, use_container_width=True)

        st.markdown("<br><br>", unsafe_allow_html=True)

        # -------------------------------------------------------------------------------------------------
        # Gráfico de Utilizadores Únicos por Mês por Sentimento
        users_per_month = Facebook_PCU_Analysis.groupby(
            ['comment_sentiment_label', pd.Grouper(key='post_date', freq='M')])['user_link'] \
            .nunique().reset_index(name='Total de Utilizadores Únicos')

        # Séries Temporais de Utilizadores por Sentimento
        fig_utilizadores_por_mes = px.area(
            users_per_month,
            x='post_date',
            y='Total de Utilizadores Únicos',
            color='comment_sentiment_label',
            title='Total de Utilizadores Únicos por Mês por Sentimento',
            labels={'post_date': 'Mês'},
            color_discrete_map=sentiment_colors,
            category_orders={
                'comment_sentiment_label': ['Positivo', 'Tendência Positiva', 'Neutro', 'Tendência Negativa', 'Negativo']},
            width=800,
        )

        # Adicionar a legenda ao topo do gráfico
        fig_utilizadores_por_mes.update_layout(legend=dict(
            title="Sentimentos",
            orientation="h",
            yanchor="bottom",
            y=0.98,
            xanchor="right",
            x=1
        ))

        col1_g, col2_g = st.columns([0.6, 0.4])

        col1_g.plotly_chart(fig_utilizadores_por_mes)

        # -------------------------------------------------------------------------------------------------
        # Pie Chart com a Distribuição de Sentimentos
        fig_dist_sentimentos_utilizadores = px.pie(
            data_frame=Facebook_PCU_Analysis['comment_sentiment_label'].value_counts().reset_index(),
            names='comment_sentiment_label',
            values='count',
            title='Distribuição de Sentimentos dos Utilizadores',
            color='comment_sentiment_label',
            color_discrete_map=sentiment_colors,
            labels={'count': 'Total de Utilizadores Únicos'},
            category_orders={
                'comment_sentiment_label': ['Positivo', 'Tendência Positiva', 'Neutro', 'Tendência Negativa', 'Negativo']},
            hole=0.5,
            width=500,
        )

        fig_dist_sentimentos_utilizadores.update_layout(legend=dict(
            title="Sentimentos",
            orientation="v",
        ))

        fig_dist_sentimentos_utilizadores.update_traces(
            hovertemplate='<b>Sentimento</b>: %{label}<br><b>Total de Utilizadores</b>: %{value}')

        col2_g.plotly_chart(fig_dist_sentimentos_utilizadores)

        # ================================================================================================
        # 3 Colunas
        col1_UG, col2_UG, col3_UG = st.columns([0.3, 0.3, 0.4])

        # Gráfico de Pizza | Proporção de Géneros dos Utilizadores sem 'USI' (Users Sem Informação)
        users_per_genre = Facebook_PCU_Analysis['user_predicted_genre'].value_counts()
        fig_utilizadores_por_genero = px.pie(
            data_frame=users_per_genre,
            names=users_per_genre.index,
            values=users_per_genre.values,
            title='Total de Utilizadores por Género',
            color=users_per_genre.index,
            color_discrete_map={'Feminino': '#FF69B4', 'Masculino': '#1E90FF'},
            hole=0.5,
        )

        col1_UG.plotly_chart(fig_utilizadores_por_genero, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Gráfico por Género e Sentimento dos Utilizadores
        users_per_genre_sentiment = Facebook_PCU_Analysis.groupby(['user_predicted_genre', 'comment_sentiment_label'])[
            'user_link'].nunique().reset_index(name='count')
        fig_genero_sentimento = px.bar(
            users_per_genre_sentiment,
            x='user_predicted_genre',
            y='count',
            title='Total de Utilizadores por Género e Sentimento',
            labels={'count': 'Total de Utilizadores', 'user_predicted_genre': 'Género'},
            color='comment_sentiment_label',
            color_discrete_map=sentiment_colors,
            width=800,
        )

        fig_genero_sentimento.update_layout(legend=dict(title="Sentimentos"))
        fig_genero_sentimento.update_traces(
            hovertemplate='<b>Género</b>: %{x}<br><b>Sentimento</b>: %{color}<br><b>Total de Utilizadores</b>: %{y}')

        col2_UG.plotly_chart(fig_genero_sentimento, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Gráfico por Sentimento e Género dos Utilizadores (X = Sentimento |  Cores = Género)
        users_per_sentiment_genre = Facebook_PCU_Analysis.groupby(['comment_sentiment_label', 'user_predicted_genre'])[
            'user_link'].nunique().reset_index(name='count')
        fig_sentimento_genero = px.bar(
            users_per_sentiment_genre,
            x='comment_sentiment_label',
            y='count',
            title='Total de Utilizadores por Sentimento e Género',
            labels={'count': 'Total de Utilizadores', 'comment_sentiment_label': 'Sentimento'},
            color='user_predicted_genre',
            color_discrete_map={'Feminino': '#FF69B4', 'Masculino': '#1E90FF'},
            width=800,
        )

        fig_sentimento_genero.update_layout(legend=dict(title="Género"))
        fig_sentimento_genero.update_traces(
            hovertemplate='<b>Sentimento</b>: %{x}<br><b>Género</b>: %{color}<br><b>Total de Utilizadores</b>: %{y}')

        col3_UG.plotly_chart(fig_sentimento_genero, use_container_width=True)

    # ================================================================================================

except KeyError or ValueError:
    st.warning("Não existem dados para apresentar.")
