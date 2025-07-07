import streamlit as st
import requests
import uuid

PROD_URL = "https://scibot-backend.uc.r.appspot.com"

def upload_pdf(files, model=None):
    file = files[0]
    files_payload = {"pdf": (file.name, file, "application/pdf")}
    
    # URL con el parametro model
    url = f"{PROD_URL}/load"
    if model:
        url += f"?model={model}"
    
    response = requests.post(url, files=files_payload)
    if response.status_code == 200:
        return response.json()  # {"session_id": ..., "summary": ...}
    else:
        # valdiar respuesta con error
        error_message = parse_error_message(response.text, response.status_code)
        st.error(error_message)
        return None

def parse_error_message(error_text, status_code):
    """Parse and simplify error messages for better user understanding"""
    try:
        import json
        error_data = json.loads(error_text)
        error_msg = error_data.get("error", "")
        
        # errores especificos
        if "Request body too large" in error_msg:
                return "⚠️ El documento es demasiado grande para este modelo. Intenta con un PDF más pequeño o selecciona otro modelo"
        
        elif "quota" in error_msg.lower() or "limit" in error_msg.lower():
            return "⚠️ Se ha alcanzado el límite de uso del modelo. Intenta más tarde o selecciona otro modelo."
        
        elif "authentication" in error_msg.lower() or "unauthorized" in error_msg.lower():
            return "⚠️ Error de autenticación. Verifica la configuración del servicio."
        
        elif "not found" in error_msg.lower():
            return "⚠️ El modelo seleccionado no está disponible. Intenta con otro modelo."
        
        else:
            return f"⚠️ Error del servidor: {error_msg}"
    
    except:
        # errores con codigos
        if status_code == 400:
            return "⚠️ Error en la solicitud. Verifica el documento o intenta con otro modelo."
        elif status_code == 429:
            return "⚠️ Demasiadas solicitudes. Espera un momento antes de intentar nuevamente."
        elif status_code == 500:
            return "⚠️ Error interno del servidor. Intenta nuevamente en unos minutos o prueba con otro modelo."
        else:
            return f"⚠️ Error del servicio (código {status_code}). Intenta nuevamente."

def ask_question(session_id, question, model=None):
    headers = {"Content-Type": "application/json"}
    json_data = {"message": question}
    
    #URL con session_id y model parameters
    url = f"{PROD_URL}/chat?session_id={session_id}"
    if model:
        url += f"&model={model}"
    
    response = requests.post(url, headers=headers, json=json_data)
    if response.status_code == 200:
        return response.json()  # {"answer": "..."}
    else:
        # simplificar mensasje de error
        error_message = parse_error_message(response.text, response.status_code)
        st.error(error_message)
        return None

def create_new_session(session_number):
    """Create a new session with a numbered display name"""
    return {
        "session_id": None,  # cuando se cargue el PDF se toma el SessionID
        "chat_history": [],
        "display_name": f"Chat {session_number}",
        "has_document": False,
        "selected_model": "meta/Llama-4-Scout-17B-16E-Instruct"  # Default model
    }

def show_welcome_page():
    """Display the welcome page with project information"""
    st.set_page_config(page_title="Sci Bot - Chat con PDF", page_icon="./favicon.png", layout="wide")
    
    # Pantalla Inicio
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.title("Generación Automática de Resúmenes Científicos con Modelos NLP G9")
        
        st.markdown("---")
        
        st.markdown("""
        Este proyecto de titulación consiste en la generación automática de resúmenes científicos 
        utilizando modelos de procesamiento de lenguaje natural (NLP). Se exploran enfoques basados 
        en Deep Learning, incluyendo MLP, Transformers como BERT, y técnicas de Transfer Learning 
        y Fine-Tuning, para mejorar la capacidad de los modelos de sintetizar información relevante 
        y producir resúmenes precisos.
        """)
        
        st.markdown("---")
        
        # Boton Inicio
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("Iniciar Programa", type="primary", use_container_width=True):
                st.session_state.show_main_app = True
                st.rerun()

def main():
    # Iniciar sesion de inicio
    if "show_main_app" not in st.session_state:
        st.session_state.show_main_app = False
    
    # Show welcome page or main app
    if not st.session_state.show_main_app:
        show_welcome_page()
    else:
        show_main_app()

def show_main_app():
    """Display the main PDF chat application"""
    st.set_page_config(page_title="Sci Bot - Chat con PDF", page_icon="./favicon.png", layout="wide")


    if "sessions" not in st.session_state:
        st.session_state.sessions = {"default": create_new_session(1)}
    if "active_session" not in st.session_state:
        st.session_state.active_session = "default"
    if "session_counter" not in st.session_state:
        st.session_state.session_counter = 1
    
    # validar modelo predefinido
    for session_key, session_data in st.session_state.sessions.items():
        if "selected_model" not in session_data:
            session_data["selected_model"] = "meta/Llama-4-Scout-17B-16E-Instruct"

    # Crear sesiones
    session_keys = list(st.session_state.sessions.keys())
    tab_labels = [st.session_state.sessions[key]["display_name"] for key in session_keys]
    tab_labels.append("+ Nuevo Chat")
    
    tabs = st.tabs(tab_labels)
    
    # Boton de nueva sesion o chat
    if len(tabs) > len(session_keys):
        with tabs[-1]:  # Last tab is "Nuevo Chat"
            if st.button("Crear Nuevo Chat", key="new_chat_btn"):
                st.session_state.session_counter += 1
                new_session_key = f"session_{st.session_state.session_counter}"
                st.session_state.sessions[new_session_key] = create_new_session(st.session_state.session_counter)
                st.session_state.active_session = new_session_key
                st.rerun()
            st.info("Haz clic en 'Crear Nuevo Chat' para iniciar una nueva sesión.")
    
    # Mostrar contenido de cada sesion
    for i, session_key in enumerate(session_keys):
        with tabs[i]:
            st.session_state.active_session = session_key
            display_session_content(session_key)

def display_session_content(session_key):
    """Display the content for a specific session"""
    current_session = st.session_state.sessions[session_key]
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("📤 Subir PDF")
        uploaded_file = st.file_uploader("Carga tu PDF", type="pdf", accept_multiple_files=False, key=f"upload_{session_key}")

        if st.button("Procesar", key=f"process_{session_key}") and uploaded_file:
            with st.spinner("Procesando..."):
                selected_model = current_session.get("selected_model", "meta/Llama-4-Scout-17B-16E-Instruct")
                result = upload_pdf([uploaded_file], selected_model)
                if result:
                    current_session["session_id"] = result.get("session_id")
                    summary = result.get("summary")
                    current_session["chat_history"] = []  # Reiniciar chat
                    current_session["chat_history"].append(("SciBot", summary))  # Mostrar resumen en el chat
                    current_session["has_document"] = True
                    st.success("¡Documento procesado!")
                    st.rerun()
        
        # Borrar Chats- Mantiene 1 chat siempre
        if len(st.session_state.sessions) > 1 and session_key != "default":
            if st.button("🗑️ Eliminar Chat", key=f"delete_{session_key}", type="secondary"):
                # Remove the session
                del st.session_state.sessions[session_key]
                # Switch to the first available session
                remaining_sessions = list(st.session_state.sessions.keys())
                st.session_state.active_session = remaining_sessions[0]
                st.rerun()

    with col2:
        # encabezado y selector de modelo
        col_header, col_model = st.columns([2, 1])
        
        with col_header:
            st.header("💬 Chat con el documento")
        
        with col_model:
            # Menu de Modelos
            model_options = {
                "LLama-4": "meta/Llama-4-Scout-17B-16E-Instruct",
                "Grok-3": "xai/grok-3",
                "DeepSeek": "deepseek/DeepSeek-R1-0528",
                "GPT-4.1": "openai/gpt-4.1"
            }
            
            # Seleccion de modelo
            current_model_key = "LLama-4"  # Default
            for key, value in model_options.items():
                if value == current_session.get("selected_model", "meta/Llama-4-Scout-17B-16E-Instruct"):
                    current_model_key = key
                    break
            
            selected_model_key = st.selectbox(
                "Modelo Elegido:",
                options=list(model_options.keys()),
                index=list(model_options.keys()).index(current_model_key),
                key=f"model_selector_{session_key}"
            )
            
            # Cambiar de modelo segun la seleccion
            selected_model_value = model_options[selected_model_key]
            if current_session.get("selected_model") != selected_model_value:
                current_session["selected_model"] = selected_model_value
        
        # Mostrar Chat
        chat_container = st.container()
        with chat_container:
            if current_session["chat_history"]:
                for speaker, msg in current_session["chat_history"]:
                    if speaker == "Tú":
                        st.markdown(f"**🧑 {speaker}:** {msg}")
                    else:
                        st.markdown(f"**🤖 {speaker}:** {msg}")
            elif not current_session["has_document"]:
                st.info("Primero debes subir un documento a la izquierda.")
            else:
                st.info("¡Documento cargado! Puedes hacer preguntas sobre él.")

        # Caja de pregunta
        if current_session["session_id"]:
            st.markdown("---")  
            
            with st.form(key=f"question_form_{session_key}", clear_on_submit=True):
                input_col, button_col = st.columns([5, 1])
                
                with input_col:
                    question = st.text_input(
                        "Pregunta sobre el documento:", 
                        key=f"question_{session_key}",
                        placeholder="Escribe tu pregunta aquí...",
                        label_visibility="visible"
                    )
                
                with button_col:
                    st.markdown("")  
                    ask_button = st.form_submit_button("Preguntar", use_container_width=True)
                
                if ask_button and question.strip():
                    with st.spinner("Obteniendo respuesta..."):
                        selected_model = current_session.get("selected_model", "meta/Llama-4-Scout-17B-16E-Instruct")
                        response = ask_question(current_session["session_id"], question, selected_model)
                        if response and "answer" in response:
                            current_session["chat_history"].append(("Tú", question))
                            current_session["chat_history"].append(("SciBot", response["answer"]))
                            st.rerun()
                elif ask_button and not question.strip():
                    st.warning("Por favor, escribe una pregunta antes de enviar.")

if __name__ == "__main__":
    main()