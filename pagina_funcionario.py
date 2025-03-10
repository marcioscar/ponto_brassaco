from datetime import datetime
import streamlit as st
import pandas as pd
from bson import ObjectId
from time import sleep
from crud import ler_usuarios, registrar, trocar_senha

st.logo('logo brassaco.png', icon_image='logo brassaco.png')

selected_month = 1

def pagina_funcionario():
    
    usuario = st.session_state['usuario']
    usuario['_id'] = str(usuario['_id'])
    df = pd.DataFrame([usuario])
    
    
    def logout():
        st.session_state['usuario'] = None
        st.session_state['logado'] = False
        if 'senha' in st.session_state:
            st.session_state['senha'] = ''
        st.session_state.clear()
        st.rerun()
    # Check if 'ponto' exists and is not empty
    if 'ponto' in df and not df['ponto'].iloc[0] == []:
        pontos = df['ponto'].iloc[0]
        df_pontos = pd.DataFrame(pontos)
    else:
        st.write(f"O Funcionário  ainda não registrou pontos.")
        st.sidebar.markdown(f'Registrar ponto para **{usuario['nome']}**')
        # data_hoje = datetime.today().strftime('%d/%m/%Y')
        if st.sidebar.button('Entrada'):
            registrar(usuario['_id'], 'entrada')
            st.session_state.senha = ''
            st.session_state.clear()
            st.rerun()
         # Exit the function early if 'ponto' is missing or empty
        return
    
    # Extrair os pontos e criar um DataFrame separado
    pontos = df['ponto'].iloc[0]
    
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
    
    # st.write(df_pontos['data'])
    
   
    df_pontos_filtered['data'] = df_pontos_filtered['registro'].dt.date
    
    


    df_pivot.reset_index(inplace=True)
    
     # Preencher valores ausentes com '00:00:00'
    df_pivot = df_pivot.fillna('00:00:00')
    
    # if df_pontos_filtered.empty:
    #     st.info('Ainda Não há Registros para esse mês', icon="ℹ️")
    #     sleep(4)
    #     logout()
        


    # Calcular a quantidade de horas trabalhadas
    def calcular_horas_trabalhadas(row):
        if not 'almoco' in df_pivot.columns:
            horas_manha = 0
            df_pivot['almoco'] = '00:00:00'   
        else:    
            horas_manha = (row['almoco'] - row['entrada']).total_seconds() / 3600
        
        if not 'volta_almoco' in df_pivot.columns:
            horas_tarde = 0
            df_pivot['volta_almoco'] = '00:00:00'

        if not 'saida' in df_pivot.columns :
            horas_tarde = 0
            df_pivot['saida'] = '00:00:00'    
            
        else:    
            horas_tarde = (row['saida'] - row['volta_almoco']).total_seconds() / 3600
        
        if horas_manha < 0:
            horas_manha = 0
        if horas_tarde < 0:   
            horas_tarde = 0 
        total_horas = horas_manha + horas_tarde
        
        horas = int(total_horas)
        minutos = int((total_horas - horas) * 60)
        
        return f'{horas}h {minutos}m' 
    
    
    df_pivot['Horas do Dia'] = df_pivot.apply(calcular_horas_trabalhadas, axis=1)
    
    # começar daqui
    if df_pivot.empty:
        if st.sidebar.button('Entrada'):
            tipo = 'entrada'
            registrar(usuario['_id'], tipo)
            st.session_state.senha = ''
            st.session_state.clear()
            st.rerun()
        return        
            

     # Formatar as colunas de hora para exibir apenas as horas
    for col in ['entrada', 'almoco', 'volta_almoco', 'saida']:
        df_pivot[col] = df_pivot[col].apply(lambda x: x.strftime('%H:%M:%S') if x != '00:00:00' else '00:00:00')
    
    df_pivot['data'] = pd.to_datetime(df_pivot['data']).dt.strftime('%d/%m/%Y')
    
    # st.write(df_pivot.columns)
    st.sidebar.markdown(f'Registrar ponto para **{usuario['nome']}**')
    data_hoje = datetime.today().strftime('%d/%m/%Y')
    
    

    # if df_pivot['data'].iloc[-1] == data_hoje:
    if df_pivot['entrada'].iloc[-1] == '00:00:00' or not df_pivot['data'].iloc[-1] == data_hoje :
        tipo = 'entrada'
        if st.sidebar.button('Entrada'):
            registrar(usuario['_id'], tipo)
            st.session_state.senha = ''
            st.session_state.clear()
            st.rerun()
            
    elif df_pivot['entrada'].iloc[-1] != '00:00:00' and df_pivot['almoco'].iloc[-1] == '00:00:00':
        tipo = 'almoco'
        if st.sidebar.button('Saída para o almoço'):
            registrar(usuario['_id'], tipo)
            st.session_state.senha = ''
            st.session_state.clear()
            
            
            
    elif df_pivot['entrada'].iloc[-1] != '00:00:00' and df_pivot['almoco'].iloc[-1] != '00:00:00' and df_pivot['volta_almoco'].iloc[-1] == '00:00:00':
        tipo = 'volta_almoco'
        if st.sidebar.button('Volta do almoço'):
            registrar(usuario['_id'], tipo)
            st.session_state.senha = ''
            st.session_state.clear()
            st.rerun()
            
            
            
    elif df_pivot['entrada'].iloc[-1] != '00:00:00' and df_pivot['almoco'].iloc[-1] != '00:00:00' and df_pivot['volta_almoco'].iloc[-1] != '00:00:00' and df_pivot['saida'].iloc[-1] == '00:00:00':
        tipo = 'saida'
        if st.sidebar.button('Saída'):
            registrar(usuario['_id'], tipo)
            st.session_state.senha = ''
            st.session_state.clear()
            st.rerun()
            

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
    
    with st.sidebar.expander('Trocar Senha'):  
        senha = st.text_input('Nova Senha')
        if st.button('Trocar'):
            id = usuario['_id']
            trocar_senha(id, senha)
            logout()
             


    df_pivot['Total de Horas'] = df_pivot['accumulated_minutes'].apply(to_time_str)
    

   


    st.sidebar.write('# Total de Horas ')  
    st.sidebar.write(f'## {df_pivot['Total de Horas'].iloc[-1]}')
    
    
    st.write('### Ponto Brassaco')
    st.dataframe(df_pivot[['data','entrada', 'almoco', 'volta_almoco', 'saida', 'Horas do Dia', 'Total de Horas']])
    # df_container.dataframe(st.session_state.df)            
                
    
       
    # st.dataframe(df_pivot[['data','entrada', 'almoco', 'volta_almoco', 'saida', 'horas_trabalhadas']])
    
    
     
   

  



    # if st.sidebar.button("Trocar a senha"):
        # trocar()

    if st.sidebar.button('Sair', type="primary"):
        logout()

                
            

    
    
    
    

    

    



    
    
    