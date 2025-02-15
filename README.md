# Generador Automático de Artículos

Esta aplicación Python genera automáticamente artículos basados en datos obtenidos de una hoja de cálculo de Google Sheets, utilizando OpenAI para la generación de contenido y guardando los resultados como documentos de Google Docs.

## Requisitos Previos

1. Python 3.7 o superior
2. Una cuenta de Google con Google Sheets y Google Drive habilitados
3. Una cuenta de OpenAI con API key

## Configuración

1. Instalar las dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar las credenciales de Google:
   - Crear un proyecto en Google Cloud Console
   - Habilitar las APIs de Google Sheets y Google Drive
   - Descargar el archivo de credenciales como `credentials.json` y colocarlo en el directorio del proyecto
   - Obtener una API key de OpenAI

3. Configurar el archivo `.env`:
   - Añadir tu API key de OpenAI
   - Añadir el ID de tu hoja de cálculo de Google
   - Añadir el ID de la carpeta de Google Drive donde se guardarán los artículos

4. Preparar la hoja de cálculo:
   - Columna A: Día
   - Columna B: Tema
   - Columna C: Público Objetivo

## Obtener el ID de la Carpeta de Google Drive

1. Crear una carpeta en Google Drive donde se guardarán los artículos
2. Abrir la carpeta en el navegador
3. El ID de la carpeta es la parte de la URL después de "folders/":
   ```
   https://drive.google.com/drive/folders/ESTE-ES-EL-ID-DE-LA-CARPETA
   ```
4. Copiar este ID y agregarlo en el archivo `.env` como `DRIVE_FOLDER_ID`

## Uso

1. Asegúrate de que tu hoja de cálculo tenga los datos necesarios
2. Ejecuta el script:
```bash
python generador_articulos.py
```

Los artículos generados se guardarán en la carpeta especificada de Google Drive como documentos de Google Docs con el formato: "día - tema"

## Estructura de la Hoja de Cálculo

La hoja debe tener la siguiente estructura:
| Día | Tema | Público |
|-----|------|---------|
| 2025-02-14 | Marketing Digital | Emprendedores |
| 2025-02-15 | Desarrollo Web | Estudiantes |

## Notas
- Los artículos se generan automáticamente usando GPT-3.5-turbo
- Cada artículo se guarda como un documento de Google Docs
- El script proporcionará el enlace de edición para cada documento creado
- Los documentos se nombran automáticamente basándose en la fecha y el tema
