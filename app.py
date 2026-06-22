import streamlit as st
import psycopg2
from groq import Groq
from gtts import gTTS
import os

# Configuración del título en la página web
st.title("Franc - Agente de Ventas por Voz")
st.write("Bienvenido al sistema de inventario en la nube de Franc.")

# TRUCO: Creamos la memoria para limpiar la barra de texto
if "texto_pregunta" not in st.session_state:
    st.session_state["texto_pregunta"] = ""

# Función para el botón de Reset: pone la memoria en blanco
def limpiar_texto():
    st.session_state["texto_pregunta"] = ""

# 1. Conexión segura a la Base de Datos de Neon
def conectar_db():
    try:
        conn = psycopg2.connect(st.secrets["DATABASE_URL"])
        return conn
    except Exception as e:
        st.error(f"Error al conectar a la base de datos cloud: {e}")
        return None

# 2. Conexión segura al Cerebro (Groq Cloud)
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

# Interfaz en la pantalla vinculada a la memoria
pregunta = st.text_input(
    "Escribe tu pregunta para Franc (ej: ¿Qué pantalones tienes?):", 
    key="texto_pregunta"
)

# Creamos el botón "Reset" justo debajo de la barra
st.button("Reset (Nueva consulta)", on_click=limpiar_texto)

if pregunta:
    # Buscar en la base de datos cloud
    conn = conectar_db()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT prenda, precio FROM public.inventario_prendas LIMIT 3;")
        prendas = cursor.fetchall()
        cursor.close()
        conn.close()
        
        texto_prendas = ", ".join([f"{p[0]} a {p[1]} pesos" for p in prendas])
        
        contexto_completo = f"El usuario pregunta: '{pregunta}'. En el inventario cloud hay: {texto_prendas}. Responde al usuario."
        respuesta_ia = consultar_groq(contexto_completo)
        
        # Mostrar respuesta en texto
        st.subheader("Franc dice:")
        st.write(respuesta_ia)
        
        # Convertir la respuesta a Voz (Audio)
        tts = gTTS(text=respuesta_ia, lang='es', tld='com.mx')
        tts.save("respuesta.mp3")
        
        # Reproductor de audio con Autoplay Automático
        st.audio("respuesta.mp3", format="audio/mp3", autoplay=True)

# ------------------------------------------------------------------
# SECCIÓN DE CONTACTO (CORREGIDA)
# ------------------------------------------------------------------
st.markdown("---") # Línea divisoria elegante

# Definimos las variables fijas arriba para evitar errores de sintaxis en el HTML
nombre_usuario = "Francisco Duran"
url_whatsapp = "https://wa.me/584168184675"

st.markdown(
    f"""
    <div style="text-align: center; padding: 20px; background-color: #f0f2f6; border-radius: 10px; margin-top: 30px;">
        <h4 style="margin: 0; color: #31333F; font-family: sans-serif;">Desarrollado por: {nombre_usuario}</h4>
        <p style="margin: 10px 0 15px 0; color: #555; font-family: sans-serif;">¿Quieres un sistema como este para tu negocio? ¡Contáctame!</p>
        <a href="{url_whatsapp}" target="_blank" style="background-color: #25D366; color: white; padding: 12px 24px; text-decoration: none; font-weight: bold; border-radius: 8px; display: inline-block; font-family: sans-serif;">
            💬 Contactar por WhatsApp
        </a>
    </div>
    """,
    unsafe_html=True
)