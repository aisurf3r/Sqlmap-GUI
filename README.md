# 🔮 sqlmap GUI - Interfaz Gráfica para sqlmap

Una interfaz gráfica moderna y completa para **sqlmap**, creada con **PyQt6**. Diseñada para facilitar el uso de sqlmap sin necesidad de escribir comandos manualmente.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-6.x-green)
![License](https://img.shields.io/badge/License-MIT-yellow)

## ✨ Características

- **Interfaz oscura moderna** y fácil de usar
- **Actualización en tiempo real** del comando sqlmap
- **Presets rápidos**: Stealth, Bazoka, Paranoia y Takeover
- Soporte completo para la mayoría de opciones de sqlmap:
  - Inyección (técnicas, tamper scripts, prefijos/sufijos)
  - Enumeración (bases de datos, tablas, columnas, dump, etc.)
  - Acceso a sistema operativo y archivos
  - Opciones de optimización y detección
- Guardado y carga de **perfiles personalizados**
- Visualización de resultados en tablas
- Consola integrada para ver la salida de sqlmap

## 📸 Capturas

<img width="1917" height="1078" alt="{7296E821-BE57-478D-AC97-1A4D1CF64A38}" src="https://github.com/user-attachments/assets/4cb56b86-0d9c-4dfe-90e0-fd8a8dc7344f" />
<img width="1920" height="1078" alt="{4B865315-CCB8-422D-8A67-664D9F717753}" src="https://github.com/user-attachments/assets/f5f6c910-6729-47a5-9c9c-9efa540f34a9" />



## 🚀 Requisitos

- Python 3.8 o superior
- sqlmap instalado y actualizado
- PyQt6

## 🛠️ Instalación

 **Clona el repositorio**:
   ```bash
   git clone https://github.com/tuusuario/sqlmap-gui.git
   cd sqlmap-gui
   ```
   

## 🚀 Instalación y Uso

1. **Clona o descarga** el repositorio.
2. Coloca `gui_sqlmap.py` dentro de la carpeta de **sqlmap**.
3. Instala PyQt6 (si no lo tienes):

   ```bash
   pip install PyQt6
   ```

Nota: Recomendado colocar la GUI en la misma carpeta que sqlmap.py para que funcione correctamente.

4. Ejecuta la GUI
```bash
python gui_sqlmap.py
```
🎛️ Uso
Modos Rápidos (Presets)

Stealth: Bajo nivel y riesgo, muy discreto
Bazoka: Alto nivel y riesgo, máximo rendimiento
Paranoia: Modo paranoico con ofuscación
Takeover: Orientado a takeover del sistema

Funcionalidades principales

Escribe la URL objetivo → el comando se actualiza automáticamente
Selecciona técnicas, tampers, opciones de enumeración, etc.
Usa los botones de la barra superior para acciones rápidas
Guarda tus configuraciones como perfiles

⚙️ Características avanzadas

Carga dinámica de scripts de tamper desde la carpeta /tamper
Soporte para POST data, cookies, headers, proxy, Tor, etc.
Parsing automático de tablas de resultados
Guardado y carga de perfiles en formato JSON

🛡️ Advertencia
Esta herramienta es solo para fines educativos y pruebas autorizadas.
El uso indebido de sqlmap puede ser ilegal. Úsalo solo en entornos donde tengas permiso explícito.


🤝 Contribuciones
Las contribuciones son bienvenidas. Si quieres mejorar la GUI, añadir funciones o corregir bugs, abre un Pull Request.
📄 Licencia
Este proyecto está bajo la licencia MIT.

Hecho con ❤️  por Aisurf3r para la comunidad de pentesting
