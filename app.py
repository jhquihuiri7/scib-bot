import streamlit as st
import requests
import uuid

PROD_URL = "https://6ed753424eda.ngrok-free.app"
#PROD_URL = "https://scibot-backend.uc.r.appspot.com"
#PROD_URL = "http://127.0.0.1:8000"

def upload_pdf(files, model=None):
    """
    Sube un archivo PDF al servidor backend para su procesamiento.

    Args:
        files (list): Una lista de archivos subidos (se espera que contenga un archivo PDF).
        model (str, optional): El nombre del modelo a utilizar para el procesamiento. Por defecto es None.

    Returns:
        dict or None: Un diccionario que contiene el session_id y el resumen si tiene éxito, de lo contrario None.
    """
    file = files[0]
    files_payload = {"pdf": (file.name, file, "application/pdf")}
    
    # Construye la URL con el parámetro del modelo si se proporciona
    url = f"{PROD_URL}/load"
    if model:
        url += f"?model={model}"

    print(model)    
    # Envía la solicitud POST al backend
    response = requests.post(url, files=files_payload)

    print(response.text)
    # Maneja la respuesta
    if response.status_code == 200:
        return response.json()
    else:
        # Analiza y muestra el mensaje de error
        error_message = parse_error_message(response.text, response.status_code)
        st.error(error_message)
        return None

def parse_error_message(error_text, status_code):
    """
    Analiza y simplifica los mensajes de error para una mejor comprensión del usuario.

    Args:
        error_text (str): El texto del mensaje de error de la respuesta HTTP.
        status_code (int): El código de estado HTTP.

    Returns:
        str: Un mensaje de error fácil de usar.
    """
    try:
        import json
        error_data = json.loads(error_text)
        error_msg = error_data.get("error", "")
        
        # Maneja mensajes de error específicos
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
        # Maneja errores basados en códigos de estado
        if status_code == 400:
            return "⚠️ Error en la solicitud. Verifica el documento o intenta con otro modelo."
        elif status_code == 429:
            return "⚠️ Demasiadas solicitudes. Espera un momento antes de intentar nuevamente."
        elif status_code == 500:
            return "⚠️ Error interno del servidor. Intenta nuevamente en unos minutos o prueba con otro modelo."
        else:
            return f"⚠️ Error del servicio (código {status_code}). Intenta nuevamente."

def ask_question(session_id, question, model=None):
    """
    Envía una pregunta al backend y obtiene una respuesta.

    Args:
        session_id (str): El ID de la sesión actual.
        question (str): La pregunta del usuario.
        model (str, optional): El modelo a utilizar para la respuesta. Por defecto es None.

    Returns:
        dict or None: Un diccionario que contiene la respuesta si tiene éxito, de lo contrario None.
    """
    headers = {"Content-Type": "application/json"}
    json_data = {"message": question}
    
    # Construye la URL con los parámetros session_id y model
    url = f"{PROD_URL}/chat?session_id={session_id}"
    if model:
        url += f"&model={model}"
    
    # Envía la solicitud POST
    response = requests.post(url, headers=headers, json=json_data)

    # Maneja la respuesta
    if response.status_code == 200:
        return response.json()  # {"answer": "..."}
    else:
        # Analiza y muestra el mensaje de error
        error_message = parse_error_message(response.text, response.status_code)
        st.error(error_message)
        return None

def create_new_session(session_number):
    """
    Crea una nueva sesión con un nombre de visualización numerado.

    Args:
        session_number (int): El número a mostrar para la nueva sesión.

    Returns:
        dict: Un diccionario que representa una nueva sesión.
    """
    return {
        "session_id": None,  # El session_id se asigna después de que se carga un PDF
        "chat_history": [],
        "display_name": f"Chat {session_number}",
        "has_document": False,
        "selected_model": "moonshotai/kimi-vl-a3b-thinking:free"  # Modelo por defecto
    }

def show_welcome_page():
    """
    Muestra la página de bienvenida con información del proyecto.
    Esta es la primera pantalla que ve el usuario.
    """
    st.set_page_config(page_title="Sci Bot - Chat con PDF", page_icon="./favicon.png", layout="wide")
    
    # Diseño de la pantalla de bienvenida
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
        
        # Botón de inicio
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("Iniciar Programa", type="primary", use_container_width=True):
                st.session_state.show_main_app = True
                st.rerun()

def main():
    """
    Función principal para ejecutar la aplicación Streamlit.
    Maneja el estado inicial y cambia entre la página de bienvenida y la aplicación principal.
    """
    # Inicializa el estado de la sesión para la aplicación principal
    if "show_main_app" not in st.session_state:
        st.session_state.show_main_app = False
    
    # Muestra la página de bienvenida o la aplicación principal según el estado
    if not st.session_state.show_main_app:
        show_welcome_page()
    else:
        show_main_app()

def show_main_app():
    """
    Muestra la interfaz principal de la aplicación de chat con PDF.
    Esto incluye la gestión de sesiones, pestañas para diferentes chats y el diseño principal.
    """
    st.set_page_config(page_title="Sci Bot - Chat con PDF", page_icon="./favicon.png", layout="wide")

    # Inicializa el estado de la sesión para las sesiones de chat
    if "sessions" not in st.session_state:
        st.session_state.sessions = {"default": create_new_session(1)}
    if "active_session" not in st.session_state:
        st.session_state.active_session = "default"
    if "session_counter" not in st.session_state:
        st.session_state.session_counter = 1
    
    # Se asegura de que todas las sesiones tengan un modelo predeterminado seleccionado
    for session_key, session_data in st.session_state.sessions.items():
        if "selected_model" not in session_data:
            session_data["selected_model"] = "moonshotai/kimi-vl-a3b-thinking:free"

    # Crea pestañas para cada sesión
    session_keys = list(st.session_state.sessions.keys())
    tab_labels = [st.session_state.sessions[key]["display_name"] for key in session_keys]
    tab_labels.append("+ Nuevo Chat")
    
    tabs = st.tabs(tab_labels)
    
    # Maneja el botón "Nuevo Chat" en la última pestaña
    if len(tabs) > len(session_keys):
        with tabs[-1]:  # La última pestaña es "Nuevo Chat"
            if st.button("Crear Nuevo Chat", key="new_chat_btn"):
                st.session_state.session_counter += 1
                new_session_key = f"session_{st.session_state.session_counter}"
                st.session_state.sessions[new_session_key] = create_new_session(st.session_state.session_counter)
                st.session_state.active_session = new_session_key
                st.rerun()
            st.info("Haz clic en 'Crear Nuevo Chat' para iniciar una nueva sesión.")
    
    # Muestra el contenido de cada sesión en su pestaña
    for i, session_key in enumerate(session_keys):
        with tabs[i]:
            st.session_state.active_session = session_key
            display_session_content(session_key)

def display_session_content(session_key):
    """
    Muestra el contenido de una sesión de chat específica.
    Esto incluye el cargador de archivos, el historial de chat y el formulario de entrada de preguntas.

    Args:
        session_key (str): La clave de la sesión a mostrar.
    """
    current_session = st.session_state.sessions[session_key]
    
    col1, col2 = st.columns([1, 2])

    with col1:
        st.header("📤 Subir PDF")
        uploaded_file = st.file_uploader("Carga tu PDF", type="pdf", accept_multiple_files=False, key=f"upload_{session_key}")

        if st.button("Procesar", key=f"process_{session_key}") and uploaded_file:
            with st.spinner("Procesando..."):
                selected_model = current_session.get("selected_model", "moonshotai/kimi-vl-a3b-thinking:free")
                result = upload_pdf([uploaded_file], selected_model)
                if result:
                    current_session["session_id"] = result.get("session_id")
                    summary = result.get("summary")
                    current_session["chat_history"] = []  # Restablecer el historial de chat
                    current_session["chat_history"].append(("SciBot", summary))  # Muestra el resumen en el chat
                    current_session["has_document"] = True
                    st.success("¡Documento procesado!")
                    st.rerun()
        
        # Botón para eliminar el chat (mantiene al menos una sesión de chat)
        if len(st.session_state.sessions) > 1 and session_key != "default":
            if st.button("🗑️ Eliminar Chat", key=f"delete_{session_key}", type="secondary"):
                # Elimina la sesión
                del st.session_state.sessions[session_key]
                # Cambia a la primera sesión disponible
                remaining_sessions = list(st.session_state.sessions.keys())
                st.session_state.active_session = remaining_sessions[0]
                st.rerun()

    with col2:
        # Encabezado y selector de modelo
        col_header, col_model = st.columns([2, 1])
        
        with col_header:
            st.header("💬 Chat con el documento")
        
        with col_model:
            # Menú desplegable de selección de modelo
            model_options = {
                "LLama-3.3": "meta-llama/llama-3.3-70b-instruct:free",
                "Mistral": "mistralai/mistral-nemo:free",
                "Kimi VL": "moonshotai/kimi-vl-a3b-thinking:free",
                "MT5 Small": "mt5-small",
            }
            
            # Obtiene la selección de modelo actual
            current_model_key = "Kimi VL"  # Por defecto
            for key, value in model_options.items():
                if value == current_session.get("selected_model", "moonshotai/kimi-vl-a3b-thinking:free"):
                    current_model_key = key
                    break
            
            selected_model_key = st.selectbox(
                "Modelo Elegido:",
                options=list(model_options.keys()),
                index=list(model_options.keys()).index(current_model_key),
                key=f"model_selector_{session_key}"
            )
            
            # Actualiza el modelo si la selección cambia
            selected_model_value = model_options[selected_model_key]
            if current_session.get("selected_model") != selected_model_value:
                current_session["selected_model"] = selected_model_value
        
        # Muestra el historial de chat
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

        # Formulario de entrada de pregunta
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
                        selected_model = current_session.get("selected_model", "moonshotai/kimi-vl-a3b-thinking:free")
                        response = ask_question(current_session["session_id"], question, selected_model)
                        if response and "answer" in response:
                            current_session["chat_history"].append(("Tú", question))
                            current_session["chat_history"].append(("SciBot", response["answer"]))
                            st.rerun()
                elif ask_button and not question.strip():
                    st.warning("Por favor, escribe una pregunta antes de enviar.")

if __name__ == "__main__":
    main()