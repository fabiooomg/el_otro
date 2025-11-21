# 🚀 Guía Rápida para Ejecutar DCCasino

Sigue estos pasos para ejecutar el juego correctamente.

## 1. Instalar Dependencias

Asegúrate de tener Python 3 instalado y ejecuta el siguiente comando para instalar las librerías necesarias:

```bash
pip install flask requests PyQt5
```

## 2. Ejecutar el Servidor

Abre una terminal en la carpeta raíz `T4/` y ejecuta:

```bash
python3 servidor/main.py
```

Verás un mensaje indicando que el servidor y la API están escuchando.

## 3. Ejecutar el Cliente

Abre **otra** terminal en la misma carpeta raíz `T4/` y ejecuta:

```bash
python3 cliente/main.py
```

¡Listo! Debería abrirse la ventana de inicio de sesión. Puedes registrar un usuario nuevo o usar uno existente si ya hay datos en la base de datos.

---
**Nota:** Es importante ejecutar ambos comandos desde la carpeta `T4/` para que el programa encuentre correctamente las imágenes y archivos de configuración.
