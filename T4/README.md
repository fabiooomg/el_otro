# 🎉 DCCasino: La Experiencia del Apostador de Agua

Bienvenido al **DCCasino**, una aplicación gráfica e interactiva implementada con arquitectura cliente-servidor para simular un casino en línea. El objetivo final es ganar dinero para recuperar el agua de los Gremen.

---

## 🚀 Cómo Ejecutar la Tarea

La tarea será ejecutada **únicamente desde la terminal del computador**.

El cliente y el servidor son entidades independientes y se encuentran en directorios distintos (`cliente/` y `servidor/`).

### 1. Requisitos Previos

Asegúrate de tener instalado **Python 3.12.9**.

### 2. Archivos de Conexión

Verifica que el archivo `cliente/backend/conexion.json` y el archivo `servidor/conexion.json` contengan la información correcta para `host`, `puerto` y `puertoAPI`.

### 3. Secuencia de Ejecución

Debes iniciar el servidor antes que el cliente.

1.  **Ejecutar el Servidor:**
    ```bash
    python servidor/main.py
    ```
    El servidor levantará la conexión TCP/IP y la API de WebServices (usando *Threading*). También gestionará la base de datos (`usuarios.csv` y `ganancias.csv`) en `servidor/database`.

2.  **Ejecutar el Cliente:**
    Abre una **nueva terminal** y ejecuta el cliente:
    ```bash
    python cliente/main.py
    ```
    El cliente se conectará al servidor e iniciará con la **Ventana de Inicio**.

---

## ✨ Alcances del Programa

La tarea implementa una arquitectura robusta y todas las funcionalidades de los tres juegos requeridos.

### 🏛️ Arquitectura y Comunicación

| Característica | Detalle de Implementación |
| :--- | :--- |
| **Arquitectura** | Cliente-Servidor con separación de directorios (`cliente/`, `servidor/`). |
| **Networking** | Sockets con protocolo **TCP/IP**. |
| **Codificación/Encriptación** | Toda comunicación es serializada, dividida en **chunks** de 124 bytes, numerada con 4 bytes (**big endian**), y **encriptada con XOR** usando `CLAVE_CASINO`. El largo del contenido original se antepone con 4