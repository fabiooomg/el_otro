# 📖 Manual de Usuario - DCCasino

Este manual te guiará paso a paso para utilizar la aplicación DCCasino, desde el registro hasta cómo jugar los diferentes juegos.

---

## 1. Inicio de Sesión y Registro

Al abrir el cliente (`python cliente/main.py`), verás la ventana de **Ingreso**.

### **Registrarse (Nuevo Usuario)**
Si es tu primera vez, debes crear una cuenta.
1. Ingresa un nombre de usuario en el campo **Usuario**.
2. Ingresa una contraseña en el campo **Clave**.
3. Haz clic en el botón **Registrar**.
   - Si el registro es exitoso, recibirás un saldo inicial de **$5,000**.
   - El sistema te avisará y podrás proceder a iniciar sesión.

### **Iniciar Sesión**
1. Ingresa tu **Usuario** y **Clave**.
2. Haz clic en **Iniciar Sesión**.
3. Si los datos son correctos, accederás al **Menú Principal**.

---

## 2. Menú Principal (Lobby)

En esta pantalla verás:
- **Tu Nombre** y **Saldo Actual**.
- **Historial de Ganancias:** Una tabla con los últimos resultados globales del servidor.
- **Botones de Juego:**
  - `Blackjack`
  - `Aviator`
  - `Ruleta` (No disponible en esta versión)
- **Cargar Dinero:** Opción para añadir fondos (si está habilitada).

Para entrar a un juego, simplemente haz clic en el botón correspondiente (ej. **Aviator** o **Blackjack**).

---

## 3. Cómo Jugar: Aviator ✈️

El objetivo es retirar tu apuesta antes de que el avión se estrelle ("Crash").

1. **Ingresar a la Sala:** Al entrar, verás el multiplicador en grande (ej. `1.00x`) y el estado de la ronda.
2. **Apostar:**
   - Espera a que el estado diga **"Periodo de Apuestas"**.
   - Escribe el monto en la casilla inferior.
   - Haz clic en **Apostar**.
3. **El Vuelo:**
   - Cuando inicie la ronda, el multiplicador empezará a subir.
   - Tu ganancia potencial aumenta con el multiplicador.
4. **Retirarse:**
   - Haz clic en el botón **Retirar** antes de que ocurra el **CRASH**.
   - Si te retiras a tiempo, ganas: `Apuesta x Multiplicador`.
   - Si ocurre el Crash antes de retirarte, pierdes tu apuesta.

---

## 4. Cómo Jugar: Blackjack ♠️

El objetivo es sumar **21** o acercarse más que el Dealer sin pasarse.

1. **Apostar:**
   - Al entrar, escribe tu monto de apuesta.
   - Haz clic en **Apostar**.
   - Se te repartirán 2 cartas (y 2 al Dealer, una oculta).
2. **Tu Turno:**
   - **Pedir Carta:** Si quieres subir tu puntaje. Ten cuidado de no pasar de 21.
   - **Plantarse:** Si estás satisfecho con tu mano. El turno pasará al Dealer.
3. **Resolución:**
   - El Dealer revelará su carta y jugará según las reglas (pide hasta 17).
   - Si el Dealer se pasa (Bust), ganas.
   - Si tienes más que el Dealer (sin pasarte), ganas.
   - El pago es 2:1 (recuperas apuesta + ganancia igual a la apuesta).

---

## 5. Salir del Juego

En cualquier juego, puedes presionar el botón **"Volver a V. Principal"** para regresar al lobby y elegir otro juego o revisar tu saldo actualizado.
