import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
from openai import OpenAI

OPENAI_API_KEY = st.secrets['API_KEY']

# API key para OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

import base64

# Función para convertir el archivo de audio a base64
def get_audio_base64(audio_file):
    with open(audio_file, "rb") as f:
        audio_bytes = f.read()
    return base64.b64encode(audio_bytes).decode()

# voice to text for questions
def audio_to_text(path):
    '''
    Transcribe audio de un archivo mp3

    INPUTS:
    path -- str - path al archivo de audio

    OUTPUTS:
    transcription.text -- str - texto transcrito del audio
    '''
    with open(path, "rb") as audio_file:
        transcription = client.audio.transcriptions.create(
            model="whisper-1", 
            file=audio_file
        )
    return transcription.text


# Text to voice for responses
def text_to_audio(text):
    '''
    Crea archivo de audio a partir de un texto

    INPUTS:
    text -- str - texto que se quiere convertir en audio

    OUTPUTS:
    none
    '''
    response = client.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text,
    )
    audio_file = "output.mp3"
    response.stream_to_file(audio_file)
    return audio_file

# handle questions
def handle_question(question):
    '''
    Responde usando IA a una pregunta

    INPUTS:
    question -- str - texto de pregunta a hacerse

    OUTPUTS:
    str - texto de respuesta de la IA
    '''

    initial_prompt = "Act\u00faa como un sommelier experto en vinos, especializado en ofrecer recomendaciones personalizadas y detalladas basadas en las preferencias del usuario, el tipo de comida que van a preparar, y las caracter\u00edsticas de diferentes vinos. Tu conocimiento incluye informaci\u00f3n sobre regiones vin\u00edcolas, tipos de uvas, notas de cata, maridajes recomendados y caracter\u00edsticas espec\u00edficas de cada vino. Responde de manera clara, profesional y \u00fatil, adaptando el nivel de detalle a las preguntas del usuario, y evita responder cosas que no est\u00e1n relacionadas a tu rol de sommelier. Los vinos en el inventario son: Cava Segura Viudas Reserva Heredad Brut, Vino Blanco Zuccardi Serie A Torrontes, Vino Tinto Casta Cirio, Vino Tinto Chateau St. Jean Merlot, Vino Tinto Jos\u00e9 Zuccardi Malbec, Vino Tinto Le Dix de los Vasco, Vino Tinto Queulat Gran Reserva Carmenere, Vino Tinto Tributo Palafox Tempranillo Cabernet, Vino Tinto Zuccardi Emma Bonarda, Vino Tinto Zuccardi Q Malbec, Vino Tinto Carmelo Rodero Crianza, Vino Tinto Carmelo Rodero Reserva, Vino Tinto Dominio de Tares Cepas Viejas, Vino Tinto Dominio de Tares Bembibre, Vino Tinto Carmelo Rodero Roble 9 meses, Vino Tinto Stags Leap Cabernet Sauvignon, Vino Tinto Brolio Chianti Classico, Vino Tinto Casalferro Barone Ricasoli, Vino Tinto Oddero Barolo, Vino Tinto Barone Ricasoli Castello Di Brolio, Vino Blanco Chablis Moreau, Vino Tinto Emev\u00e9 Cabernet Sauvignon, Vino Tinto Emev\u00e9 Shiraz, Vino Tinto Norton Malbec Reserva, Vino Tinto Catena Malbec, Vino Tinto Norton Privada, Vino Tinto Ch\u00e2teau Chasses Spleen, Vino Blanco Stags Leap Chardonnay, Vino Tinto El Coto De Imaz Reserva, Vino Tinto Gran Ricardo, Vino Tinto Marqu\u00e9s De C\u00e1ceres Crianza, Vino Tinto Marqu\u00e9s De C\u00e1ceres Reserva, Vino Tinto Marqu\u00e9s De C\u00e1ceres Gaudium Reserva, Vino Tinto Mauro Cosecha, Vino Tinto Prima, Vino Tinto Resalte Origen, Vino Tinto Mongrana IGT, Vino Blanco Paco Y Lola Albari\u00f1o, Vino Tinto Nebbiolo Langhe Pio Cesare, Vino Tinto Pago de los Capellanes Crianza, Vino Tinto Tres Picos de Borsao, Vino Tinto San Rom\u00e1n, Espumoso Segura Viudas Brut Reserva, Vino Tinto Ventisquero Vertice."

    # Construir historial de mensajes
    messages_for_api = [{"role": "system", "content": initial_prompt}] + [{"role": msg['role'], "content": msg['content']} for msg in st.session_state.messages]

    completion = client.chat.completions.create(
        model="ft:gpt-4o-mini-2024-07-18:tae::AFlqsMGP",
        messages=messages_for_api
    )

    return completion.choices[0].message.content

def main():

    bg='''
    <style>
    [data-testid="stAppViewContainer"]{
    background-image: url("https://img.freepik.com/premium-photo/wine-wooden-table-background-blurred-wine-shop-with-bottles_191555-1126.jpg?w=1060");
    background-size: cover;
    }
    [data-testid="stMainBlockContainer"]{
    background-color: rgba(0,0,0,.5);
    } 
    [data-testid="stHeader"]{
    background-color: rgba(0,0,0,0);
    }
    [data-testid="stMarkdown"]{
    color: rgb(255,255,255);
    }
    </style>
    '''

    st.markdown(bg, unsafe_allow_html = True)

    st.title("Asistente de Vinos")

    # Inicializar el estado de la sesión para almacenar los mensajes si no existe
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Usar Módulo de streamlit Audio Recorder
    audio_bytes = audio_recorder(text="Haz click para comenzar a hablar!",
                                 recording_color="#ff0000",
                                 neutral_color="#d3d3d3")
    if audio_bytes:

        path = 'myfile.wav'
        
        # Escribe el archivo de audio
        with open(path, 'wb') as f:
            f.write(audio_bytes)
        
        try:
            # Transcribe el audio
            with st.spinner("Transcribiendo el audio..."):
                question = audio_to_text(path)
                # st.write(f"Pregunta hecha: {question}")
                st.session_state.messages.append({"role": "user", "content": question})  # Agregar el mensaje del usuario al historial
        finally:
            # Cierra el archivo y lo elimina de forma segura
            if os.path.exists(path):
                try:
                    os.remove(path)
                except PermissionError:
                    st.error(f"No se pudo eliminar {path} porque está en uso.")

        # Maneja la pregunta con IA
        with st.spinner("Consultando la IA..."):
            response = handle_question(question)
            st.session_state.messages.append({"role": "assistant", "content": response})  # Agregar la respuesta de la IA al historial

            # Convierte la respuesta a audio y lo reproduce automáticamente
            with st.spinner("Convirtiendo la respuesta a audio..."):
                audio_file = text_to_audio(response)

            # Convierte el audio a base64
            audio_base64 = get_audio_base64(audio_file)

            # Crea la etiqueta HTML para reproducir el audio automáticamente
            audio_html = f"""
                <audio autoplay>
                    <source src="data:audio/mpeg;base64,{audio_base64}" type="audio/mp3">
                </audio>
            """

            # Muestra el audio usando HTML y lo reproduce automáticamente
            st.markdown(audio_html, unsafe_allow_html=True)

            # Elimina el archivo temporal de audio
            if os.path.exists(audio_file):
                os.remove(audio_file)

if __name__ == "__main__":
    main()
