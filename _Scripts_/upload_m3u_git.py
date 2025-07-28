import os
import sys
import asyncio
import requests
from github import Github
from telegram import Bot
import urllib3

# Configuration
GITHUB_TOKEN = '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'
REPO_FULL_NAME = 'Darkbcn/_Code_'        # Formato: usuario/repositorio
FILE_PATH = 'm3u/it.m3u'                 # Ruta del archivo en el repositorio
M3U_URL = 'https://gtking.x10.mx/kongtking/kongtking.m3u'  # La URL puede ser una de las dos mencionadas
TELEGRAM_BOT_TOKEN = '7944188065:AAGxwKsIxGttsC7MasUoPSwAN50DJfYT49c'  # Token del bot de Telegram
TELEGRAM_CHAT_ID = '1151753241'  # ID del chat donde se enviará el mensaje


# === Desactivar advertencias de SSL si decides ignorar certificados ===
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


def download_m3u(url: str) -> str:
    """Descarga el contenido del archivo M3U desde la URL dada."""
    try:
        # ⚠️ Puedes poner verify=True si el SSL es válido
        response = requests.get(url, verify=False)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        print(f"Error al descargar el M3U: {e}")
        return None


def update_github_file(content: str) -> bool:
    """Actualiza el archivo M3U en el repositorio de GitHub."""
    try:
        github = Github(GITHUB_TOKEN)
        repo = github.get_repo(REPO_FULL_NAME)

        file_contents = repo.get_contents(FILE_PATH)
        repo.update_file(file_contents.path, "Update M3U file", content, file_contents.sha)
        print("✅ El fichero M3U ha sido actualizado correctamente en GitHub.")
        return True
    except Exception as e:
        print(f"❌ Error al actualizar el archivo en GitHub: {e}")
        return False


async def send_to_telegram(message: str, file_path: str = None):
    """Envía un mensaje (y opcionalmente un archivo) a Telegram."""
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    try:
        if file_path and os.path.exists(file_path):
            with open(file_path, 'rb') as file:
                await bot.send_document(chat_id=TELEGRAM_CHAT_ID, document=file, caption=message)
        else:
            await bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
        print("📨 Mensaje enviado a Telegram.")
    except Exception as e:
        print(f"❌ Error al enviar mensaje a Telegram: {e}")


async def main():
    print("⬇️ Descargando M3U...")
    m3u_content = download_m3u(M3U_URL)

    if not m3u_content:
        await send_to_telegram("❌ Error al descargar el archivo M3U.")
        sys.exit(1)

    temp_file_path = "downloaded_file.m3u"
    with open(temp_file_path, "w", encoding="utf-8") as f:
        f.write(m3u_content)

    print("📤 Actualizando GitHub...")
    if update_github_file(m3u_content):
        await send_to_telegram("✅ El archivo M3U fue actualizado en GitHub correctamente.", temp_file_path)
    else:
        await send_to_telegram("❌ Error al actualizar el archivo M3U en GitHub.", temp_file_path)

    os.remove(temp_file_path)
    print("🧹 Archivo temporal eliminado.")


if __name__ == "__main__":
    asyncio.run(main())
