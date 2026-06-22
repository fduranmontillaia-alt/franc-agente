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
# SECCIÓN DE CONTACTO (PIE DE PÁGINA TOTALMENTE CORREGIDA)
# ------------------------------------------------------------------
st.markdown("---") # Línea divisoria elegante

# Creamos columnas limpias nativas de Streamlit para evitar usar CSS conflictivo
col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    st.markdown("### Desarrollado por: **Francisco Duran**")
    st.write("¿Quieres un sistema automático como este para tu negocio? ¡Contáctame!")
    
    # Enlace directo y limpio a tu WhatsApp
    url_whatsapp = "https://wa.me/584168184675"
    st.link_button("💬 Contactar por WhatsApp", url_whatsapp, type="primary")