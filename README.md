# Buscador de Clientes Potenciales

Herramienta con interfaz web para buscar pymes en Google Maps (por tipo de negocio y ciudad) y filtrar los mejores prospectos para ofrecerles servicios de análisis de datos.

## Qué hace

- Buscas por ejemplo: "panaderías" + "Cali, Colombia".
- La herramienta abre Google Maps en segundo plano y recopila: nombre, dirección, teléfono, sitio web, reseñas, calificación, horario y tipo de negocio.
- Puedes filtrar para ver solo los negocios **sin sitio web** (suelen ser mejores prospectos, porque probablemente tampoco usan dashboards ni análisis de datos).
- Descargas la lista final en un archivo CSV para contactarlos.

## Paso a paso para instalarlo (solo se hace una vez)

### 1. Instalar Python
Necesitas Python 3.9, 3.10 o 3.11 (no uses la versión más reciente, puede dar problemas de compatibilidad).
Descárgalo de https://www.python.org/downloads/ — durante la instalación en Windows, marca la casilla **"Add Python to PATH"**.

### 2. Descomprimir esta carpeta
Guarda y descomprime la carpeta `buscador-clientes` en un lugar fácil de encontrar, por ejemplo en tu Escritorio.

### 3. Abrir una terminal dentro de la carpeta
- **Windows**: entra a la carpeta `buscador-clientes`, haz clic derecho dentro de ella (en un espacio vacío) y selecciona "Abrir en Terminal" (o "Abrir ventana de PowerShell aquí").
- **Mac**: abre la app "Terminal", escribe `cd ` (con un espacio) y arrastra la carpeta `buscador-clientes` a la ventana, luego presiona Enter.

### 4. Instalar las dependencias
Copia y pega este comando en la terminal, y presiona Enter:
```bash
pip install -r requirements.txt
```

### 5. Instalar el navegador que usa la herramienta
```bash
playwright install chromium
```

Con esto ya quedó todo instalado. Estos pasos 1 a 5 solo se hacen la primera vez.

## Cómo usarla cada vez que quieras buscar clientes

1. Abre la terminal dentro de la carpeta `buscador-clientes` (como en el paso 3).
2. Ejecuta:
   ```bash
   streamlit run app.py
   ```
3. Se abrirá automáticamente una pestaña en tu navegador con la interfaz.
4. Escribe el **tipo de negocio** (ej. "restaurantes") y la **ciudad** (ej. "Cali, Colombia").
5. Elige cuántos negocios quieres buscar (recomendado: entre 15 y 30 para que no tarde mucho).
6. Haz clic en **"Buscar"** y espera — puede tardar unos minutos, verás el avance en pantalla.
7. Cuando termine, usa los filtros (por ejemplo, "solo negocios sin sitio web") para quedarte con los mejores prospectos.
8. Haz clic en **"Descargar lista en CSV"** para guardar el archivo y empezar a contactarlos.

Para cerrar la herramienta, vuelve a la terminal y presiona `Ctrl + C`.

## Recomendaciones importantes

- **Úsala con moderación**: no busques cientos de negocios seguidos ni la dejes corriendo todo el día. Búsquedas moderadas (15-30 resultados, un par de veces al día) reducen el riesgo de que Google la bloquee temporalmente.
- **Ten en cuenta los Términos de Servicio de Google**: extraer datos de Google Maps de forma automatizada no está oficialmente permitido por Google. Esta herramienta es útil para prospección puntual a pequeña escala, pero no la conviertas en un proceso masivo o público.
- Si en algún momento deja de funcionar, es probable que Google haya cambiado el diseño de su página (pasa cada cierto tiempo) y los "XPaths" del archivo `scraper.py` necesiten actualizarse.

## Si algo falla

- **"playwright: command not found"**: repite el paso 5 (`playwright install chromium`).
- **La terminal dice que no reconoce "streamlit" o "pip"**: revisa que Python se haya instalado correctamente y que esté en el PATH (reinstala marcando esa casilla).
- **No encuentra resultados**: prueba con un término de búsqueda más específico, como "restaurantes en Cali, Colombia" en vez de solo "restaurantes".
