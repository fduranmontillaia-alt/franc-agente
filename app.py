import streamlit as st
import psycopg2
from groq import Groq
from gtts import gTTS
import os

# Configuración del título en la página web
st.title("Franc - Agente de Ventas por Voz")
st.write("Bienvenido al sistema de inventario en la nube de Franc.")

# --- NUEVA FUNCIÓN PARA LIMPIAR LA PANTALLA ---
# Esta función borra el texto guardado cuando el usuario decide escribir algo nuevo
def limpiar_pregunta_anterior():
    if "pregunta_guardada" in st.session_state:
        # Si lo que está en la barra de texto es diferente a lo que guardamos,
        # significa que el usuario borró o está escribiendo algo nuevo, así que limpiamos el audio anterior.
        if st.session_state.barra_texto != st.session_state.pregunta_guardada:
            st.session_state.mostrar_respuesta = False

# Inicializamos las variables de memoria la primera vez que carga la página
if "mostrar_respuesta" not in st.session_state:
    st.session_state.mostrar_respuesta = False
if "pregunta_guardada" not in st.session_state:
    st.session_state.pregunta_guardada = ""

# Conexión segura a la Base de Datos de Neon
def conectar_db():
    try:
        conn = psycopg2.connect(st.secrets["DATABASE_URL"])
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos cloud: {e}")
        return None

# Conexión segura al Cerebro (Groq Cloud)
def consultar_groq(prompt_usuario):
    try:
        client = Groq(api_key=st.secrets["GROQ_API_KEY"])
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "Eres Franc, un agente de ventas amable y conciso. Responde corto."},
                {"role": "user", "content": prompt_usuario}
            ]
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"Error en el cerebro de IA: {e}"

# --- BARRA DE ENTRADA MODIFICADA ---
# Agregamos 'key' para controlar el texto y 'on_change' para activar la limpieza automática
pregunta = st.text_input(
    "Escribe tu pregunta para Franc (ej: ¿Qué pantalones tienes?):",
    key="barra_texto",
    on_change=limpiar_pregunta_anterior
)

# Cuando el usuario presiona ENTER
if pregunta:
    # Si es una pregunta nueva que no hemos procesado, ejecutamos todo el circuito
    if st.session_state.pregunta_guardada != pregunta:
        conn = conectar_db()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT prenda, precio FROM public.inventario_prendas LIMIT 3;")
            prendas = cursor.fetchall()
            cursor.close()
            conn.close()
            
            texto_prendas = ", ".join([f"{p[0]} a {p[1]} pesos" for p in prendas])
            contexto_completo = f"El usuario pregunta: '{pregunta}'. En el inventario cloud hay: {texto_prendas}. Responde al usuario."
            
            # Guardamos la respuesta y activamos la vista
            st.session_state.respuesta_ia = consultar_groq(contexto_completo)
            st.session_state.pregunta_guardada = pregunta
            st.session_state.mostrar_respuesta = True
            
            # Convertir la respuesta a Voz (Audio)
            tts = gTTS(text=st.session_state.respuesta_ia, lang='es', tld='com.mx')
            tts.save("respuesta.mp3")

# Solo si la memoria dice que debemos mostrar la respuesta, la pintamos en pantalla
if st.session_state.mostrar_respuesta:
    st.subheader("Franc dice:")
    st.write(st.session_state.respuesta_ia)
    # Autoplay activo para que suene solo
    st.audio("respuesta.mp3", format="audio/mp3", autoplay=True)