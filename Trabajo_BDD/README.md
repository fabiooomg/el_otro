# Club Social y Deportivo DCColo - E1

## 1. Análisis del problema
(texto explicando el dominio)

## 2. Modelo E/R
(imagen de tu diagrama + explicación de decisiones)

## 3. Esquema Relacional

Sintaxis: **atributo** indica llave primaria y →TABLA indica llave foránea.

### Personas:
PERSONA (nombre: VARCHAR(100), correo: VARCHAR(100), direccion: VARCHAR(100), telefono: VARCHAR(100), alternativo: VARCHAR(100), **RUN**: VARCHAR(12), cod_comuna→COMUNA: INT, nombre_cargo→CARGO: VARCHAR(100))
> Persona está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Region:
REGION (**cod_region**: INT, nombre: VARCHAR(100))
> Region está en BCNF porque la dependencia funcional es 
> cod_region → nombre, donde cod_region es llave primaria.

### Comuna:
COMUNA (**cod_comuna**: INT, nombre: VARCHAR(100), cod_region→REGION: INT, nombre_sucursal→SUCURSALES: VARCHAR(100))
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Socios:
SOCIOS (**RUN**→PERSONA: VARCHAR(12), Fecha_IN: date, Fecha_OUT: date, estado: VARCHAR(100), nombre_sucursal→SUCURSAL: VARCHAR(100))
> Socios está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Contactos-Empresa:
CONTACTOS_EMPRESA (**RUN**→PERSONA: VARCHAR(12))
> Contactos-Empresa está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Clientes:
CLIENTES (**RUN**→PERSONA: VARCHAR(12))
> Clientes está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Usuarios:
USUARIOS (**RUN**→PERSONA: VARCHAR(12), email_reg: VARCHAR(100), clave_enc: VARCHAR(100))
> Usuarios está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Administrativos:
ADMINISTRATIVOS (**RUN**→USUARIOS: VARCHAR(12))
> Administrativos está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Invitados:
INVITADOS (**RUN**→PERSONA: VARCHAR(12), nombre_titular→TITULARES: VARCHAR(100))
> Invitados está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Titulares:
TITULARES (**RUN**→SOCIOS: VARCHAR(12))
> Titulares está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Beneficiarios:
BENEFICIARIOS (**RUN**→SOCIOS: VARCHAR(12))
> Beneficiarios está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Titulares:
ADICIONALES (**RUN**→SOCIOS: VARCHAR(12))
> Titulares está en BCNF porque la dependencia funcional es 
> RUN → todos los argumentos, donde RUN es llave primaria.

### Reserva:
RESERVA (**id_reserva**: int, fecha: date, ejecutado: VARCHAR(100), hora_IN: VARCHAR(5), hora_OUT: VARCHAR(5), Monto_P: int, nombre_titular→TITULARES: VARCHAR(100), nombre_lugar→LUGARES: VARCHAR(100))
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Membresia:
MEMBRESIA (**id_membresia**: int, fecha_in: date, fecha_out: date, monto_total: int, nombre_titular→TITULARES)
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Cuota:
CUOTA (**id_cuota**: int, n_cuota: int, monto: int, pagado: bool, fecha_pago: date, fecha_ven: date, id_membresia→MEMBRESIA: int)
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Lugares:
LUGARES (**id_lugar**: int, nombre: VARCHAR(100), tipo: VARCHAR(100), disponibilidad: VARCHAR(100), capacidad: int, nombre_sucursal→SUCURSAL: VARCHAR(100))
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Sucursales:
SUCURSALES (**Nombre**: VARCHAR(100), direccion: VARCHAR(100), Valores_M:int)
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Precio/tarifa:
PRECIO/TARIFA (**id_precio**: int, valor: int, dia_semana: VARCHAR(10), tipo_cobro: VARCHAR(10), fecha_in: date, fecha_out: date, hora: VARCHAR(5), nombre_lugar→LUGARES: VARCHAR(100))
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Cargo:
CARGO (**id_cargo**: int, nombre: VARCHAR(100), fecha_in: date, fecha_out: date, nombre_sucursal→SUCURSALES: VARCHAR(100))
> Cargo está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Eventos:
EVENTOS (**codigo**: int, nombre: VARCHAR(100), encargado: VARCHAR(100), RUN_encargado: VARCHAR(12), fecha: date)
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

### Asistentes:
ASISTENTES (**codigo**→EVENTOS: int, run: VARCHAR(12), nombre: VARCHAR(100))
> Comuna está en BCNF porque la dependencia funcional es 
> cod_comuna → todos los argumentos, donde cod_comuna es llave primaria.

## 4. Consultas SQL
(las 5 consultas)

## 5. Referencias