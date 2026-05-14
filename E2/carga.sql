-- =============================================================
-- carga.sql  –  Club Social y Deportivo DCColo
-- IIC2413 - Bases de Datos - Etapa 2
-- =============================================================
-- Ejecución (desde directorio E2 del servidor):
--   psql -U <usuario> -d <base> -f carga.sql
-- Los archivos XXXOK.csv deben estar en el mismo directorio
-- desde donde se ejecuta psql.
-- =============================================================

\set ON_ERROR_STOP off
\encoding UTF8

-- =============================================================
-- 0.  TABLAS TEMPORALES DE LOG Y ERROR
-- =============================================================
BEGIN;

CREATE TEMP TABLE IF NOT EXISTS t_carga_log (
    id_log  serial,
    tabla   text,
    accion  text,
    detalle text
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE IF NOT EXISTS t_carga_err (
    id_err  serial,
    tabla   text,
    fila    text,
    motivo  text
) ON COMMIT PRESERVE ROWS;

COMMIT;

-- =============================================================
-- 1.  ESQUEMA COMPLETO  (drop en orden inverso de FK → create)
-- =============================================================
BEGIN;

-- ---- limpieza ----
DROP TABLE IF EXISTS public.pago_reserva        CASCADE;
DROP TABLE IF EXISTS public.reserva             CASCADE;
DROP TABLE IF EXISTS public.pago_evento         CASCADE;
DROP TABLE IF EXISTS public.asistente_evento    CASCADE;
DROP TABLE IF EXISTS public.evento              CASCADE;
DROP TABLE IF EXISTS public.contacto_empresa    CASCADE;
DROP TABLE IF EXISTS public.empresa             CASCADE;
DROP TABLE IF EXISTS public.persona_cargo       CASCADE;
DROP TABLE IF EXISTS public.cargo               CASCADE;
DROP TABLE IF EXISTS public.usuario             CASCADE;
DROP TABLE IF EXISTS public.pago_cuota          CASCADE;
DROP TABLE IF EXISTS public.cuota               CASCADE;
DROP TABLE IF EXISTS public.membresia           CASCADE;
DROP TABLE IF EXISTS public.relacion_socio      CASCADE;
DROP TABLE IF EXISTS public.socio               CASCADE;
DROP TABLE IF EXISTS public.precio_lugar        CASCADE;
DROP TABLE IF EXISTS public.lugar               CASCADE;
DROP TABLE IF EXISTS public.sucursal            CASCADE;
DROP TABLE IF EXISTS public.persona             CASCADE;
DROP TABLE IF EXISTS public.naci                CASCADE;
DROP TABLE IF EXISTS public.comuna              CASCADE;
DROP TABLE IF EXISTS public.region              CASCADE;

-- ---- REGION ----
CREATE TABLE public.region (
    codigo_region  integer      NOT NULL,
    nombre         varchar(100) NOT NULL,
    CONSTRAINT region_pkey    PRIMARY KEY (codigo_region),
    CONSTRAINT region_nom_uk  UNIQUE      (nombre)
);

-- ---- COMUNA ----
CREATE TABLE public.comuna (
    codigo_comuna  integer      NOT NULL,
    nombre         varchar(100) NOT NULL,
    codigo_region  integer      NOT NULL,
    CONSTRAINT comuna_pkey      PRIMARY KEY (codigo_comuna),
    CONSTRAINT comuna_region_fk FOREIGN KEY (codigo_region)
                                REFERENCES public.region(codigo_region)
                                ON UPDATE CASCADE ON DELETE RESTRICT
);

-- ---- SUCURSAL ----
CREATE TABLE public.sucursal (
    codigo_sucursal varchar(10)  NOT NULL,
    nombre          varchar(100) NOT NULL,
    direccion       varchar(150) NOT NULL,
    codigo_comuna   integer,
    CONSTRAINT sucursal_pkey      PRIMARY KEY (codigo_sucursal),
    CONSTRAINT sucursal_nom_uk    UNIQUE      (nombre),
    CONSTRAINT sucursal_comuna_fk FOREIGN KEY (codigo_comuna)
                                  REFERENCES public.comuna(codigo_comuna)
);

-- ---- LUGAR ----
CREATE TABLE public.lugar (
    codigo_lugar    varchar(15)  NOT NULL,
    nombre          varchar(100) NOT NULL,
    capacidad       integer      NOT NULL CHECK (capacidad > 0),
    codigo_sucursal varchar(10)  NOT NULL,
    tipo_lugar      varchar(20)  NOT NULL,
    CONSTRAINT lugar_pkey        PRIMARY KEY (codigo_lugar),
    CONSTRAINT lugar_suc_nom_uk  UNIQUE      (nombre, codigo_sucursal),
    CONSTRAINT lugar_sucursal_fk FOREIGN KEY (codigo_sucursal)
                                 REFERENCES public.sucursal(codigo_sucursal)
);

-- ---- PRECIO_LUGAR ----
CREATE TABLE public.precio_lugar (
    id_precio    serial       NOT NULL,
    codigo_lugar varchar(15),
    tipo_precio  varchar(20)  NOT NULL,
    dia_semana   varchar(15),
    hora_inicio  time,
    hora_termino time,
    fecha_inicio date,
    fecha_fin    date,
    monto        integer      NOT NULL CHECK (monto >= 0),
    CONSTRAINT precio_lugar_pkey   PRIMARY KEY (id_precio),
    CONSTRAINT precio_lugar_lug_fk FOREIGN KEY (codigo_lugar)
                                   REFERENCES public.lugar(codigo_lugar)
);

-- ---- PERSONA ----
CREATE TABLE public.persona (
    run                  varchar(12)  NOT NULL,
    nombre_completo      varchar(150) NOT NULL,
    email                varchar(150),
    telefono_celular     varchar(20),
    telefono_alternativo varchar(20),
    direccion_calle      varchar(150),
    codigo_comuna        integer,
    fecha_nacimiento     date,
    CONSTRAINT persona_pkey      PRIMARY KEY (run),
    CONSTRAINT persona_comuna_fk FOREIGN KEY (codigo_comuna)
                                 REFERENCES public.comuna(codigo_comuna)
);

-- ---- NACI (auxiliar) ----
CREATE TABLE public.naci (
    run varchar(12),
    nac date
);

-- ---- SOCIO ----
CREATE TABLE public.socio (
    id_socio             serial      NOT NULL,
    run_persona          varchar(12),
    tipo_socio           varchar(30) NOT NULL,
    fecha_inicio         date        NOT NULL,
    fecha_fin            date,
    codigo_sucursal_base varchar(10),
    CONSTRAINT socio_pkey          PRIMARY KEY (id_socio),
    CONSTRAINT socio_run_tipo_uk   UNIQUE      (run_persona, tipo_socio),
    CONSTRAINT socio_persona_fk    FOREIGN KEY (run_persona)
                                   REFERENCES public.persona(run),
    CONSTRAINT socio_sucursal_fk   FOREIGN KEY (codigo_sucursal_base)
                                   REFERENCES public.sucursal(codigo_sucursal)
);

-- ---- RELACION_SOCIO ----
CREATE TABLE public.relacion_socio (
    id_relacion          serial      NOT NULL,
    id_socio_titular     integer,
    id_socio_dependiente integer,
    parentesco           varchar(30) NOT NULL,
    CONSTRAINT relacion_socio_pkey       PRIMARY KEY (id_relacion),
    CONSTRAINT relacion_soc_dep_uk       UNIQUE (id_socio_titular, id_socio_dependiente),
    CONSTRAINT relacion_titular_fk       FOREIGN KEY (id_socio_titular)
                                         REFERENCES public.socio(id_socio),
    CONSTRAINT relacion_dependiente_fk   FOREIGN KEY (id_socio_dependiente)
                                         REFERENCES public.socio(id_socio)
);

-- ---- MEMBRESIA ----
CREATE TABLE public.membresia (
    id_membresia     serial  NOT NULL,
    id_socio_titular integer,
    anio             integer NOT NULL CHECK (anio >= 2000),
    fecha_inicio     date    NOT NULL,
    fecha_fin        date    NOT NULL,
    monto_base       integer NOT NULL CHECK (monto_base >= 0),
    CONSTRAINT membresia_pkey      PRIMARY KEY (id_membresia),
    CONSTRAINT membresia_soc_yr_uk UNIQUE      (id_socio_titular, anio),
    CONSTRAINT membresia_socio_fk  FOREIGN KEY (id_socio_titular)
                                   REFERENCES public.socio(id_socio)
);

-- ---- CUOTA ----
CREATE TABLE public.cuota (
    id_cuota          serial      NOT NULL,
    id_membresia      integer,
    mes               integer     NOT NULL CHECK (mes BETWEEN 1 AND 12),
    fecha_vencimiento date        NOT NULL,
    monto_total       integer     NOT NULL CHECK (monto_total >= 0),
    estado            varchar(20) NOT NULL
                      CHECK (estado IN ('pagado','atrasado','pendiente')),
    CONSTRAINT cuota_pkey         PRIMARY KEY (id_cuota),
    CONSTRAINT cuota_mem_mes_uk   UNIQUE      (id_membresia, mes),
    CONSTRAINT cuota_membresia_fk FOREIGN KEY (id_membresia)
                                  REFERENCES public.membresia(id_membresia)
);

-- ---- PAGO_CUOTA ----
CREATE TABLE public.pago_cuota (
    id_pago_cuota serial      NOT NULL,
    cuota_numero  integer,
    fecha_pago    date        NOT NULL,
    monto_pagado  integer     NOT NULL CHECK (monto_pagado >= 0),
    medio_pago    varchar(30),
    id_socio      integer,
    CONSTRAINT pago_cuota_pkey      PRIMARY KEY (id_pago_cuota),
    CONSTRAINT pago_cuota_cuota_fk  FOREIGN KEY (cuota_numero)
                                    REFERENCES public.cuota(id_cuota)
);

-- ---- USUARIO ----
CREATE TABLE public.usuario (
    id_usuario       serial       NOT NULL,
    run_persona      varchar(12),
    email_login      varchar(150) NOT NULL,
    clave_encriptada varchar(255) NOT NULL,
    tipo_usuario     varchar(30)  NOT NULL,
    CONSTRAINT usuario_pkey        PRIMARY KEY (id_usuario),
    CONSTRAINT usuario_email_uk    UNIQUE      (email_login),
    CONSTRAINT usuario_persona_fk  FOREIGN KEY (run_persona)
                                   REFERENCES public.persona(run)
);

-- ---- CARGO ----
CREATE TABLE public.cargo (
    id_cargo serial       NOT NULL,
    nombre   varchar(100) NOT NULL,
    CONSTRAINT cargo_pkey      PRIMARY KEY (id_cargo),
    CONSTRAINT cargo_nombre_uk UNIQUE      (nombre)
);

-- ---- PERSONA_CARGO ----
CREATE TABLE public.persona_cargo (
    id_persona_cargo serial      NOT NULL,
    run_persona      varchar(12),
    id_cargo         integer,
    codigo_sucursal  varchar(10),
    fecha_inicio     date        NOT NULL,
    fecha_termino    date,
    CONSTRAINT persona_cargo_pkey         PRIMARY KEY (id_persona_cargo),
    CONSTRAINT persona_cargo_persona_fk   FOREIGN KEY (run_persona)
                                          REFERENCES public.persona(run),
    CONSTRAINT persona_cargo_cargo_fk     FOREIGN KEY (id_cargo)
                                          REFERENCES public.cargo(id_cargo),
    CONSTRAINT persona_cargo_sucursal_fk  FOREIGN KEY (codigo_sucursal)
                                          REFERENCES public.sucursal(codigo_sucursal)
);

-- ---- EMPRESA ----
CREATE TABLE public.empresa (
    rut_empresa varchar(15)  NOT NULL,
    nombre      varchar(150) NOT NULL,
    CONSTRAINT empresa_pkey PRIMARY KEY (rut_empresa)
);

-- ---- CONTACTO_EMPRESA ----
CREATE TABLE public.contacto_empresa (
    id_contacto serial      NOT NULL,
    rut_empresa varchar(15),
    run_persona varchar(12),
    nombre      varchar(50),
    cargo       varchar(50),
    CONSTRAINT contacto_empresa_pkey        PRIMARY KEY (id_contacto),
    CONSTRAINT contacto_empresa_empresa_fk  FOREIGN KEY (rut_empresa)
                                            REFERENCES public.empresa(rut_empresa)
);

-- ---- EVENTO ----
CREATE TABLE public.evento (
    codigo_evento         varchar(20)  NOT NULL,
    nombre                varchar(150) NOT NULL,
    fecha_evento          date         NOT NULL,
    codigo_lugar          varchar(15),
    codigo_sucursal       varchar(10),
    tipo_cliente          varchar(20)  NOT NULL
                          CHECK (tipo_cliente IN ('socio','persona','empresa')),
    identificador_cliente varchar(20)  NOT NULL,
    CONSTRAINT evento_pkey         PRIMARY KEY (codigo_evento),
    CONSTRAINT evento_lugar_fk     FOREIGN KEY (codigo_lugar)
                                   REFERENCES public.lugar(codigo_lugar),
    CONSTRAINT evento_sucursal_fk  FOREIGN KEY (codigo_sucursal)
                                   REFERENCES public.sucursal(codigo_sucursal)
);

-- ---- ASISTENTE_EVENTO ----
CREATE TABLE public.asistente_evento (
    id_asistente     serial       NOT NULL,
    codigo_evento    varchar(20),
    run_asistente    varchar(12),
    nombre_asistente varchar(150),
    CONSTRAINT asistente_evento_pkey       PRIMARY KEY (id_asistente),
    CONSTRAINT asistente_evento_evento_fk  FOREIGN KEY (codigo_evento)
                                           REFERENCES public.evento(codigo_evento)
);

-- ---- PAGO_EVENTO ----
CREATE TABLE public.pago_evento (
    id_pago_evento serial      NOT NULL,
    codigo_evento  varchar(20),
    fecha_pago     date        NOT NULL,
    monto          integer     NOT NULL CHECK (monto >= 0),
    tipo_pago      varchar(20) NOT NULL,
    CONSTRAINT pago_evento_pkey       PRIMARY KEY (id_pago_evento),
    CONSTRAINT pago_evento_evento_fk  FOREIGN KEY (codigo_evento)
                                      REFERENCES public.evento(codigo_evento)
);

-- ---- RESERVA ----
CREATE TABLE public.reserva (
    codigo_reserva varchar(20) NOT NULL,
    codigo_lugar   varchar(15),
    run_reservante varchar(12),
    fecha_inicio   timestamp   NOT NULL,
    fecha_fin      timestamp   NOT NULL,
    estado         varchar(20) NOT NULL
                   CHECK (estado IN ('reservada','ejecutada','cancelada')),
    CONSTRAINT reserva_pkey        PRIMARY KEY (codigo_reserva),
    CONSTRAINT reserva_lugar_fk    FOREIGN KEY (codigo_lugar)
                                   REFERENCES public.lugar(codigo_lugar),
    CONSTRAINT reserva_persona_fk  FOREIGN KEY (run_reservante)
                                   REFERENCES public.persona(run)
);

-- ---- PAGO_RESERVA ----
CREATE TABLE public.pago_reserva (
    id_pago_reserva serial      NOT NULL,
    codigo_reserva  varchar(20),
    fecha_pago      date        NOT NULL,
    monto           integer     NOT NULL CHECK (monto >= 0),
    medio_pago      varchar(30),
    CONSTRAINT pago_reserva_pkey        PRIMARY KEY (id_pago_reserva),
    CONSTRAINT pago_reserva_reserva_fk  FOREIGN KEY (codigo_reserva)
                                        REFERENCES public.reserva(codigo_reserva)
);

COMMIT;


-- =============================================================
-- 2.  TABLAS DE STAGING  (temporales, una por CSV)
-- =============================================================
BEGIN;

CREATE TEMP TABLE stg_regiones (
    codigo_comuna  text, nombre_comuna  text,
    codigo_region  text, nombre_region  text
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE stg_sucursales (
    sucursal_nombre      text, direccion_sucursal    text,
    comuna_nombre        text, lugar_nombre          text,
    tipo_lugar           text, capacidad_personas    text,
    precio               text, descuento_socio       text,
    tipo_precio          text, dia_semana            text,
    hora_inicio          text, hora_termino          text,
    fecha_inicio_vig     text, fecha_fin_vig         text
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE stg_personas (
    run_persona           text, nombre_completo        text,
    email                 text, telefono_celular       text,
    telefono_alternativo  text, direccion_calle        text,
    comuna_nombre         text, region_codigo          text,
    region_nombre         text, tipo_persona           text,
    run_socio_titular     text, parentesco             text,
    fecha_nacimiento      text, fecha_inicio_membresia text,
    fecha_fin_membresia   text, es_usuario_sistema     text,
    tipo_usuario          text, clave_en_texto_plano   text,
    sucursal_base_nombre  text
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE stg_reservas (
    codigo_reserva  text, fecha_reserva   text,
    fecha_inicio    text, fecha_fin       text,
    estado_reserva  text, run_reservante  text,
    nombre_reservante text,es_socio        text,
    lugar_nombre    text, sucursal_nombre text,
    monto_total     text, monto_pagado    text,
    medio_pago      text, fecha_pago      text
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE stg_eventos (
    evento_id             text, nombre_evento          text,
    fecha_contratacion    text, fecha_evento           text,
    lugar_nombre          text, sucursal_nombre        text,
    tipo_cliente          text, run_cliente            text,
    nombre_cliente        text, rut_contacto_empresa   text,
    nombre_contacto       text, cargo_contacto         text,
    lista_asistentes      text, monto_total_evento     text,
    monto_pagado_reserva  text, monto_pagado_ejecucion text
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE stg_pagos (
    pago_id             text, run_socio_titular    text,
    nombre_socio        text, anio_membresia       text,
    mes_cuota           text, fecha_vencimiento    text,
    monto_membresia     text, monto_adicionales    text,
    monto_total         text, estado_pago          text,
    fecha_pago          text, medio_pago           text
) ON COMMIT PRESERVE ROWS;

CREATE TEMP TABLE stg_cargos (
    run_persona       text, sucursal_nombre   text,
    nombre_cargo      text, fecha_inicio_cargo text,
    fecha_termino_cargo text
) ON COMMIT PRESERVE ROWS;

COMMIT;


-- =============================================================
-- 3.  CARGA DE ARCHIVOS CSV OK  (\COPY psql metacommand)
-- Los archivos deben estar en el directorio de trabajo actual.
-- =============================================================

-- Región y Comunas (header ya tiene nombres ASCII gracias a main.php)
\COPY stg_regiones   (codigo_comuna, nombre_comuna, codigo_region, nombre_region)
  FROM 'regiones_comunasOK.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Sucursales y Lugares
\COPY stg_sucursales (sucursal_nombre, direccion_sucursal, comuna_nombre, lugar_nombre, tipo_lugar,
                      capacidad_personas, precio, descuento_socio, tipo_precio, dia_semana,
                      hora_inicio, hora_termino, fecha_inicio_vig, fecha_fin_vig)
  FROM 'sucursales_lugaresOK.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Personas y Socios
\COPY stg_personas   (run_persona, nombre_completo, email, telefono_celular, telefono_alternativo,
                      direccion_calle, comuna_nombre, region_codigo, region_nombre, tipo_persona,
                      run_socio_titular, parentesco, fecha_nacimiento, fecha_inicio_membresia,
                      fecha_fin_membresia, es_usuario_sistema, tipo_usuario, clave_en_texto_plano,
                      sucursal_base_nombre)
  FROM 'personas_sociosOK.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Reservas (lista de columnas explícita → descarta header con acento si existiera)
\COPY stg_reservas   (codigo_reserva, fecha_reserva, fecha_inicio, fecha_fin, estado_reserva,
                      run_reservante, nombre_reservante, es_socio, lugar_nombre, sucursal_nombre,
                      monto_total, monto_pagado, medio_pago, fecha_pago)
  FROM 'reservas_arriendos OK.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Eventos (header tiene acento en "fecha_contratación" → mapeamos por posición)
\COPY stg_eventos    (evento_id, nombre_evento, fecha_contratacion, fecha_evento, lugar_nombre,
                      sucursal_nombre, tipo_cliente, run_cliente, nombre_cliente,
                      rut_contacto_empresa, nombre_contacto, cargo_contacto,
                      lista_asistentes, monto_total_evento, monto_pagado_reserva, monto_pagado_ejecucion)
  FROM 'eventosOK.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Pagos de membresías
\COPY stg_pagos      (pago_id, run_socio_titular, nombre_socio, anio_membresia, mes_cuota,
                      fecha_vencimiento, monto_membresia, monto_adicionales, monto_total,
                      estado_pago, fecha_pago, medio_pago)
  FROM 'pagos_membresiasOK.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Cargos administrativos
\COPY stg_cargos     (run_persona, sucursal_nombre, nombre_cargo, fecha_inicio_cargo, fecha_termino_cargo)
  FROM 'cargos_administrativosOK.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');


-- =============================================================
-- 4.  DISTRIBUCIÓN: REGION y COMUNA
-- =============================================================
BEGIN;

INSERT INTO public.region (codigo_region, nombre)
SELECT DISTINCT codigo_region::integer, nombre_region
FROM stg_regiones
WHERE codigo_region ~ '^\d+$'
  AND nombre_region != ''
ON CONFLICT (codigo_region) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('region', 'INSERT', (SELECT COUNT(*)::text || ' regiones insertadas' FROM public.region));

-- Registrar regiones rechazadas (región fuera de rango o nula)
INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT DISTINCT 'region', codigo_region || '|' || nombre_region,
       'region_codigo inválido o nombre vacío'
FROM stg_regiones
WHERE NOT (codigo_region ~ '^\d+$' AND nombre_region != '')
  AND (codigo_region IS NOT NULL OR nombre_region IS NOT NULL);

INSERT INTO public.comuna (codigo_comuna, nombre, codigo_region)
SELECT r.codigo_comuna::integer, r.nombre_comuna, r.codigo_region::integer
FROM stg_regiones r
WHERE r.codigo_comuna ~ '^\d+$'
  AND r.nombre_comuna != ''
  AND EXISTS (SELECT 1 FROM public.region rg WHERE rg.codigo_region = r.codigo_region::integer)
ON CONFLICT (codigo_comuna) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('comuna', 'INSERT', (SELECT COUNT(*)::text || ' comunas insertadas' FROM public.comuna));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'comuna', r.codigo_comuna || '|' || r.nombre_comuna,
       CASE
           WHEN NOT (r.codigo_comuna ~ '^\d+$') THEN 'codigo_comuna no numérico'
           WHEN r.nombre_comuna = ''             THEN 'nombre_comuna vacío'
           ELSE 'codigo_region sin registro padre en region'
       END
FROM stg_regiones r
WHERE NOT (
    r.codigo_comuna ~ '^\d+$'
    AND r.nombre_comuna != ''
    AND EXISTS (SELECT 1 FROM public.region rg WHERE rg.codigo_region = r.codigo_region::integer)
);

COMMIT;


-- =============================================================
-- 5.  DISTRIBUCIÓN: SUCURSAL, LUGAR, PRECIO_LUGAR
-- =============================================================
BEGIN;

-- Tabla auxiliar temporal: sucursales únicas con código generado
CREATE TEMP TABLE tmp_suc AS
SELECT DISTINCT ON (sucursal_nombre)
    sucursal_nombre,
    direccion_sucursal,
    comuna_nombre,
    'S' || LPAD(ROW_NUMBER() OVER (ORDER BY sucursal_nombre)::text, 3, '0') AS codigo_suc
FROM stg_sucursales
ORDER BY sucursal_nombre;

INSERT INTO public.sucursal (codigo_sucursal, nombre, direccion, codigo_comuna)
SELECT
    ts.codigo_suc,
    ts.sucursal_nombre,
    ts.direccion_sucursal,
    c.codigo_comuna
FROM tmp_suc ts
LEFT JOIN public.comuna c ON LOWER(c.nombre) = LOWER(ts.comuna_nombre)
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('sucursal', 'INSERT', (SELECT COUNT(*)::text || ' sucursales insertadas' FROM public.sucursal));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'sucursal', ts.sucursal_nombre, 'comuna_nombre no encontrada en tabla comuna'
FROM tmp_suc ts
WHERE NOT EXISTS (SELECT 1 FROM public.comuna c WHERE LOWER(c.nombre) = LOWER(ts.comuna_nombre));

-- Tabla auxiliar: lugares únicos por sucursal con código generado
CREATE TEMP TABLE tmp_lug AS
SELECT DISTINCT ON (sucursal_nombre, lugar_nombre)
    sucursal_nombre,
    lugar_nombre,
    tipo_lugar,
    capacidad_personas,
    'L' || LPAD(ROW_NUMBER() OVER (ORDER BY sucursal_nombre, lugar_nombre)::text, 4, '0') AS codigo_lug
FROM stg_sucursales
ORDER BY sucursal_nombre, lugar_nombre;

INSERT INTO public.lugar (codigo_lugar, nombre, capacidad, codigo_sucursal, tipo_lugar)
SELECT
    tl.codigo_lug,
    tl.lugar_nombre,
    tl.capacidad_personas::integer,
    s.codigo_sucursal,
    tl.tipo_lugar
FROM tmp_lug tl
JOIN public.sucursal s ON s.nombre = tl.sucursal_nombre
WHERE tl.capacidad_personas ~ '^\d+$'
  AND tl.capacidad_personas::integer > 0
ON CONFLICT (nombre, codigo_sucursal) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('lugar', 'INSERT', (SELECT COUNT(*)::text || ' lugares insertados' FROM public.lugar));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'lugar', tl.sucursal_nombre || '|' || tl.lugar_nombre,
       CASE
           WHEN NOT EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = tl.sucursal_nombre)
               THEN 'sucursal padre no encontrada'
           ELSE 'capacidad_personas inválida (' || tl.capacidad_personas || ')'
       END
FROM tmp_lug tl
WHERE NOT (
    tl.capacidad_personas ~ '^\d+$'
    AND tl.capacidad_personas::integer > 0
    AND EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = tl.sucursal_nombre)
);

-- PRECIO_LUGAR: cada fila en stg_sucursales es un periodo de precio
INSERT INTO public.precio_lugar (codigo_lugar, tipo_precio, dia_semana, hora_inicio, hora_termino,
                                 fecha_inicio, fecha_fin, monto)
SELECT
    l.codigo_lugar,
    sl.tipo_precio,
    NULLIF(sl.dia_semana,    ''),
    NULLIF(sl.hora_inicio,   '')::time,
    NULLIF(sl.hora_termino,  '')::time,
    NULLIF(sl.fecha_inicio_vig, '')::date,
    NULLIF(sl.fecha_fin_vig,    '')::date,
    sl.precio::integer
FROM stg_sucursales sl
JOIN public.sucursal s ON s.nombre = sl.sucursal_nombre
JOIN public.lugar    l ON l.nombre = sl.lugar_nombre AND l.codigo_sucursal = s.codigo_sucursal
WHERE sl.precio ~ '^\d+$'    -- sólo filas con precio numérico válido
  AND sl.tipo_precio != '';

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('precio_lugar', 'INSERT', (SELECT COUNT(*)::text || ' precios insertados' FROM public.precio_lugar));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'precio_lugar',
       sl.sucursal_nombre || '|' || sl.lugar_nombre || '|' || sl.precio,
       CASE
           WHEN NOT (sl.precio ~ '^\d+$') THEN 'precio no numérico'
           WHEN sl.tipo_precio = ''        THEN 'tipo_precio vacío'
           ELSE 'lugar o sucursal padre no encontrado'
       END
FROM stg_sucursales sl
WHERE NOT (
    sl.precio ~ '^\d+$'
    AND sl.tipo_precio != ''
    AND EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = sl.sucursal_nombre)
    AND EXISTS (SELECT 1 FROM public.lugar l
                JOIN public.sucursal s ON l.codigo_sucursal = s.codigo_sucursal
                WHERE l.nombre = sl.lugar_nombre AND s.nombre = sl.sucursal_nombre)
);

COMMIT;


-- =============================================================
-- 6.  DISTRIBUCIÓN: PERSONA
-- Precaución: el mismo RUN puede aparecer en varias filas
-- (distintos roles). Se usa DISTINCT ON para tomar la primera.
-- Además se añaden reservantes y contactos de empresa que no
-- estén en personas_socios (para respetar las FK).
-- =============================================================
BEGIN;

INSERT INTO public.persona (run, nombre_completo, email, telefono_celular,
                             telefono_alternativo, direccion_calle,
                             codigo_comuna, fecha_nacimiento)
SELECT DISTINCT ON (sp.run_persona)
    sp.run_persona,
    sp.nombre_completo,
    NULLIF(sp.email, ''),
    NULLIF(sp.telefono_celular,    ''),
    NULLIF(sp.telefono_alternativo,''),
    NULLIF(sp.direccion_calle,     ''),
    c.codigo_comuna,
    NULLIF(sp.fecha_nacimiento, '')::date
FROM stg_personas sp
LEFT JOIN public.comuna c
       ON LOWER(c.nombre) = LOWER(sp.comuna_nombre)
      AND c.codigo_region  = sp.region_codigo::integer
ORDER BY sp.run_persona
ON CONFLICT (run) DO NOTHING;

-- Reservantes que no aparecen en personas_socios
INSERT INTO public.persona (run, nombre_completo)
SELECT DISTINCT r.run_reservante, r.nombre_reservante
FROM stg_reservas r
WHERE r.run_reservante != ''
  AND NOT EXISTS (SELECT 1 FROM public.persona p WHERE p.run = r.run_reservante)
ON CONFLICT (run) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('persona', 'INSERT', (SELECT COUNT(*)::text || ' personas insertadas' FROM public.persona));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'persona', sp.run_persona || '|' || sp.nombre_completo,
       'fecha_nacimiento no parseable: ' || sp.fecha_nacimiento
FROM stg_personas sp
WHERE sp.fecha_nacimiento != ''
  AND sp.fecha_nacimiento !~ '^\d{4}-\d{2}-\d{2}$'
LIMIT 500;

COMMIT;


-- =============================================================
-- 7.  DISTRIBUCIÓN: SOCIO y RELACION_SOCIO
-- =============================================================
BEGIN;

INSERT INTO public.socio (run_persona, tipo_socio, fecha_inicio, fecha_fin, codigo_sucursal_base)
SELECT
    sp.run_persona,
    CASE sp.tipo_persona
        WHEN 'socio_titular' THEN 'titular'
        ELSE sp.tipo_persona   -- beneficiario / adicional
    END,
    NULLIF(sp.fecha_inicio_membresia, '')::date,
    NULLIF(sp.fecha_fin_membresia,    '')::date,
    s.codigo_sucursal
FROM stg_personas sp
LEFT JOIN public.sucursal s ON s.nombre = sp.sucursal_base_nombre
WHERE sp.tipo_persona IN ('socio_titular', 'beneficiario', 'adicional')
  AND NULLIF(sp.fecha_inicio_membresia,'') IS NOT NULL
  AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = sp.run_persona)
ON CONFLICT (run_persona, tipo_socio) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('socio', 'INSERT', (SELECT COUNT(*)::text || ' socios insertados' FROM public.socio));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'socio', sp.run_persona || '|' || sp.tipo_persona,
       CASE
           WHEN NULLIF(sp.fecha_inicio_membresia,'') IS NULL
               THEN 'fecha_inicio_membresia vacía'
           WHEN NOT EXISTS (SELECT 1 FROM public.persona p WHERE p.run = sp.run_persona)
               THEN 'persona padre no existe'
           ELSE 'otro error'
       END
FROM stg_personas sp
WHERE sp.tipo_persona IN ('socio_titular','beneficiario','adicional')
  AND NOT (
      NULLIF(sp.fecha_inicio_membresia,'') IS NOT NULL
      AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = sp.run_persona)
  );

-- RELACION_SOCIO: vincula titular ↔ dependiente usando id_socio
INSERT INTO public.relacion_socio (id_socio_titular, id_socio_dependiente, parentesco)
SELECT
    st.id_socio,      -- el titular
    sd.id_socio,      -- el dependiente
    sp.parentesco
FROM stg_personas sp
-- socio del dependiente
JOIN public.socio sd ON sd.run_persona = sp.run_persona
-- socio del titular
JOIN public.socio st ON st.run_persona = sp.run_socio_titular
                    AND st.tipo_socio  = 'titular'
WHERE sp.run_socio_titular != ''
  AND sp.parentesco        != ''
  AND sp.tipo_persona IN ('beneficiario','adicional')
ON CONFLICT (id_socio_titular, id_socio_dependiente) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('relacion_socio', 'INSERT',
        (SELECT COUNT(*)::text || ' relaciones insertadas' FROM public.relacion_socio));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'relacion_socio', sp.run_persona || '|' || sp.run_socio_titular,
       'titular o dependiente sin registro en socio'
FROM stg_personas sp
WHERE sp.run_socio_titular != ''
  AND sp.parentesco        != ''
  AND sp.tipo_persona IN ('beneficiario','adicional')
  AND NOT (
      EXISTS (SELECT 1 FROM public.socio sd WHERE sd.run_persona = sp.run_persona)
      AND EXISTS (SELECT 1 FROM public.socio st
                  WHERE st.run_persona = sp.run_socio_titular AND st.tipo_socio = 'titular')
  );

COMMIT;


-- =============================================================
-- 8.  DISTRIBUCIÓN: MEMBRESIA, CUOTA, PAGO_CUOTA
-- Fuente: pagos_membresiasOK.csv
-- Cada combinación única (run_socio_titular, anio) → 1 membresía
-- =============================================================
BEGIN;

INSERT INTO public.membresia (id_socio_titular, anio, fecha_inicio, fecha_fin, monto_base)
SELECT
    s.id_socio,
    pg.anio_membresia::integer,
    (pg.anio_membresia || '-01-01')::date AS fecha_inicio,
    (pg.anio_membresia || '-12-31')::date AS fecha_fin,
    MIN(pg.monto_membresia::integer)       AS monto_base
FROM (
    SELECT DISTINCT run_socio_titular, anio_membresia, monto_membresia
    FROM stg_pagos
    WHERE anio_membresia ~ '^\d{4}$'
      AND monto_membresia ~ '^\d+$'
) pg
JOIN public.socio s ON s.run_persona = pg.run_socio_titular
                   AND s.tipo_socio  = 'titular'
GROUP BY s.id_socio, pg.anio_membresia
ON CONFLICT (id_socio_titular, anio) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('membresia', 'INSERT', (SELECT COUNT(*)::text || ' membresías insertadas' FROM public.membresia));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT DISTINCT 'membresia', pg.run_socio_titular || '|' || pg.anio_membresia,
       CASE
           WHEN NOT (pg.anio_membresia ~ '^\d{4}$') THEN 'anio_membresia inválido'
           WHEN NOT EXISTS (SELECT 1 FROM public.socio s
                            WHERE s.run_persona = pg.run_socio_titular AND s.tipo_socio = 'titular')
               THEN 'socio titular no encontrado en tabla socio'
           ELSE 'otro error'
       END
FROM stg_pagos pg
WHERE NOT (
    pg.anio_membresia ~ '^\d{4}$'
    AND pg.monto_membresia ~ '^\d+$'
    AND EXISTS (SELECT 1 FROM public.socio s
                WHERE s.run_persona = pg.run_socio_titular AND s.tipo_socio = 'titular')
);

-- CUOTA: una fila del staging = una cuota mensual
INSERT INTO public.cuota (id_membresia, mes, fecha_vencimiento, monto_total, estado)
SELECT
    m.id_membresia,
    pg.mes_cuota::integer,
    pg.fecha_vencimiento::date,
    pg.monto_total::integer,
    pg.estado_pago
FROM stg_pagos pg
JOIN public.socio s ON s.run_persona = pg.run_socio_titular AND s.tipo_socio = 'titular'
JOIN public.membresia m ON m.id_socio_titular = s.id_socio
                       AND m.anio = pg.anio_membresia::integer
WHERE pg.mes_cuota         ~ '^\d+$'
  AND pg.monto_total       ~ '^\d+$'
  AND pg.fecha_vencimiento ~ '^\d{4}-\d{2}-\d{2}$'
  AND pg.estado_pago IN ('pagado','atrasado','pendiente')
ON CONFLICT (id_membresia, mes) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('cuota', 'INSERT', (SELECT COUNT(*)::text || ' cuotas insertadas' FROM public.cuota));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'cuota', pg.run_socio_titular || '|' || pg.anio_membresia || '|mes' || pg.mes_cuota,
       'cuota rechazada: estado inválido, monto no numérico, fecha inválida o membresía no existe'
FROM stg_pagos pg
WHERE NOT (
    pg.mes_cuota         ~ '^\d+$'
    AND pg.monto_total   ~ '^\d+$'
    AND pg.fecha_vencimiento ~ '^\d{4}-\d{2}-\d{2}$'
    AND pg.estado_pago IN ('pagado','atrasado','pendiente')
    AND EXISTS (SELECT 1 FROM public.socio s
                JOIN public.membresia m ON m.id_socio_titular = s.id_socio
                WHERE s.run_persona = pg.run_socio_titular
                  AND s.tipo_socio  = 'titular'
                  AND m.anio = pg.anio_membresia::integer)
);

-- PAGO_CUOTA: sólo cuotas que tienen fecha y estado=pagado
INSERT INTO public.pago_cuota (cuota_numero, fecha_pago, monto_pagado, medio_pago, id_socio)
SELECT
    c.id_cuota,
    pg.fecha_pago::date,
    pg.monto_total::integer,
    NULLIF(pg.medio_pago,''),
    s.id_socio
FROM stg_pagos pg
JOIN public.socio    s ON s.run_persona = pg.run_socio_titular AND s.tipo_socio = 'titular'
JOIN public.membresia m ON m.id_socio_titular = s.id_socio AND m.anio = pg.anio_membresia::integer
JOIN public.cuota    c ON c.id_membresia = m.id_membresia AND c.mes = pg.mes_cuota::integer
WHERE pg.fecha_pago ~ '^\d{4}-\d{2}-\d{2}$'
  AND pg.estado_pago = 'pagado';

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('pago_cuota', 'INSERT', (SELECT COUNT(*)::text || ' pagos de cuota insertados' FROM public.pago_cuota));

COMMIT;


-- =============================================================
-- 9.  DISTRIBUCIÓN: USUARIO
-- =============================================================
BEGIN;

INSERT INTO public.usuario (run_persona, email_login, clave_encriptada, tipo_usuario)
SELECT DISTINCT ON (sp.run_persona)
    sp.run_persona,
    sp.email,                          -- email usado como login
    md5(sp.clave_en_texto_plano),      -- hash MD5 de la clave
    sp.tipo_usuario
FROM stg_personas sp
WHERE sp.es_usuario_sistema = 'SI'
  AND NULLIF(sp.email,'')              IS NOT NULL
  AND NULLIF(sp.clave_en_texto_plano,'') IS NOT NULL
  AND sp.tipo_usuario IN ('admin','administrativo','socio')
  AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = sp.run_persona)
ORDER BY sp.run_persona
ON CONFLICT (email_login) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('usuario', 'INSERT', (SELECT COUNT(*)::text || ' usuarios insertados' FROM public.usuario));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'usuario', sp.run_persona || '|' || sp.email,
       CASE
           WHEN NULLIF(sp.email,'') IS NULL         THEN 'email vacío (requerido para login)'
           WHEN NULLIF(sp.clave_en_texto_plano,'') IS NULL THEN 'clave vacía'
           WHEN sp.tipo_usuario NOT IN ('admin','administrativo','socio') THEN 'tipo_usuario inválido'
           ELSE 'persona padre no existe'
       END
FROM stg_personas sp
WHERE sp.es_usuario_sistema = 'SI'
  AND NOT (
      NULLIF(sp.email,'')               IS NOT NULL
      AND NULLIF(sp.clave_en_texto_plano,'') IS NOT NULL
      AND sp.tipo_usuario IN ('admin','administrativo','socio')
      AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = sp.run_persona)
  );

COMMIT;


-- =============================================================
-- 10. DISTRIBUCIÓN: CARGO y PERSONA_CARGO
-- =============================================================
BEGIN;

INSERT INTO public.cargo (nombre)
SELECT DISTINCT nombre_cargo
FROM stg_cargos
WHERE nombre_cargo != ''
ON CONFLICT (nombre) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('cargo', 'INSERT', (SELECT COUNT(*)::text || ' cargos insertados' FROM public.cargo));

INSERT INTO public.persona_cargo (run_persona, id_cargo, codigo_sucursal, fecha_inicio, fecha_termino)
SELECT
    ca.run_persona,
    cg.id_cargo,
    s.codigo_sucursal,
    ca.fecha_inicio_cargo::date,
    NULLIF(ca.fecha_termino_cargo,'')::date
FROM stg_cargos ca
JOIN public.cargo    cg ON cg.nombre = ca.nombre_cargo
JOIN public.sucursal s  ON s.nombre  = ca.sucursal_nombre
WHERE ca.fecha_inicio_cargo ~ '^\d{4}-\d{2}-\d{2}$'
  AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = ca.run_persona);

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('persona_cargo', 'INSERT',
        (SELECT COUNT(*)::text || ' asignaciones de cargo insertadas' FROM public.persona_cargo));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'persona_cargo', ca.run_persona || '|' || ca.nombre_cargo || '|' || ca.sucursal_nombre,
       CASE
           WHEN NOT EXISTS (SELECT 1 FROM public.persona p WHERE p.run = ca.run_persona)
               THEN 'persona no existe en tabla persona'
           WHEN NOT EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = ca.sucursal_nombre)
               THEN 'sucursal no encontrada'
           ELSE 'fecha_inicio_cargo inválida o cargo vacío'
       END
FROM stg_cargos ca
WHERE NOT (
    ca.fecha_inicio_cargo ~ '^\d{4}-\d{2}-\d{2}$'
    AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = ca.run_persona)
    AND EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = ca.sucursal_nombre)
    AND ca.nombre_cargo != ''
);

COMMIT;


-- =============================================================
-- 11. DISTRIBUCIÓN: EMPRESA y CONTACTO_EMPRESA
-- =============================================================
BEGIN;

INSERT INTO public.empresa (rut_empresa, nombre)
SELECT DISTINCT ev.run_cliente, ev.nombre_cliente
FROM stg_eventos ev
WHERE ev.tipo_cliente = 'empresa'
  AND ev.run_cliente  != ''
ON CONFLICT (rut_empresa) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('empresa', 'INSERT', (SELECT COUNT(*)::text || ' empresas insertadas' FROM public.empresa));

-- Contactos: un contacto por evento de empresa (cuando hay run de contacto)
INSERT INTO public.contacto_empresa (rut_empresa, run_persona, nombre, cargo)
SELECT DISTINCT ON (ev.rut_contacto_empresa, ev.run_cliente)
    ev.run_cliente,
    NULLIF(ev.rut_contacto_empresa,''),
    NULLIF(ev.nombre_contacto,''),
    NULLIF(ev.cargo_contacto,'')
FROM stg_eventos ev
WHERE ev.tipo_cliente          = 'empresa'
  AND ev.rut_contacto_empresa != ''
  AND EXISTS (SELECT 1 FROM public.empresa e WHERE e.rut_empresa = ev.run_cliente)
ORDER BY ev.rut_contacto_empresa, ev.run_cliente;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('contacto_empresa', 'INSERT',
        (SELECT COUNT(*)::text || ' contactos de empresa insertados' FROM public.contacto_empresa));

COMMIT;


-- =============================================================
-- 12. DISTRIBUCIÓN: EVENTO, ASISTENTE_EVENTO, PAGO_EVENTO
-- =============================================================
BEGIN;

INSERT INTO public.evento (codigo_evento, nombre, fecha_evento, codigo_lugar,
                           codigo_sucursal, tipo_cliente, identificador_cliente)
SELECT
    ev.evento_id,
    ev.nombre_evento,
    ev.fecha_evento::date,
    l.codigo_lugar,
    s.codigo_sucursal,
    ev.tipo_cliente,
    ev.run_cliente
FROM stg_eventos ev
JOIN public.sucursal s ON s.nombre = ev.sucursal_nombre
LEFT JOIN public.lugar l ON LOWER(l.nombre) = LOWER(ev.lugar_nombre)
                        AND l.codigo_sucursal = s.codigo_sucursal
WHERE ev.fecha_evento ~ '^\d{4}-\d{2}-\d{2}$'
  AND ev.nombre_evento != ''
  AND ev.tipo_cliente IN ('socio','persona','empresa')
  AND ev.run_cliente   != ''
ON CONFLICT (codigo_evento) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('evento', 'INSERT', (SELECT COUNT(*)::text || ' eventos insertados' FROM public.evento));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'evento', ev.evento_id || '|' || ev.nombre_evento,
       CASE
           WHEN NOT (ev.fecha_evento ~ '^\d{4}-\d{2}-\d{2}$') THEN 'fecha_evento inválida'
           WHEN ev.tipo_cliente NOT IN ('socio','persona','empresa') THEN 'tipo_cliente inválido'
           WHEN NOT EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = ev.sucursal_nombre)
               THEN 'sucursal no encontrada'
           ELSE 'run_cliente vacío o nombre_evento vacío'
       END
FROM stg_eventos ev
WHERE NOT (
    ev.fecha_evento  ~ '^\d{4}-\d{2}-\d{2}$'
    AND ev.nombre_evento != ''
    AND ev.tipo_cliente IN ('socio','persona','empresa')
    AND ev.run_cliente   != ''
    AND EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = ev.sucursal_nombre)
);

-- ASISTENTE_EVENTO: parsear lista separada por ';'
-- unnest + string_to_array sobre la lista de asistentes
INSERT INTO public.asistente_evento (codigo_evento, nombre_asistente)
SELECT
    ev.evento_id,
    TRIM(asistente) AS nombre_asistente
FROM stg_eventos ev,
     LATERAL unnest(string_to_array(ev.lista_asistentes, ';')) AS asistente
WHERE ev.lista_asistentes != ''
  AND TRIM(asistente)     != ''
  AND EXISTS (SELECT 1 FROM public.evento e WHERE e.codigo_evento = ev.evento_id);

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('asistente_evento', 'INSERT',
        (SELECT COUNT(*)::text || ' asistentes insertados' FROM public.asistente_evento));

-- PAGO_EVENTO: pago en reserva (tipo='reserva') y pago en ejecución (tipo='ejecucion')
INSERT INTO public.pago_evento (codigo_evento, fecha_pago, monto, tipo_pago)
SELECT ev.evento_id,
       COALESCE(NULLIF(ev.fecha_contratacion,''), ev.fecha_evento)::date,
       ev.monto_pagado_reserva::integer,
       'reserva'
FROM stg_eventos ev
WHERE ev.monto_pagado_reserva ~ '^\d+$'
  AND ev.monto_pagado_reserva::integer > 0
  AND EXISTS (SELECT 1 FROM public.evento e WHERE e.codigo_evento = ev.evento_id)

UNION ALL

SELECT ev.evento_id,
       ev.fecha_evento::date,
       ev.monto_pagado_ejecucion::integer,
       'ejecucion'
FROM stg_eventos ev
WHERE ev.monto_pagado_ejecucion ~ '^\d+$'
  AND ev.monto_pagado_ejecucion::integer > 0
  AND ev.fecha_evento ~ '^\d{4}-\d{2}-\d{2}$'
  AND EXISTS (SELECT 1 FROM public.evento e WHERE e.codigo_evento = ev.evento_id);

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('pago_evento', 'INSERT',
        (SELECT COUNT(*)::text || ' pagos de evento insertados' FROM public.pago_evento));

COMMIT;


-- =============================================================
-- 13. DISTRIBUCIÓN: RESERVA y PAGO_RESERVA
-- =============================================================
BEGIN;

INSERT INTO public.reserva (codigo_reserva, codigo_lugar, run_reservante,
                             fecha_inicio, fecha_fin, estado)
SELECT
    r.codigo_reserva,
    l.codigo_lugar,
    r.run_reservante,
    r.fecha_inicio::timestamp,
    r.fecha_fin::timestamp,
    r.estado_reserva
FROM stg_reservas r
JOIN public.sucursal s ON s.nombre = r.sucursal_nombre
LEFT JOIN public.lugar l ON LOWER(l.nombre) = LOWER(r.lugar_nombre)
                        AND l.codigo_sucursal = s.codigo_sucursal
WHERE r.codigo_reserva != ''
  AND r.fecha_inicio   ~ '^\d{4}-\d{2}-\d{2}'
  AND r.fecha_fin      ~ '^\d{4}-\d{2}-\d{2}'
  AND r.estado_reserva IN ('reservada','ejecutada','cancelada')
  AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = r.run_reservante)
ON CONFLICT (codigo_reserva) DO NOTHING;

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('reserva', 'INSERT', (SELECT COUNT(*)::text || ' reservas insertadas' FROM public.reserva));

INSERT INTO t_carga_err (tabla, fila, motivo)
SELECT 'reserva', r.codigo_reserva || '|' || r.run_reservante,
       CASE
           WHEN r.codigo_reserva = '' THEN 'codigo_reserva vacío'
           WHEN NOT EXISTS (SELECT 1 FROM public.persona p WHERE p.run = r.run_reservante)
               THEN 'run_reservante no existe en persona'
           WHEN r.estado_reserva NOT IN ('reservada','ejecutada','cancelada')
               THEN 'estado_reserva inválido'
           WHEN NOT EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = r.sucursal_nombre)
               THEN 'sucursal no encontrada'
           ELSE 'fecha_inicio o fecha_fin inválida'
       END
FROM stg_reservas r
WHERE NOT (
    r.codigo_reserva != ''
    AND r.fecha_inicio ~ '^\d{4}-\d{2}-\d{2}'
    AND r.fecha_fin   ~ '^\d{4}-\d{2}-\d{2}'
    AND r.estado_reserva IN ('reservada','ejecutada','cancelada')
    AND EXISTS (SELECT 1 FROM public.persona p WHERE p.run = r.run_reservante)
    AND EXISTS (SELECT 1 FROM public.sucursal s WHERE s.nombre = r.sucursal_nombre)
);

-- PAGO_RESERVA: sólo reservas con monto_pagado > 0 y fecha_pago válida
INSERT INTO public.pago_reserva (codigo_reserva, fecha_pago, monto, medio_pago)
SELECT
    r.codigo_reserva,
    r.fecha_pago::date,
    r.monto_pagado::integer,
    NULLIF(r.medio_pago,'')
FROM stg_reservas r
WHERE r.monto_pagado ~ '^\d+$'
  AND r.monto_pagado::integer > 0
  AND r.fecha_pago ~ '^\d{4}-\d{2}-\d{2}$'
  AND EXISTS (SELECT 1 FROM public.reserva rv WHERE rv.codigo_reserva = r.codigo_reserva);

INSERT INTO t_carga_log (tabla, accion, detalle)
VALUES ('pago_reserva', 'INSERT',
        (SELECT COUNT(*)::text || ' pagos de reserva insertados' FROM public.pago_reserva));

COMMIT;


-- =============================================================
-- 14. RESUMEN FINAL Y EXPORTACIÓN DE LOG/ERR
-- =============================================================
BEGIN;

-- Resumen de la carga
INSERT INTO t_carga_log (tabla, accion, detalle)
SELECT 'RESUMEN', 'TOTAL', tabla || ': ' || COUNT(*)::text || ' registros'
FROM (
    SELECT 'region'           AS tabla FROM public.region
    UNION ALL SELECT 'comuna'           FROM public.comuna
    UNION ALL SELECT 'sucursal'         FROM public.sucursal
    UNION ALL SELECT 'lugar'            FROM public.lugar
    UNION ALL SELECT 'precio_lugar'     FROM public.precio_lugar
    UNION ALL SELECT 'persona'          FROM public.persona
    UNION ALL SELECT 'socio'            FROM public.socio
    UNION ALL SELECT 'relacion_socio'   FROM public.relacion_socio
    UNION ALL SELECT 'membresia'        FROM public.membresia
    UNION ALL SELECT 'cuota'            FROM public.cuota
    UNION ALL SELECT 'pago_cuota'       FROM public.pago_cuota
    UNION ALL SELECT 'usuario'          FROM public.usuario
    UNION ALL SELECT 'cargo'            FROM public.cargo
    UNION ALL SELECT 'persona_cargo'    FROM public.persona_cargo
    UNION ALL SELECT 'empresa'          FROM public.empresa
    UNION ALL SELECT 'contacto_empresa' FROM public.contacto_empresa
    UNION ALL SELECT 'evento'           FROM public.evento
    UNION ALL SELECT 'asistente_evento' FROM public.asistente_evento
    UNION ALL SELECT 'pago_evento'      FROM public.pago_evento
    UNION ALL SELECT 'reserva'          FROM public.reserva
    UNION ALL SELECT 'pago_reserva'     FROM public.pago_reserva
) t
GROUP BY tabla;

COMMIT;

-- Exportar cargaLOG.csv
\COPY (SELECT id_log, tabla, accion, detalle FROM t_carga_log ORDER BY id_log)
  TO 'cargaLOG.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Exportar cargaERR.csv
\COPY (SELECT id_err, tabla, fila, motivo FROM t_carga_err ORDER BY id_err)
  TO 'cargaERR.csv'
  WITH (FORMAT CSV, HEADER TRUE, DELIMITER ';', ENCODING 'UTF8');

-- Mostrar resumen en consola
\echo '============================================='
\echo 'CARGA COMPLETADA – RESUMEN POR TABLA'
\echo '============================================='
SELECT tabla, COUNT(*) AS registros_en_log
FROM t_carga_log
GROUP BY tabla ORDER BY tabla;

\echo ''
\echo 'Errores registrados en cargaERR.csv:'
SELECT tabla, COUNT(*) AS errores
FROM t_carga_err
GROUP BY tabla ORDER BY tabla;
