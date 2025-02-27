import streamlit as st
import pandas as pd
from bson import ObjectId
from time import sleep
from datetime import datetime

from crud import alterar_usuario, apagar_usuario, criar_usuario 

st.logo('logo brassaco.png', icon_image='logo brassaco.png')
 

def pagina_gestao():

    def logout():
        st.session_state['usuario'] = None
        st.session_state['logado'] = False
        if 'senha' in st.session_state:
            st.session_state['senha'] = ''
        st.session_state.clear()
        st.rerun()
        
    usuarios = st.session_state['usuarios']
    df_todos = pd.DataFrame.from_dict(usuarios, orient="index")
    
    df = df_todos[(df_todos['adm'] != True) & (df_todos['ponto'].notnull())]

    col1, col2 = st.columns(2)
    with col1:
        nome_usuario = st.selectbox(
                'Selecione o Funcionário',
                df.nome,
                )
        df_filtrado = df[df.index == nome_usuario]

    
    pontos = df_filtrado['ponto'].iloc[0]
    df_pontos = pd.DataFrame(pontos)


    selected_month = st.selectbox(
        "Selecione o Mês",
        range(1, 13),
        index=datetime.now().month - 1,
    )


    df_pontos_filtered = df_pontos[df_pontos['registro'].dt.month == selected_month]

    
    # Criar uma coluna 'data' apenas com a data
    df_pontos_filtered['data'] = df_pontos_filtered['registro'].dt.date
    
    # Criar uma coluna 'hora' apenas com a hora
    df_pontos_filtered['hora'] = df_pontos_filtered['registro']
    
    # Pivotar o DataFrame para ter datas como linhas e tipos como colunas
    df_pivot = df_pontos_filtered.pivot_table(index='data', columns='tipo', values='hora', aggfunc='first')
    

    df_pivot.reset_index(inplace=True)
     # Preencher valores ausentes com '00:00:00'
    df_pivot = df_pivot.fillna('00:00:00')

    if df_pontos_filtered.empty:
        st.info('Ainda Não há Registros para esse mês', icon="ℹ️")
        sleep(4)
        logout()


    # Calcular a quantidade de horas trabalhadas
    def calcular_horas_trabalhadas(row):
        if not 'almoco' in df_pivot.columns:
            horas_manha = 0
            df_pivot['almoco'] = '00:00:00'   
        else:    
            horas_manha = (row['almoco'] - row['entrada']).total_seconds() / 3600
        
        if not 'saida' in df_pivot.columns :
            horas_tarde = 0
            df_pivot['saida'] = '00:00:00'
        
        if not 'volta_almoco' in df_pivot.columns:
            horas_tarde = 0
            df_pivot['volta_almoco'] = '00:00:00'
            
        else:    
            horas_tarde = (row['saida'] - row['volta_almoco']).total_seconds() / 3600
        # horas_manha = (row['almoco'] - row['entrada']).total_seconds() / 3600
        
        # horas_tarde = (row['saida'] - row['volta_almoco']).total_seconds() / 3600
        
        if horas_manha < 0:
            horas_manha = 0
        if horas_tarde < 0:   
            horas_tarde = 0 
        total_horas = horas_manha + horas_tarde
        
        horas = int(total_horas)
        minutos = int((total_horas - horas) * 60)
        
        return f'{horas}h {minutos}m' 
    
    df_pivot['Horas do Dia'] = df_pivot.apply(calcular_horas_trabalhadas, axis=1)


     # Formatar as colunas de hora para exibir apenas as horas
    for col in ['entrada', 'almoco', 'volta_almoco', 'saida']:
        df_pivot[col] = df_pivot[col].apply(lambda x: x.strftime('%H:%M:%S') if x != '00:00:00' else '00:00:00')
    
    df_pivot['data'] = pd.to_datetime(df_pivot['data']).dt.strftime('%d/%m/%Y')

        # --- Calculate Accumulated Hours ---
    def to_minutes(time_str):
        """Converts a 'Xh Ym' string to total minutes."""
        if pd.isna(time_str):
          return 0
        if isinstance(time_str, int):
          return time_str
        hours, minutes = map(int, time_str.replace('h', ' ').replace('m', '').split())
        return hours * 60 + minutes

    df_pivot['total_minutes'] = df_pivot['Horas do Dia'].apply(to_minutes)
    df_pivot['accumulated_minutes'] = df_pivot['total_minutes'].cumsum()
    
    def to_time_str(total_minutes):
      """Convert total minutes to Xh Ym string"""
      hours = total_minutes // 60
      minutes = total_minutes % 60
      return f"{hours}h {minutes}m"
    
    df_pivot['Total de Horas'] = df_pivot['accumulated_minutes'].apply(to_time_str)
    
    
    col2.write('Total de Horas ')  
    col2.write(f'##### {df_pivot['Total de Horas'].iloc[-1]}')
    
    st.dataframe(df_pivot[['data','entrada', 'almoco', 'volta_almoco', 'saida', 'Horas do Dia', 'Total de Horas']])

    
    
    with st.sidebar:
       tab1, tab2, tab3 = st.tabs(["Editar", "Incluir", "Apagar"])
       with tab1:
            usuario = st.selectbox(
                    'Selecione o Funcionário',
                    df_todos.nome, key=1
                    )
            editar = df_todos[df_todos.index == usuario]
        
            nome = st.text_input(
                'Nome do usuário para modificar', 
                value=editar.nome.item()
                )
            senha = st.text_input('Senha do usuário', value='xxxxx')
            email = st.text_input(
                'Email para modificar', 
                value=editar.email.item()
                ) 
            loja = st.text_input(
                'Loja para modificar', 
                value=editar.loja.item()
                ) 
            adm = st.checkbox('Administrador ?', value=editar.adm.item() ,key=5)
        
            if st.button('Modificar'):
                id = editar._id.item()
                if senha == 'xxxxx':
                    alterar_usuario(id, nome = nome, email = email, loja= loja, adm=adm)
                else:
                    alterar_usuario(id, password=senha, nome = nome, email = email, loja= loja, adm=adm)
            with tab2:
                nome = st.text_input('Nome')
                senha = st.text_input('Senha')
                email = st.text_input('Email')
                loja = st.text_input('Loja')
                adm = st.checkbox('Administrador ?' , key=3)
                if st.button('Criar'):
                    criar_usuario(nome, email, senha, loja, adm)
                    st.rerun()  
            with tab3:
                usuario = st.selectbox(
                    'Selecione o Funcionário',
                    df_todos.nome, key=23
                    )
                funcionario = df_todos[df_todos.index == usuario]
                id = funcionario['_id'].iloc[0]
                if st.button('Apagar'):
                    apagar_usuario(id)
                    st.toast('Apagado com Sucesso', icon='🗑️')
                    st.rerun()
                    
    
    def logout():
        st.session_state['usuario'] = None
        st.session_state['logado'] = False
        if 'senha' in st.session_state:
            st.session_state['senha'] = ''
        st.session_state.clear()
        st.rerun()
       
    if st.sidebar.button('Sair', type="primary"):
        logout()
                

                


          

    

    