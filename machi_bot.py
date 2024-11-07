import asyncio
import requests
from telethon import TelegramClient, events
from bs4 import BeautifulSoup

# Configuración del cliente de Telegram
API_ID = '20451779'
API_HASH = 'da79d8408831a094d64edb184f253bab'
PHONE_NUMBER = '+51903356436'

# Inicializar cliente de Telegram
client = TelegramClient('mi_sesion_token', API_ID, API_HASH)

# Lista de usuarios autorizados para consultar el token
USUARIOS_AUTORIZADOS = ['ABUS1VEDD', 'Asteriscom', 'ChokySupport']  # Agrega más usuarios aquí

# Lista de URLs asociadas a cada comando
URLS = {
    '/token1': 'http://161.132.49.242:1241/token/private/31742607',
    '/token2': 'http://161.132.49.242:1241/token/private/31900419'  # Agrega más comandos y URLs aquí
}

# Registro de valores enviados previamente
valores_enviados = set()

async def obtener_datos(url):
    """Extrae el usuario, contraseña y token del HTML de la URL proporcionada."""
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')

            # Extraemos los valores de cada campo
            usuario = soup.find(text="Usuario:").find_next('input')['value']
            password = soup.find(text="Contraseña:").find_next('input')['value']
            token = soup.find(text="Token:").find_next('input')['value']

            return usuario, password, token
        else:
            return None, None, None
    except Exception as e:
        print(f"Error al obtener los datos de la URL {url}: {str(e)}")
        return None, None, None

async def manejar_comando(event, url):
    """Maneja la respuesta para cualquier comando registrado en la lista URLS."""
    sender = await event.get_sender()  # Obtenemos información del remitente
    username = sender.username  # Extraemos su nombre de usuario

    if username in USUARIOS_AUTORIZADOS:
        usuario, password, token = await obtener_datos(url)

        if usuario and password and token:
            # Enviar cada valor si no se ha enviado antes
            chat_id = event.chat_id  # Obtenemos el ID del chat para enviar los mensajes

            for valor in [usuario, password, token]:
                if valor not in valores_enviados:
                    await client.send_message(chat_id, valor)
                    valores_enviados.add(valor)  # Marcar como enviado
                    await asyncio.sleep(2)  # Retraso opcional entre mensajes
        else:
            await client.send_message(event.chat_id, "❌ Error al obtener los datos del token.")
    else:
        # Si no está autorizado, enviamos un mensaje de advertencia
        await client.send_message(event.chat_id, "❌ No estás autorizado para usar este comando.")

# Registrar los comandos dinámicamente
for comando, url in URLS.items():
    @client.on(events.NewMessage(pattern=comando))
    async def evento_handler(event, url=url):  # El parámetro url se pasa como valor predeterminado
        await manejar_comando(event, url)

# Ejecutar el cliente de Telegram
async def main():
    await client.start(PHONE_NUMBER)
    print("Bot de token conectado y funcionando.")
    await client.run_until_disconnected()

# Iniciar el cliente de Telegram
with client:
    client.loop.run_until_complete(main())
