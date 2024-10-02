import streamlit as st
from audio_recorder_streamlit import audio_recorder
import os
from openai import OpenAI

OPENAI_API_KEY = st.secrets['API_KEY']

# API key para OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

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
    completion = client.chat.completions.create(
    model="ft:gpt-4o-mini-2024-07-18:tae::AB12SPoT",
    messages=[
        {"role": "system", "content": "Eres un asistente de ventas especializado en vinos. Tu función es recomendar únicamente los siguientes vinos: Cava Segura Viudas Reserva Heredad Brut, Vino Blanco Zuccardi Serie A Torrontes, Vino Tinto Casta Cirio, Vino Tinto Chateau St. Jean Merlot, Vino Tinto José Zuccardi Malbec, Vino Tinto Le Dix de los Vasco, Vino Tinto Queulat Gran Reserva Carmenere, Vino Tinto Tributo Palafox Tempranillo Cabernet, Vino Tinto Zuccardi Emma Bonarda, Vino Tinto Zuccardi Q Malbec, Vino Tinto Carmelo Rodero Crianza, Vino Tinto Carmelo Rodero Reserva, Vino Tinto Dominio de Tares Cepas Viejas, Vino Tinto Dominio de Tares Bembibre, Vino Tinto Carmelo Rodero Roble 9 meses, Vino Tinto Stags Leap Cabernet Sauvignon, Vino Tinto Brolio Chianti Classico, Vino Tinto Casalferro Barone Ricasoli, Vino Tinto Oddero Barolo, Vino Tinto Barone Ricasoli Castello Di Brolio, Vino Blanco Chablis Moreau, Vino Tinto Emevé Cabernet Sauvignon, Vino Tinto Emevé Shiraz, Vino Tinto Norton Malbec Reserva, Vino Tinto Catena Malbec, Vino Tinto Norton Privada, Vino Tinto Château Chasses Spleen, Vino Blanco Stags Leap Chardonnay, Vino Tinto El Coto De Imaz Reserva, Vino Tinto Gran Ricardo, Vino Tinto Marqués De Cáceres Crianza, Vino Tinto Marqués De Cáceres Reserva, Vino Tinto Marqués De Cáceres Gaudium Reserva, Vino Tinto Mauro Cosecha, Vino Tinto Prima, Vino Tinto Resalte Origen, Vino Tinto Mongrana IGT, Vino Blanco Paco Y Lola Albariño, Vino Tinto Nebbiolo Langhe Pio Cesare, Vino Tinto Pago de los Capellanes Crianza, Vino Tinto Tres Picos de Borsao, Vino Tinto San Román, Espumoso Segura Viudas Brut Reserva, Vino Tinto Ventisquero Vertice."}, {"role": "user", "content": "Hoy voy a comer un ribeye a la parrilla, ¿qué vino me recomiendas?"}, {"role": "assistant", "content": "Para un ribeye a la parrilla, te recomiendo los siguientes vinos: Carmelo Rodero Crianza, Stags Leap Cabernet Sauvignon, José Zuccardi Malbec, Gran Ricardo, Norton Privada. (Si la pregunta no es sobre comida o vino, simplemente di que tu función es recomendar vinos)."},
        {"role": "user", "content": question}
    ])
    return completion.choices[0].message.content

def main():

    st.title("Asistente de Vinos")

    # Usar Módulo de streamlit Audio Recorder
    audio_bytes = audio_recorder()
    if audio_bytes:

        path = 'myfile.wav'
        
        # Escribe el archivo de audio
        with open(path, 'wb') as f:
            f.write(audio_bytes)
        
        try:
            # Transcribe el audio
            with st.spinner("Transcribiendo el audio..."):
                question = audio_to_text(path)
                st.write(f"Pregunta hecha: {question}")
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
        # st.write(f"Respuesta de la IA: {response}")
        
        # Convierte el texto a audio
        with st.spinner("Convirtiendo la respuesta a audio..."):
            audio_file = text_to_audio(response)

        # Reproduce el audio generado en la parte superior (justo después de la transcripción)
        st.audio(audio_file)

        # Limpia archivos temporales
        os.remove(audio_file)

if __name__ == "__main__":
    main()
