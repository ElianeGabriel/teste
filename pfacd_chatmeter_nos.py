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
                        background-color: #555555;
                    }}
                    
                    div.stSlider > div[data-baseweb="slider"] > div > div > div > div{{
                        color: #555555; 
                    }}
                    
                    div.stSlider > div[data-baseweb = "slider"] > div > div {{
                        background: #555555;}}
                        
                    div.stSlider > div[data-baseweb = "slider"] > div[data-testid="stTickBar"] > div {{
                        background: rgb(1 1 1 / 0%); }}
                        
                    .stTabs [data-baseweb="tab"] {{
                        color: #555555;
                    }}
                    
                    .stTabs [data-baseweb="tab-highlight"] {{
                        background-color: #222222;
                    }}
                    
                    button[kind="secondary"] {{
                        border: 1px solid #222222;
                    }}
                    
                    button[kind="secondary"]:hover {{
                        font-weight: bold;
                        color: #222222;
                        border: 2px solid #222222;
                    }}
                        
            </style>''', unsafe_allow_html=True)
st.write("""Esta página apresenta um conjunto de gráficos que fornecem insights valiosos sobre os dados recolhidos,
         referente à <b>NOS</b>.""", unsafe_allow_html=True)
st.divider()

# ================================================================================================
# Definir Paletas de Cores da NOS
palette_NOS = [
    '#222222',  # Cinzento Escuro
    '#555555',  # Cinzento
    '#aaaaaa',  # Cinzento Claro
]

# Paleta de Cores para Género
colors_gender = {
    'Masculino': '#81BEF7',
    'Feminino': '#F5A9D0',
    'Indeterminado': '#BDBDBD'
}

# ================================================================================================
# Import da Base de Dados com Análise
Facebook_PCU_Analysis, Facebook_Posts_Analysis = pfacd_functions.load_data()
Facebook_PCU_Analysis = Facebook_PCU_Analysis[Facebook_PCU_Analysis['page'] == 'NOS']
Facebook_Posts_Analysis = Facebook_Posts_Analysis[Facebook_Posts_Analysis['page'] == 'NOS']

# ================================================================================================
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

    # Filtro por Data | Intervalo de Datas - Post e PCU
    if filters['start_date'] and filters['end_date']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_date'] >= filters['start_date']) & (
                filtered_Post_df['post_date'] <= filters['end_date'])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_date'] >= filters['start_date']) & (
                filtered_PCU_df['post_date'] <= filters['end_date'])]

    # Filtro por Posts que incluem 'NOS' - Post e PCU
    if filters['post_NOS_filter']:
        filtered_Post_df = filtered_Post_df[filtered_Post_df['post_text_NOS'] == 1]
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['post_text_NOS'] == 1]

    # Filtro por Comentários que incluem 'NOS' - PCU
    if filters['comment_NOS_filter']:
        filtered_PCU_df = filtered_PCU_df[filtered_PCU_df['comment_text_NOS'] == 1]

    # Filtro por Nº de Reações - Post e PCU
    if filters['n_reacts']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_Post_df['post_reactions'] <= filters['n_reacts'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_reactions'] >= filters['n_reacts'][0]) & (
                filtered_PCU_df['post_reactions'] <= filters['n_reacts'][1])]

    # Filtro por Nº de Comentários - Post e PCU
    if filters['n_comments']:
        filtered_Post_df = filtered_Post_df[(filtered_Post_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_Post_df['post_comments'] <= filters['n_comments'][1])]
        filtered_PCU_df = filtered_PCU_df[(filtered_PCU_df['post_comments'] >= filters['n_comments'][0]) & (
                filtered_PCU_df['post_comments'] <= filters['n_comments'][1])]

    # Filtro por Nº de Partilhas - Post e PCU
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
start_date, end_date = pfacd_functions.init_page_dates_pickers(Facebook_PCU_Analysis['post_date'], col1_F, col2_F)

with col3_F:
    # Filtro por Posts que incluem 'NOS'
    post_NOS_filter = st.checkbox("Apenas Posts que Incluem **NOS**", value=False)

    # Filtro por Comentários que incluem 'NOS'
    comment_NOS_filter = st.checkbox("Apenas Comentários que Incluem **NOS**", value=False)

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
        'post_NOS_filter': post_NOS_filter,
        'comment_NOS_filter': comment_NOS_filter,
        'n_reacts': n_reacts,
        'n_comments': n_comments,
        'n_shares': n_shares
    })

st.divider()

# ================================================================================================
# Cartões com Nº de Posts, Comentários e Utilizadores Únicos
col1, col2, col3 = st.columns(3)

# Cartão 1 | Total de Posts
pfacd_functions.create_card(col1, "fas fa-newspaper", (34, 34, 34), (255, 255, 255),
                            "Total de Posts", Facebook_PCU_Analysis['post_id'].nunique())

# Cartão 2 | Total de Comentários
pfacd_functions.create_card(col2, "fas fa-comments", (85, 85, 85), (255, 255, 255),
                            "Total de Comentários", Facebook_PCU_Analysis['comment_id'].nunique())

# Cartão 3 | Total de Utilizadores Únicos
pfacd_functions.create_card(col3, "fas fa-users", (170, 170, 170), (255, 255, 255),
                            "Total de Utilizadores Únicos", Facebook_PCU_Analysis['user_link'].nunique())

st.markdown("<br><br>", unsafe_allow_html=True)

# ================================================================================================
# 3 Tabs com 'Posts', 'Comentários' e 'Users'
tab1, tab2, tab3 = st.tabs(["Posts", "Comentários", "Utilizadores"])

try:
    # ===================================== POSTS =========================================
    with tab1:
        st.write("# Posts")

        # Calcular o número total de comentários por mês para cada página por sentimento
        posts_per_month = Facebook_Posts_Analysis.groupby(['page', pd.Grouper(key='post_date', freq='M')])['post_id'] \
            .nunique().reset_index(name='Total de Publicações')

        # Gráfico de Linhas
        fig_plot_line = px.line(posts_per_month, x='post_date', y='Total de Publicações',
                                title='Total de Publicações por Mês')
        fig_plot_line.update_traces(line_color='#222222', line_width=1)
        fig_plot_line.update_layout(
            xaxis_title='Data',
            yaxis_title='Total de Publicações',
            legend_title='Página',
            font=dict(
                family='Arial',
                size=12,
                color='black'
            )
        )

        fig_plot_line.update_traces(hovertemplate='<b>Data</b>: %{x}<br><b>Total de Publicações</b>: %{y}')

        col1_P, col2_P = st.columns([0.7, 0.3])
        col1_P.plotly_chart(fig_plot_line, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        with col2_P:
            # Calcular a tabela de frequência dos posts por dia da semana
            posts_per_weekday = pd.pivot_table(Facebook_Posts_Analysis,
                                               index='post_weekday',
                                               columns='page',
                                               values='post_id',
                                               aggfunc='nunique')

            # Reindexar a tabela de acordo com a lista de dias da semana ordenada
            ordered_weekdays = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado',
                                'Domingo']
            posts_per_weekday = posts_per_weekday.reindex(ordered_weekdays)

            # Renomear as colunas para tornar mais claro o conteúdo
            posts_per_weekday.index.name = 'Dia da Semana'
            posts_per_weekday_percent = round(posts_per_weekday.div(posts_per_weekday.sum(axis=0), axis=1) * 100, 2)

            posts_per_weekday_df = pd.DataFrame({
                'n': posts_per_weekday['NOS'],
                '%': posts_per_weekday_percent['NOS']
            })
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("##### Posts por Dia da Semana")
            st.dataframe(posts_per_weekday_df, use_container_width=True)

            # Tabela de Frequência de Posts por Ano
            posts_per_year = Facebook_Posts_Analysis.groupby(['page', pd.Grouper(key='post_date', freq='Y')])['post_id'] \
                .nunique().reset_index(name='Total de Publicações')
            posts_per_year['post_date'] = posts_per_year['post_date'].dt.year.astype(str)
            posts_per_year = posts_per_year.pivot(index='post_date', columns='page', values='Total de Publicações')

            # Calcular a percentagem de posts por ano na mesma tabela
            posts_per_year_percent = round(posts_per_year.div(posts_per_year.sum(axis=0), axis=1) * 100, 2)
            posts_per_year_percent.columns = ['%']
            posts_per_year.columns = ['n']
            posts_per_year = pd.concat([posts_per_year, posts_per_year_percent], axis=1)
            posts_per_year.index.name = 'Ano'

            col1_A, col2_A = st.columns(2)
            col1_A.dataframe(posts_per_year[0:3], use_container_width=True)
            col2_A.dataframe(posts_per_year[3:], use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        with col1_P:
            col1_T, col2_T, col3_T = st.columns(3)
            # Cartão 1.1 | Média de Posts diários
            pfacd_functions.create_card(col1_T, "fas fa-newspaper", (34, 34, 34), (255, 255, 255),
                                        "Média Diária de Posts",
                                        int(Facebook_PCU_Analysis['post_id'].nunique() / Facebook_PCU_Analysis['post_date'].nunique()))

            # Cartão 1.2 | Média de Posts Mensais
            pfacd_functions.create_card(col2_T, "fas fa-newspaper", (85, 85, 85), (255, 255, 255),
                                        "Média Mensal de Posts",
                                        int(Facebook_PCU_Analysis['post_id'].nunique() / Facebook_PCU_Analysis['post_date'].dt.month.nunique()))

            # Cartão 1.3 | Média de Posts Anuais
            pfacd_functions.create_card(col3_T, "fas fa-newspaper", (170, 170, 170), (255, 255, 255),
                                        "Média Anual de Posts", int(Facebook_PCU_Analysis['post_id'].nunique() / Facebook_PCU_Analysis['post_date'].dt.year.nunique()))

        # -------------------------------------------------------------------------------------------------
        # Top 5 Posts com + Interações (Tens de Agrupar os posts por post_id e somar as interações)
        top_posts = Facebook_PCU_Analysis.groupby(['post_id', 'post_text'])[['post_reactions', 'post_comments', 'post_shares']].sum().reset_index()
        top_posts = top_posts.sort_values(by=['post_reactions', 'post_comments', 'post_shares'], ascending=False).head(5)

        # Por como index o 'post_text' e não ver o 'post_id'
        top_posts = top_posts.set_index('post_text')
        top_posts = top_posts.drop(columns='post_id')
        top_posts = top_posts.rename(columns={'post_reactions': 'Reações', 'post_comments': 'Comentários', 'post_shares': 'Partilhas'})

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Top 5 Posts com Mais Interações")
        st.dataframe(top_posts, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Contagem de post_id por mDeBERTa_post_CR_label (para perceber se Carece de Resposta ou Não)
        posts_per_CR_label = Facebook_PCU_Analysis['mDeBERTa_post_CR_label'].value_counts().reset_index()
        posts_per_CR_label.columns = ['CR Label', 'Total de Posts']

        # Calcular a percentagem para cada CR Label
        posts_per_CR_label['Percentagem'] = (posts_per_CR_label['Total de Posts'] / posts_per_CR_label['Total de Posts'].sum()) * 100

        # Criar o gráfico de barras
        fig_plot_bar = px.bar(posts_per_CR_label, x='CR Label', y='Total de Posts',
                              title='Total de Posts por CR Label',
                              color='CR Label',
                              color_discrete_map={'Carece de Resposta': palette_NOS[0], 'Não Carece de Resposta': palette_NOS[1]})

        # Adicionar anotações de percentagem no topo das barras
        for i, row in posts_per_CR_label.iterrows():
            fig_plot_bar.add_annotation(
                x=row['CR Label'],
                y=row['Total de Posts'],
                text=f"{row['Percentagem']:.2f}%",
                showarrow=False,
                font=dict(
                    family='Arial',
                    size=12,
                    color='black'
                ),
                yshift=10  # Ajustar o deslocamento vertical das anotações, se necessário
            )

        fig_plot_bar.update_layout(
            xaxis_title='CR Label',
            yaxis_title='Total de Posts',
            font=dict(
                family='Arial',
                size=12,
                color='black'
            )
        )

        fig_plot_bar.update_traces(hovertemplate='<b>CR Label</b>: %{x}<br><b>Total de Posts</b>: %{y}')

        col1_G, col2_G = st.columns(2)
        col1_G.plotly_chart(fig_plot_bar, use_container_width=True)

        # Tabela de Frequências ('n' e '%') de post_id por Mês
        posts_per_month = pd.pivot_table(Facebook_Posts_Analysis,
                                         index=pd.Grouper(key='post_month'),  # , freq='Y'),
                                         columns='page',
                                         values='post_id',
                                         aggfunc='nunique')

        # Lista de meses em ordem cronológica
        ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
                          'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        # Reindexar a tabela de acordo com a lista de meses ordenada
        posts_per_month = posts_per_month.reindex(ordered_months)

        # Renomear as colunas para tornar mais claro o conteúdo
        posts_per_month.columns = [f'{col}' for col in posts_per_month.columns]
        posts_per_month.index.name = 'Mês'
        posts_per_month_percent = round(posts_per_month.div(posts_per_month.sum(axis=0), axis=1) * 100, 2)
        posts_per_month['%'] = posts_per_month_percent
        posts_per_month.columns = ['n', '%']

        with col2_G:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Total de Publicações por Mês")
            col1_G1, col2_G1 = st.columns(2)

            col1_G1.dataframe(posts_per_month[0:6], use_container_width=True)
            col2_G1.dataframe(posts_per_month[6:], use_container_width=True)

        # -------------------------------------------------------------------------------------------------

        # Soma de post shares, soma de post reactions e contagem de post comments por mês (agrupar por post_id)
        posts_per_SRC = Facebook_PCU_Analysis.groupby(['post_id', pd.Grouper(key='post_date', freq='D')]) \
            .agg({'post_shares': 'sum', 'post_reactions': 'sum', 'post_comments': 'sum'}).reset_index()

        # Gráfico de Área
        posts_per_SRC_plot = px.area(
            posts_per_SRC,
            x='post_date',
            y=['post_shares', 'post_reactions', 'post_comments'],
            labels={'post_shares': 'Partilhas', 'post_reactions': 'Reações', 'post_comments': 'Comentários'},
            title='Total de Partilhas, Reações e Comentários por Dia',
            color_discrete_sequence=palette_NOS
        )
        posts_per_SRC_plot.update_traces(stackgroup=None, fill='tozeroy')

        names = {'post_shares': 'Partilhas', 'post_reactions': 'Reações', 'post_comments': 'Comentários'}
        posts_per_SRC_plot.for_each_trace(lambda t: t.update(name=names[t.name]))
        posts_per_SRC_plot.update_layout(
            title='Total de Partilhas, Reações e Comentários por Mês',
            xaxis_title='Data',
            yaxis_title='Total',
            font=dict(
                family='Arial',
                size=12,
                color='black'
            ),
            legend=dict(
                title='Tipo de Interação'
            )
        )

        posts_per_SRC_plot.update_traces(
            hovertemplate='<b>Data</b>: %{x}<br><b>Nº de Interações=</b>: %{y}'
        )

        st.plotly_chart(posts_per_SRC_plot, use_container_width=True)


    # ===================================== COMENTÁRIOS =========================================
    with tab2:
        st.write("# Comentários")

        comments_per_month = Facebook_PCU_Analysis.groupby(['page', pd.Grouper(key='post_date', freq='M')])['comment_id'] \
            .nunique().reset_index(name='Total de Comentários')

        # Gráfico de Linhas
        fig_plot_line = px.line(comments_per_month, x='post_date', y='Total de Comentários',
                                title='Total de Comentários por Mês')
        fig_plot_line.update_traces(line_color='#555555', line_width=1)
        fig_plot_line.update_layout(
            xaxis_title='Data',
            yaxis_title='Total de Comentários',
            legend_title='Página',
            font=dict(
                family='Arial',
                size=12,
                color='black'
            )
        )

        fig_plot_line.update_traces(hovertemplate='<b>Data</b>: %{x}<br><b>Total de Comentários</b>: %{y}')

        col1_C, col2_C = st.columns([0.7, 0.3])
        col1_C.plotly_chart(fig_plot_line, use_container_width=True)

        with col1_C:
            col1_TC, col2_TC, col3_TC = st.columns(3)

            # Cartão 2.1 | Média de Comentários Diários
            pfacd_functions.create_card(col1_TC, "fas fa-comments", (34, 34, 34), (255, 255, 255),
                                        "Média Diária de Comentários", int(Facebook_PCU_Analysis['comment_id'].nunique() / Facebook_PCU_Analysis['post_date'].nunique()))

            # Cartão 2.2 | Média de Comentários Mensais
            pfacd_functions.create_card(col2_TC, "fas fa-comments", (85, 85, 85), (255, 255, 255),
                                        "Média Mensal de Comentários", int(Facebook_PCU_Analysis['comment_id'].nunique() / Facebook_PCU_Analysis['post_date'].dt.month.nunique()))

            # Cartão 2.3 | Média de Comentários Anuais
            pfacd_functions.create_card(col3_TC, "fas fa-comments", (170, 170, 170), (255, 255, 255),
                                        "Média Anual de Comentários", int(Facebook_PCU_Analysis['comment_id'].nunique() / Facebook_PCU_Analysis['post_date'].dt.year.nunique()))

        # -------------------------------------------------------------------------------------------------
        with col2_C:
            # Calcular a tabela de frequência dos comentários por dia da semana
            comments_per_weekday = pd.pivot_table(Facebook_PCU_Analysis,
                                                  index='post_weekday',
                                                  columns='page',
                                                  values='comment_id',
                                                  aggfunc='nunique')

            # Reindexar a tabela de acordo com a lista de dias da semana ordenada
            ordered_weekdays = ['Segunda-feira', 'Terça-feira', 'Quarta-feira', 'Quinta-feira', 'Sexta-feira', 'Sábado', 'Domingo']
            comments_per_weekday = comments_per_weekday.reindex(ordered_weekdays)

            # Renomear as colunas para tornar mais claro o conteúdo
            comments_per_weekday.index.name = 'Dia da Semana'
            comments_per_weekday_percent = round(comments_per_weekday.div(comments_per_weekday.sum(axis=0), axis=1) * 100, 2)

            comments_per_weekday_df = pd.DataFrame({
                'n': comments_per_weekday['NOS'],
                '%': comments_per_weekday_percent['NOS']
            })
            st.markdown("<br><br>", unsafe_allow_html=True)
            st.markdown("##### Comentários por Dia da Semana")
            st.dataframe(comments_per_weekday_df, use_container_width=True)

            # Tabela de Frequência de Comentários por Ano
            comments_per_year = Facebook_PCU_Analysis.groupby(['page', pd.Grouper(key='post_date', freq='Y')])['comment_id'] \
                .nunique().reset_index(name='Total de Comentários')
            comments_per_year['post_date'] = comments_per_year['post_date'].dt.year.astype(str)
            comments_per_year = comments_per_year.pivot(index='post_date', columns='page', values='Total de Comentários')

            # Calcular a percentagem de comentários por ano na mesma tabela
            comments_per_year_percent = round(comments_per_year.div(comments_per_year.sum(axis=0), axis=1) * 100, 2)
            comments_per_year_percent.columns = ['%']
            comments_per_year.columns = ['n']
            comments_per_year = pd.concat([comments_per_year, comments_per_year_percent], axis=1)
            comments_per_year.index.name = 'Ano'

            col1_AC, col2_AC = st.columns(2)
            col1_AC.dataframe(comments_per_year[0:3], use_container_width=True)
            col2_AC.dataframe(comments_per_year[3:], use_container_width=True)

        # -------------------------------------------------------------------------------------------------

        # Top 5 Comentários com + Reações (Tens de Agrupar os comentários por comment_id e ordenar pelas reações)
        top_comments = Facebook_PCU_Analysis.groupby(['comment_id', 'comment_text'])[['comment_reactions', 'comment_num_responses']].sum().reset_index()
        top_comments = top_comments.sort_values(by=['comment_reactions', 'comment_num_responses'], ascending=False).head(5)

        # Por como index o 'comment_text' e não ver o 'comment_id'
        top_comments = top_comments.set_index('comment_text')
        top_comments = top_comments.drop(columns='comment_id')
        top_comments = top_comments.rename(columns={'comment_reactions': 'Nº de Reações', 'comment_num_responses': 'Nº de Respostas'})

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Top 5 Comentários com Mais Reações")
        st.dataframe(top_comments, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Contagem de comment_id por mDeBERTa_comment_CR_label (para perceber se Carece de Resposta ou Não)
        comments_per_CR_label = Facebook_PCU_Analysis['mDeBERTa_comment_CR_label'].value_counts().reset_index()
        comments_per_CR_label.columns = ['CR Label', 'Total de Comentários']

        # Calcular a percentagem para cada CR Label
        comments_per_CR_label['Percentagem'] = (comments_per_CR_label['Total de Comentários'] / comments_per_CR_label['Total de Comentários'].sum()) * 100

        # Criar o gráfico de barras
        fig_plot_bar = px.bar(comments_per_CR_label, x='CR Label', y='Total de Comentários',
                              title='Total de Comentários por CR Label',
                              color='CR Label',
                              color_discrete_map={'Carece de Resposta': palette_NOS[0], 'Não Carece de Resposta': palette_NOS[1]})

        # Adicionar anotações de percentagem no topo das barras
        for i, row in comments_per_CR_label.iterrows():
            fig_plot_bar.add_annotation(
                x=row['CR Label'],
                y=row['Total de Comentários'],
                text=f"{row['Percentagem']:.2f}%",
                showarrow=False,
                font=dict(
                    family='Arial',
                    size=12,
                    color='black'
                ),
                yshift=10
            )

        fig_plot_bar.update_layout(
            xaxis_title='CR Label',
            yaxis_title='Total de Comentários',
            font=dict(
                family='Arial',
                size=12,
                color='black'
            )
        )

        fig_plot_bar.update_traces(hovertemplate='<b>CR Label</b>: %{x}<br><b>Total de Comentários</b>: %{y}')

        col1_GC, col2_GC = st.columns(2)
        col1_GC.plotly_chart(fig_plot_bar, use_container_width=True)

        # Tabela de Frequências ('n' e '%') de comment_id por Mês
        comments_per_month = pd.pivot_table(Facebook_PCU_Analysis,
                                            index=pd.Grouper(key='post_month'),  # , freq='Y'),
                                            columns='page',
                                            values='comment_id',
                                            aggfunc='nunique')

        # Lista de meses em ordem cronológica
        ordered_months = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 'Julho',
                          'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']

        # Reindexar a tabela de acordo com a lista de meses ordenada
        comments_per_month = comments_per_month.reindex(ordered_months)

        # Renomear as colunas para tornar mais claro o conteúdo
        comments_per_month.columns = [f'{col}' for col in comments_per_month.columns]
        comments_per_month.index.name = 'Mês'
        comments_per_month_percent = round(comments_per_month.div(comments_per_month.sum(axis=0), axis=1) * 100, 2)
        comments_per_month['%'] = comments_per_month_percent
        comments_per_month.columns = ['n', '%']

        with col2_GC:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown("### Total de Comentários por Mês")
            col1_GC1, col2_GC1 = st.columns(2)

            col1_GC1.dataframe(comments_per_month[0:6], use_container_width=True)
            col2_GC1.dataframe(comments_per_month[6:], use_container_width=True)

    # ===================================== UTILIZADORES =========================================
    with tab3:
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
            color_continuous_scale='Greys'
        )

        fig_utilizadores_por_distrito.update_traces(hovertemplate='<b>Distrito</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')

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
            color_continuous_scale='Greys'
        )

        fig_utilizadores_por_concelho.update_traces(hovertemplate='<b>Concelho</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')

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
            color_continuous_scale='Greys'
        )

        fig_utilizadores_por_freguesia.update_traces(hovertemplate='<b>Freguesia</b>: %{x}<br><b>Total de Utilizadores</b>: %{y}')

        col3_U.plotly_chart(fig_utilizadores_por_freguesia, use_container_width=True)

        st.markdown("<br><br>", unsafe_allow_html=True)
        # -------------------------------------------------------------------------------------------------
        col1_U11, col2_U11 = st.columns([0.6, 0.4])

        # Cartão 3.1 | Média de Utilizadores Únicos Diários
        pfacd_functions.create_card(col2_U11, "fas fa-users", (34, 34, 34), (255, 255, 255),
                                    "Média Diária de Utilizadores Únicos", int(Facebook_PCU_Analysis['user_link'].nunique() / Facebook_PCU_Analysis['post_date'].nunique()))

        # Cartão 3.2 | Média de Utilizadores Únicos Mensais
        pfacd_functions.create_card(col2_U11, "fas fa-users", (85, 85, 85), (255, 255, 255),
                                    "Média Mensal de Utilizadores Únicos", int(Facebook_PCU_Analysis['user_link'].nunique() / Facebook_PCU_Analysis['post_date'].dt.month.nunique()))

        # Cartão 3.3 | Média de Utilizadores Únicos Anuais
        pfacd_functions.create_card(col2_U11, "fas fa-users", (170, 170, 170), (255, 255, 255),
                                    "Média Anual de Utilizadores Únicos", int(Facebook_PCU_Analysis['user_link'].nunique() / Facebook_PCU_Analysis['post_date'].dt.year.nunique()))

        # -------------------------------------------------------------------------------------------------
        # Série Temporal de Utilizadores Únicos
        users_per_month = Facebook_PCU_Analysis.groupby(['page', pd.Grouper(key='post_date', freq='M')])['user_link'] \
            .nunique().reset_index(name='Total de Utilizadores')

        # Gráfico de Linhas
        fig_plot_line = px.line(users_per_month, x='post_date', y='Total de Utilizadores',
                                title='Total de Utilizadores Únicos por Mês')
        fig_plot_line.update_traces(line_color='#555555', line_width=1)
        fig_plot_line.update_layout(
            xaxis_title='Data',
            yaxis_title='Total de Utilizadores Únicos',
            legend_title='Página',
            font=dict(
                family='Arial',
                size=12,
                color='black'
            )
        )

        fig_plot_line.update_traces(hovertemplate='<b>Data</b>: %{x}<br><b>Total de Utilizadores Únicos</b>: %{y}')

        col1_U11.plotly_chart(fig_plot_line, use_container_width=True)

        # -------------------------------------------------------------------------------------------------
        # Agrupar por Distrito, Concelho e Freguesia por user_link único e sem 'USI' (Users Sem Informação)
        df_treemap = Facebook_PCU_Analysis.copy()
        df_treemap = df_treemap[df_treemap['user_distrito'] != 'USI']
        df_treemap = df_treemap[df_treemap['user_concelho'] != 'USI']
        df_treemap = df_treemap[df_treemap['user_freguesia'] != 'USI']

        # Agrupar por user_link único
        df_treemap = df_treemap.groupby(['user_distrito', 'user_concelho', 'user_freguesia'])[
            'user_link'].size().reset_index(name='count')

        # TreeMap de Utilizadores por Distrito, Concelho e Frequesia
        fig_treemap = px.treemap(df_treemap,
                                 path=['user_distrito', 'user_concelho', 'user_freguesia'],
                                 title='Total de Utilizadores por Distrito, Concelho e Freguesia',
                                 values='count',
                                 color='count',
                                 color_continuous_scale='Greys',
                                 height=1200)
        fig_treemap.update_layout(
            font=dict(
                family='Arial',
                size=12,
                color='black'
            )
        )

        col1_U11.plotly_chart(fig_treemap, use_container_width=True)
        # -------------------------------------------------------------------------------------------------
        # Calcular a tabela de frequência dos utilizadores por género
        users_per_genre = Facebook_PCU_Analysis['user_predicted_genre'].value_counts().reset_index()
        users_per_genre.columns = ['Género', 'Total de Utilizadores']

        # Calculando a percentagem para cada género
        users_per_genre['Percentagem'] = (users_per_genre['Total de Utilizadores'] / users_per_genre['Total de Utilizadores'].sum()) * 100

        # Criando o gráfico de barras
        fig_plot_bar = px.bar(users_per_genre, x='Género', y='Total de Utilizadores',
                              title='Total de Utilizadores por Género',
                              color='Género',
                              color_discrete_map=colors_gender)

        # Adicionando anotações de percentagem no topo das barras
        for i, row in users_per_genre.iterrows():
            fig_plot_bar.add_annotation(
                x=row['Género'],
                y=row['Total de Utilizadores'],
                text=f"{row['Percentagem']:.2f}%",
                showarrow=False,
                font=dict(
                    family='Arial',
                    size=12,
                    color='black'
                ),
                yshift=10
            )

        fig_plot_bar.update_layout(
            xaxis_title='Género',
            yaxis_title='Total de Utilizadores',
            font=dict(
                family='Arial',
                size=12,
                color='black'
            )
        )

        col2_U11.plotly_chart(fig_plot_bar, use_container_width=True)

        # ================================================================================================
        # Gráfico de Icicle para género e dia da semana
        df = Facebook_PCU_Analysis.copy()

        # Filtrar para incluir apenas "Masculino", "Feminino" e "Indeterminado"
        df = df[df['user_predicted_genre'].isin(['Masculino', 'Feminino', 'Indeterminado'])]

        # Agrupar dados por Género e Dia da Semana
        grouped_df = df.groupby(['user_predicted_genre', 'post_weekday']).size().reset_index(name='Total de Utilizadores')

        # Calcular percentagem para cada género e dia da semana
        total_users = grouped_df['Total de Utilizadores'].sum()
        grouped_df['Percentagem'] = (grouped_df['Total de Utilizadores'] / total_users) * 100

        # Adicionar uma coluna com o Total de tudo
        grouped_df["Todos"] = "Todos"

        # Criar o gráfico de icicle com Plotly Express
        fig_gender_weekday = px.icicle(
            grouped_df,
            path=['Todos', 'user_predicted_genre', 'post_weekday'],
            values='Total de Utilizadores',
            color='user_predicted_genre',
            color_discrete_map=colors_gender,
            height=600,
            custom_data=['Percentagem']
        )
        fig_gender_weekday.update_layout(
            title='Distribuição de Utilizadores por Género e Dia da Semana',
            font=dict(
                family='Arial',
                size=14,
                color='black'
            )
        )
        fig_gender_weekday.update_traces(hovertemplate='''<b>Género</b>: %{label}<br>
                                                          <b>Dia da Semana</b>: %{parent}<br>
                                                          <b>Total de Utilizadores</b>: %{value}<br>
                                                          <b>Percentagem</b>: %{customdata[0]:.1f}%''')

        # Exibir o gráfico no Streamlit
        col1_U11.plotly_chart(fig_gender_weekday, use_container_width=True)

    # -------------------------------------------------------------------------------------------------
except KeyError or ValueError:
    st.warning("Não existem dados para apresentar.")
