import os
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import pickle
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv
import json
import io

# Cargar variables de entorno
load_dotenv()

# Configuración de OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Configuración de Google
SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets.readonly',
    'https://www.googleapis.com/auth/drive.file'
]
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
DRIVE_FOLDER_ID = os.getenv('DRIVE_FOLDER_ID')
RANGE_NAME = 'A2:C'  # Asumiendo que A1:C1 son los encabezados

def obtener_credenciales():
    """Obtiene o refresca las credenciales de Google."""
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return creds

def leer_datos_spreadsheet():
    """Lee los datos de la hoja de cálculo de Google."""
    try:
        creds = obtener_credenciales()
        service = build('sheets', 'v4', credentials=creds)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=SPREADSHEET_ID,
                                  range=RANGE_NAME).execute()
        valores = result.get('values', [])
        return valores
    except Exception as e:
        print(f"Error al leer la hoja de cálculo: {str(e)}")
        return []

def generar_articulo(tema, publico):
    """Genera un artículo usando OpenAI."""
    try:
        prompt = f"""Escribe un artículo detallado sobre {tema} para {publico}.
        
        Instrucciones de formato:
        - No uses formato markdown
        - No uses símbolos especiales como #, *, - para formateo
        - Usa párrafos separados por líneas en blanco
        - Para los títulos, simplemente escríbelos en una línea separada
        - El artículo debe tener:
          1. Un título principal
          2. Una introducción
          3. Desarrollo del contenido con subtítulos descriptivos
          4. Una conclusión
        
        El artículo debe ser informativo, bien estructurado y con un tono apropiado para la audiencia."""

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Eres un escritor experto que genera artículos en formato de documento Word, sin usar markdown ni caracteres especiales de formateo."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content
    except Exception as e:
        print(f"Error al generar el artículo: {str(e)}")
        return None

def guardar_articulo_drive(dia, tema, contenido):
    """Guarda el artículo como un documento de Google Docs."""
    try:
        creds = obtener_credenciales()
        service = build('drive', 'v3', credentials=creds)
        
        # Limpiar el tema para usarlo como nombre de archivo
        tema_limpio = "".join(c for c in tema if c.isalnum() or c in (' ', '-')).rstrip()
        nombre_archivo = f"{dia} - {tema_limpio}"
        
        # Crear el archivo como Google Doc
        file_metadata = {
            'name': nombre_archivo,
            'parents': [DRIVE_FOLDER_ID],
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        # Convertir el contenido a un objeto tipo archivo
        contenido_bytes = io.BytesIO(contenido.encode('utf-8'))
        media = MediaIoBaseUpload(contenido_bytes, 
                                mimetype='text/plain',
                                resumable=True)
        
        # Subir el archivo a Google Drive como Google Doc
        file = service.files().create(body=file_metadata,
                                    media_body=media,
                                    fields='id, webViewLink').execute()
        
        print(f"Artículo guardado en Drive como documento: {nombre_archivo}")
        print(f"Link para editar el documento: {file.get('webViewLink')}")
        return file.get('id')
    except Exception as e:
        print(f"Error al guardar el artículo en Drive: {str(e)}")
        return None

def main():
    print("Iniciando generador de artículos...")
    
    # Verificar que tenemos el ID de la carpeta de Drive
    if not DRIVE_FOLDER_ID:
        print("Error: No se ha especificado el ID de la carpeta de Drive en el archivo .env")
        return
    
    # Leer datos de la hoja de cálculo
    datos = leer_datos_spreadsheet()
    
    if not datos:
        print("No se encontraron datos para procesar.")
        return
    
    for fila in datos:
        if len(fila) >= 3:
            dia = fila[0]
            tema = fila[1]
            publico = fila[2]
            
            print(f"\nProcesando artículo para el día {dia}")
            print(f"Tema: {tema}")
            print(f"Público: {publico}")
            
            # Generar el artículo
            articulo = generar_articulo(tema, publico)
            
            if articulo:
                # Guardar el artículo en Drive
                archivo_id = guardar_articulo_drive(dia, tema, articulo)
                if archivo_id:
                    print(f"Artículo guardado exitosamente con ID: {archivo_id}")
            else:
                print(f"No se pudo generar el artículo para {tema}")

if __name__ == '__main__':
    main()
