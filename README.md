# SciBot: Generación Automática de Resúmenes Científicos con Modelos NLP

Este proyecto es una aplicación web que permite a los usuarios chatear con documentos PDF. La aplicación utiliza modelos de procesamiento de lenguaje natural (NLP) para generar resúmenes y responder preguntas sobre el contenido de los documentos.

## Arquitectura

El proyecto se compone de dos partes principales:

*   **Frontend**: Una aplicación web creada con Streamlit que proporciona la interfaz de usuario.
*   **Backend**: Un servicio backend que se encarga de procesar los documentos PDF y de interactuar con los modelos de NLP.

El código de este repositorio corresponde únicamente al frontend de la aplicación. El backend es un servicio aparte desplegado en Google Cloud Run.

## Cómo ejecutar el frontend

Para ejecutar el frontend en su entorno local, siga estos pasos:

1.  **Clonar el repositorio:**

    ```bash
    git clone https://github.com/taller-de-integracion-g9/sci-bot.git
    cd sci-bot
    ```

2.  **Crear un entorno virtual:**

    ```bash
    python -m venv venv
    source venv/bin/activate  # En Windows, use `venv\Scripts\activate`
    ```

3.  **Instalar las dependencias:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Ejecutar la aplicación:**

    ```bash
    streamlit run app.py
    ```

La aplicación estará disponible en `http://localhost:8501`.

## Documentación de la API del Backend

El frontend se comunica con un backend desplegado en `https://scibot-backend.uc.r.appspot.com`. A continuación se detallan los endpoints de la API, inferidos a partir del código del frontend.

### Cargar un PDF

*   **Endpoint**: `/load`
*   **Método**: `POST`
*   **Descripción**: Sube un archivo PDF para su procesamiento. El backend extrae el texto del PDF y lo prepara para el chat.
*   **Query Parameters**:
    *   `model` (opcional): El nombre del modelo a utilizar.
*   **Request Body**:
    *   `pdf`: El archivo PDF a procesar (multipart/form-data).
*   **Respuesta Exitosa (200 OK)**:
    ```json
    {
      "session_id": "una-cadena-aleatoria",
      "summary": "Un resumen del documento."
    }
    ```
*   **Respuesta de Error**:
    *   `400 Bad Request`: Error en la solicitud.
    *   `413 Request Entity Too Large`: El documento es demasiado grande.
    *   `429 Too Many Requests`: Demasiadas solicitudes.
    *   `500 Internal Server Error`: Error interno del servidor.

### Chatear con un documento

*   **Endpoint**: `/chat`
*   **Método**: `POST`
*   **Descripción**: Envía una pregunta sobre un documento previamente cargado.
*   **Query Parameters**:
    *   `session_id`: El ID de la sesión devuelto por el endpoint `/load`.
    *   `model` (opcional): El nombre del modelo a utilizar.
*   **Request Body**:
    ```json
    {
      "message": "Tu pregunta sobre el documento."
    }
    ```
*   **Respuesta Exitosa (200 OK)**:
    ```json
    {
      "answer": "La respuesta a tu pregunta."
    }
    ```
*   **Respuesta de Error**:
    *   `400 Bad Request`: Error en la solicitud.
    *   `429 Too Many Requests`: Demasiadas solicitudes.
    *   `500 Internal Server Error`: Error interno del servidor.

### Modelos Disponibles

El frontend permite seleccionar entre los siguientes modelos:

*   **LLama-3.3**: `meta-llama/llama-3.3-70b-instruct:free`
*   **Mistral**: `mistralai/mistral-nemo:free`
*   **DeepSeek R1**: `deepseek/deepseek-r1-0528:free`
*   **Qwen**: `qwen/qwq-32b:free`
