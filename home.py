import streamlit as st
from time import sleep
from crud import criar_usuario, ler_usuarios, verifica_senha
from pagina_gestao import pagina_gestao
from pagina_funcionario import pagina_funcionario
# st.set_page_config(page_title='Ponto Brassaco', page_icon=':clock:', layout='wide')
st.logo('logo brassaco.png', icon_image='logo brassaco.png')
usuarios = ler_usuarios()
usuarios = {usuario["nome"]: usuario for usuario in usuarios}

st.session_state['usuarios'] = usuarios

def login():
    with st.container(border=True):    
        nome_usuario = st.selectbox(
            'Selecione o seu nome',
            usuarios.keys(), key=23232, index= None, placeholder="Selecione o Nome",

            )
        
        if nome_usuario is not None:
            usuario = usuarios[nome_usuario]    
        
        senha = st.text_input('Digite sua senha', type='password', key="senha")
        if st.button('Acessar'):
            usuario = usuarios[nome_usuario]
            if  verifica_senha( usuario['password'], senha):
                st.success('Login efetuado com sucesso')
                st.session_state['logado'] = True
                st.session_state['usuario'] = usuario
                st.session_state.senha = ''
                # sleep(1)
                st.rerun()
            else:
                st.error('Senha incorreta')

def pagina_principal():
    # st.write('### Ponto Brassaco')
    usuario = st.session_state['usuario']
    if usuario['adm']:
        st.session_state['adm'] = True
        pagina_gestao()
        st.rerun()
    else:
        pagina_funcionario()
        st.rerun()
     
    


def main():
    if not 'logado' in st.session_state:
        st.session_state['logado'] = False
    if not 'adm' in st.session_state:
        st.session_state['adm'] = False    
    if not st.session_state['logado']:
        st.title('Ponto Brassaco')
        login()
    else:
        pagina_principal()

  
if __name__ == '__main__':
    main()  