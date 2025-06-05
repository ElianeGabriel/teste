# ======
# Função:

######################### MAL FEITO #########################
'''
# Top 5 Freguesias
top_freguesias = Facebook_PCU_Analysis_filtered['user_freguesia'].value_counts().head(5)
top_freguesias_pct = (top_freguesias / Facebook_PCU_Analysis_filtered[
    'user_freguesia'].value_counts().sum()) * 100
top_freguesias_df = pd.concat([top_freguesias.reset_index(), top_freguesias_pct.reset_index()], axis=1)
top_freguesias_df.columns = ['Freguesia', 'Nº de Utilizadores', '% de Utilizadores']
col1_F.table(top_freguesias_df)

# Top 5 Concelhos
top_concelhos = Facebook_PCU_Analysis_filtered['user_concelho'].value_counts().head(5)
top_concelhos_pct = (top_concelhos / Facebook_PCU_Analysis_filtered['user_concelho'].value_counts().sum()) * 100
top_concelhos_df = pd.concat([top_concelhos.reset_index(), top_concelhos_pct.reset_index()], axis=1)
top_concelhos_df.columns = ['Concelho', 'Nº de Utilizadores', '% de Utilizadores']
col2_F.table(top_concelhos_df)

# Top 5 Distritos
top_distritos = Facebook_PCU_Analysis_filtered['user_distrito'].value_counts().head(5)
top_distritos_pct = (top_distritos / Facebook_PCU_Analysis_filtered['user_distrito'].value_counts().sum()) * 100
top_distritos_df = pd.concat([top_distritos.reset_index(), top_distritos_pct.reset_index()], axis=1)
top_distritos_df.columns = ['Distrito', 'Nº de Utilizadores', '% de Utilizadores']
col3_F.table(top_distritos_df)
'''


# # Spinner para o Mapa                      --------------------------------------- Confirmar se isto não está a demorar mais tempo
# if st.session_state.clicked:
#     with st.spinner("A processar..."):
#         time.sleep(8)
#     with st.spinner("A criar..."):
#         time.sleep(8)
#     with st.spinner("A ficar bonito..."):
#         time.sleep(8)
#     with st.spinner("Mesmo a acabar..."):
#         time.sleep(8)
#     alert = st.success('Esperemos que já tenha carregado!')  # Display the alert
#     time.sleep(5)  # Wait for 3 seconds
#     alert.empty()  # Clear the alert

# start_date, end_date = st.slider("Intervalo de Datas",
#                                  min_value=Facebook_PCU_Analysis['post_date'].dt.date.min(),
#                                  max_value=Facebook_PCU_Analysis['post_date'].dt.date.max(),
#                                  value=(Facebook_PCU_Analysis['post_date'].dt.date.min(),
#                                         Facebook_PCU_Analysis['post_date'].dt.date.max()))


# Streamlit.py
# Importar a base de dados
Facebook_PCU_Analysis = load_data()

# with st.sidebar:

#     st.header('ChatMeter')

#     st.markdown("# Filtros")
#     selected_page = st.selectbox("Select Page", Facebook_PCU_Analysis['page'].unique())
#     st.markdown("<hr>", unsafe_allow_html=True)


# sentiment_options = ['Positive', 'Negative', 'Neutral']
# selected_sentiment = st.selectbox("Select Sentiment", sentiment_options)

# ----------------------------------------------------------------

# Criar o Facebook_Posts_Analysis
Facebook_Posts_Analysis = Facebook_PCU_Analysis.groupby('post_id').first().reset_index()

# Selecionar apenas as colunas relevantes para o Facebook_Posts_Analysis
Facebook_Posts_Analysis = Facebook_Posts_Analysis[
    ['post_id', 'page', 'post_link', 'post_date',

     # 'post_day', 'post_month', 'post_year', 'post_hour', 'post_language',
     'post_reactions', 'post_comments',
     'post_shares', 'post_text', 'post_text_clean',
     'TXRBSF_post_sentiment_label', 'TXRBSF_post_sentiment_score',
     'mDeBERTa_post_sentiment_label', 'mDeBERTa_post_sentiment_score',
     'post_text_Vodafone', 'post_text_MEO',
     'post_text_NOS', 'post_text_DIGI',
     'mDeBERTa_post_topic_label_1', 'mDeBERTa_post_topic_score_1',
     'mDeBERTa_post_topic_label_2', 'mDeBERTa_post_topic_score_2',
     'mDeBERTa_post_topic_label_3', 'mDeBERTa_post_topic_score_3',
     'mDeBERTa_post_CR_label', 'mDeBERTa_post_CR_score']]

# Criar o Facebook_Comments_Analysis
Facebook_Comments_Analysis = Facebook_PCU_Analysis.groupby('comment_id').first().reset_index()

# =============================================================================

st.header('nada', divider='grey')
st.title(':darkblue[Chatmeter] 🌡️')

# Add a text
st.write("Hello, Streamlit!")

st.markdown('### Metrics')
col1, col2, col3 = st.columns(3)
col1.metric("Temperature", "70 °F", "1.2 °F")
col2.metric("Wind", "9 mph", "-8%")
col3.metric("Humidity", "86%", "4%")

# Add a filter for the year column
year = st.slider('Year',
                 min_value=Facebook_Comments_Analysis['post_date'].dt.year.min(),
                 max_value=Facebook_Comments_Analysis['post_date'].dt.year.max(),
                 value=Facebook_Comments_Analysis['post_date'].dt.year.min())

st.line_chart(Facebook_Posts_Analysis['post_date'].dt.year.value_counts())

# Filter the dataframe based on the selected year
Facebook_Comments_filtered = Facebook_Comments_Analysis[Facebook_Comments_Analysis['post_date'].dt.year == year]

# Create a bar chart of the 'post_' column
st.bar_chart(Facebook_Comments_filtered['post_date'].dt.year.value_counts())

# ------------------------------------------------------------------------------

# Criar o gráfico circular
colors = ['blue', 'red', 'green', 'yellow']
values = Facebook_Comments_filtered['page'].value_counts()
labels = Facebook_Comments_filtered['page'].unique()
fig = px.pie(values=values, names=labels, title='Distribuição de comentários por página',
             color_discrete_sequence=colors)
fig.update_traces(textinfo='percent+label')
st.plotly_chart(fig)

# ----
# c1, c2 = st.columns((7,3))
# with c1:
#     st.markdown('### Heatmap')
#     plost.time_hist(
#         data=Facebook_PCU_Analysis,
#         date='post_date',
#         x_unit='week',
#         y_unit='day',
#         color='red',
#         aggregate='median',
#         legend=None,
#         height=345,
#         use_container_width=True
#     )

# with c2:
#     st.markdown('### Donut chart')
#     plost.donut_chart(
#         data=Facebook_Comments_Analysis,
#         theta='page',
#         color='company',
#         legend='bottom',
#         use_container_width=True
#     )