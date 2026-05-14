-- =============================================================
-- agenda.sql
-- Agenda de la sucursal "Santa Cruz" para la semana
-- que comienza el lunes 6 de abril de 2026 (06-04 al 12-04-2026)
-- Muestra: día, fecha, hora de inicio, lugar, y qué o quién
--          tiene reservado/programado cada lugar en ese bloque.
-- Agrupado por día → hora → lugar.
-- Ejecución:  psql -U <usuario> -d <base> -f agenda.sql -o agenda.txt
-- =============================================================

\encoding UTF8
\pset format aligned
\pset border 2
\pset title 'Agenda Sucursal Santa Cruz – Semana 06/04/2026'

-- Constantes de la semana
\set semana_ini '2026-04-06'
\set semana_fin '2026-04-12'

-- ---------------------------------------------------------------
-- CTE principal: une reservas y eventos en un único listado
-- ---------------------------------------------------------------
WITH semana AS (
    SELECT
        DATE '2026-04-06' AS fecha_ini,
        DATE '2026-04-12' AS fecha_fin
),

-- --- Bloque 1: Reservas de la semana en Santa Cruz ---
reservas AS (
    SELECT
        TO_CHAR(r.fecha_inicio, 'Day')               AS dia_semana,
        r.fecha_inicio::date                          AS fecha,
        TO_CHAR(r.fecha_inicio, 'HH24:MI')           AS hora_inicio,
        TO_CHAR(r.fecha_fin,    'HH24:MI')           AS hora_fin,
        l.nombre                                      AS lugar,
        l.tipo_lugar,
        'Reserva'                                     AS tipo_actividad,
        p.nombre_completo                             AS descripcion,
        p.run                                         AS identificador
    FROM public.reserva r
    JOIN public.lugar    l ON l.codigo_lugar    = r.codigo_lugar
    JOIN public.sucursal s ON s.codigo_sucursal = l.codigo_sucursal
    JOIN public.persona  p ON p.run             = r.run_reservante
    WHERE s.nombre = 'Santa Cruz'
      AND r.estado  IN ('reservada', 'ejecutada')
      AND r.fecha_inicio::date BETWEEN '2026-04-06' AND '2026-04-12'
),

-- --- Bloque 2: Eventos de la semana en Santa Cruz ---
eventos AS (
    SELECT
        TO_CHAR(e.fecha_evento, 'Day')               AS dia_semana,
        e.fecha_evento                                AS fecha,
        '00:00'                                       AS hora_inicio,
        '23:59'                                       AS hora_fin,
        l.nombre                                      AS lugar,
        l.tipo_lugar,
        'Evento'                                      AS tipo_actividad,
        e.nombre                                      AS descripcion,
        e.identificador_cliente                       AS identificador
    FROM public.evento   e
    JOIN public.lugar    l ON l.codigo_lugar    = e.codigo_lugar
    JOIN public.sucursal s ON s.codigo_sucursal = e.codigo_sucursal
    WHERE s.nombre     = 'Santa Cruz'
      AND e.fecha_evento BETWEEN '2026-04-06' AND '2026-04-12'
),

-- --- Unión y orden ---
agenda AS (
    SELECT * FROM reservas
    UNION ALL
    SELECT * FROM eventos
)

SELECT
    TRIM(dia_semana)   AS "Día",
    fecha              AS "Fecha",
    hora_inicio        AS "Hora inicio",
    hora_fin           AS "Hora fin",
    lugar              AS "Lugar",
    tipo_lugar         AS "Tipo lugar",
    tipo_actividad     AS "Tipo",
    descripcion        AS "Evento / Socio reservante",
    identificador      AS "RUN / Código cliente"
FROM agenda
ORDER BY
    fecha,
    hora_inicio,
    lugar;
