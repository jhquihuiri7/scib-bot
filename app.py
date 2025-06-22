import streamlit as st
import requests
import uuid

PROD_URL = "https://scibot-backend.uc.r.appspot.com"

def upload_pdf(files):
    file = files[0]
    files_payload = {"pdf": (file.name, file, "application/pdf")}
    response = requests.post(f"{PROD_URL}/load", files=files_payload)
    if response.status_code == 200:
        return response.json()  # {"session_id": ..., "summary": ...}
    else:
        st.error(f"Upload error: {response.text}")
        return None

def ask_question(session_id, question):
    headers = {"Content-Type": "application/json"}
    json_data = {"message": question}
    response = requests.post(f"{PROD_URL}/chat?session_id={session_id}", headers=headers, json=json_data)
    if response.status_code == 200:
        return response.json()  # {"answer": "..."}
    else:
        st.error(f"Chat error: {response.text}")
        return None

def create_new_session(session_number):
    """Create a new session with a numbered display name"""
    return {
        "session_id": None,  # Will be set when PDF is uploaded
        "chat_history": [],
        "display_name": f"Chat {session_number}",
        "has_document": False
    }

def show_welcome_page():
    """Display the welcome page with project information"""
    st.set_page_config(page_title="Generación Automática de Resúmenes Científicos", page_icon="📊", layout="wide")
    
    # Center the content
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
        
        # Center the button
        col_btn1, col_btn2, col_btn3 = st.columns([1, 1, 1])
        with col_btn2:
            if st.button("Iniciar Programa", type="primary", use_container_width=True):
                st.session_state.show_main_app = True
                st.rerun()

def main():
    # Initialize session state
    if "show_main_app" not in st.session_state:
        st.session_state.show_main_app = False
    
    # Show welcome page or main app
    if not st.session_state.show_main_app:
        show_welcome_page()
    else:
        show_main_app()

def show_main_app():
    """Display the main PDF chat application"""
    st.set_page_config(page_title="Chat con PDFs", page_icon="📄", layout="wide")

    # Initialize session state for main app
    if "sessions" not in st.session_state:
        st.session_state.sessions = {"default": create_new_session(1)}
    if "active_session" not in st.session_state:
        st.session_state.active_session = "default"
    if "session_counter" not in st.session_state:
        st.session_state.session_counter = 1

    # Create tabs for sessions
    session_keys = list(st.session_state.sessions.keys())
    tab_labels = [st.session_state.sessions[key]["display_name"] for key in session_keys]
    tab_labels.append("+ Nuevo Chat")
    
    tabs = st.tabs(tab_labels)
    
    # Handle new chat creation button
    if len(tabs) > len(session_keys):
        with tabs[-1]:  # Last tab is "Nuevo Chat"
            if st.button("Crear Nuevo Chat", key="new_chat_btn"):
                st.session_state.session_counter += 1
                new_session_key = f"session_{st.session_state.session_counter}"
                st.session_state.sessions[new_session_key] = create_new_session(st.session_state.session_counter)
                st.session_state.active_session = new_session_key
                st.rerun()
            st.info("Haz clic en 'Crear Nuevo Chat' para iniciar una nueva sesión.")
    
    # Display content for existing session tabs
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
                result = upload_pdf([uploaded_file])
                if result:
                    current_session["session_id"] = result.get("session_id")
                    summary = result.get("summary")
                    current_session["chat_history"] = []  # Reiniciar chat
                    current_session["chat_history"].append(("SciBot", summary))  # Mostrar resumen en el chat
                    current_session["has_document"] = True
                    st.success("¡Documento procesado!")
                    st.rerun()
        
        # Delete chat button - only show if this is not the last remaining session and not the first session
        if len(st.session_state.sessions) > 1 and session_key != "default":
            if st.button("🗑️ Eliminar Chat", key=f"delete_{session_key}", type="secondary"):
                # Remove the session
                del st.session_state.sessions[session_key]
                # Switch to the first available session
                remaining_sessions = list(st.session_state.sessions.keys())
                st.session_state.active_session = remaining_sessions[0]
                st.rerun()

    with col2:
        st.header("💬 Chat con el documento")
        
        # Display chat history
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

        # Question input at the bottom
        if current_session["session_id"]:
            st.markdown("---")  # Separator line
            
            # Use form to handle Enter key submission
            with st.form(key=f"question_form_{session_key}", clear_on_submit=True):
                # Create columns for question input and button with proper alignment
                input_col, button_col = st.columns([5, 1])
                
                with input_col:
                    question = st.text_input(
                        "Pregunta sobre el documento:", 
                        key=f"question_{session_key}",
                        placeholder="Escribe tu pregunta aquí...",
                        label_visibility="visible"
                    )
                
                with button_col:
                    # Add empty space to align with the text input
                    st.markdown("")  # Empty line to match the label height
                    st.markdown("") 
                    ask_button = st.form_submit_button("Preguntar", use_container_width=True)
                
                # Handle question submission (both button and Enter key)
                if ask_button and question.strip():
                    with st.spinner("Obteniendo respuesta..."):
                        response = ask_question(current_session["session_id"], question)
                        if response and "answer" in response:
                            current_session["chat_history"].append(("Tú", question))
                            current_session["chat_history"].append(("SciBot", response["answer"]))
                            st.rerun()
                elif ask_button and not question.strip():
                    st.warning("Por favor, escribe una pregunta antes de enviar.")

if __name__ == "__main__":
    main()
