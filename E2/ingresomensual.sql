-- =============================================================
-- ingresomensual.sql
-- Ingreso mensual (mes en curso) de la sucursal "Santa Cruz"
-- por concepto de:  membresías  |  reservas ejecutadas  |  eventos
-- Agrupado en dos categorías:
--   • RECIBIDO   → ingresos efectivamente cobrados/pagados
--   • ESPERADO   → ingresos futuros pendientes de cobro
-- Ejecución:  psql -U <usuario> -d <base> -f ingresomensual.sql -o ingresomensual.txt
-- =============================================================

\encoding UTF8
\pset format aligned
\pset border 2
\pset title 'Ingreso Mensual – Sucursal Santa Cruz'

WITH
-- ---- Parámetros del mes actual ----
params AS (
    SELECT
        DATE_TRUNC('month', CURRENT_DATE)::date                  AS inicio_mes,
        (DATE_TRUNC('month', CURRENT_DATE)
         + INTERVAL '1 month' - INTERVAL '1 day')::date          AS fin_mes,
        TO_CHAR(CURRENT_DATE, 'Month YYYY')                      AS etiqueta_mes
),

-- =========================================================
-- A) MEMBRESÍAS  –  socios cuya sucursal_base es Santa Cruz
-- =========================================================

-- Cuotas PAGADAS en el mes actual
mem_recibido AS (
    SELECT
        'Membresías'            AS concepto,
        'RECIBIDO'              AS categoria,
        SUM(pc.monto_pagado)    AS monto
    FROM public.pago_cuota pc
    JOIN public.cuota      c  ON c.id_cuota   = pc.cuota_numero
    JOIN public.membresia  m  ON m.id_membresia = c.id_membresia
    JOIN public.socio      s  ON s.id_socio   = m.id_socio_titular
    JOIN public.sucursal   su ON su.codigo_sucursal = s.codigo_sucursal_base
    WHERE su.nombre            = 'Santa Cruz'
      AND pc.fecha_pago BETWEEN (SELECT inicio_mes FROM params)
                             AND (SELECT fin_mes    FROM params)
),

-- Cuotas PENDIENTES/ATRASADAS del mes actual (ingreso esperado)
mem_esperado AS (
    SELECT
        'Membresías'            AS concepto,
        'ESPERADO'              AS categoria,
        SUM(c.monto_total)      AS monto
    FROM public.cuota      c
    JOIN public.membresia  m  ON m.id_membresia = c.id_membresia
    JOIN public.socio      s  ON s.id_socio   = m.id_socio_titular
    JOIN public.sucursal   su ON su.codigo_sucursal = s.codigo_sucursal_base
    WHERE su.nombre            = 'Santa Cruz'
      AND c.mes = EXTRACT(MONTH FROM CURRENT_DATE)
      AND m.anio = EXTRACT(YEAR  FROM CURRENT_DATE)
      AND c.estado IN ('pendiente', 'atrasado')
),

-- =========================================================
-- B) RESERVAS EJECUTADAS  –  lugares de Santa Cruz
-- =========================================================

-- Pagos de reservas ejecutadas ya cobrados en el mes
res_recibido AS (
    SELECT
        'Reservas ejecutadas'   AS concepto,
        'RECIBIDO'              AS categoria,
        SUM(pr.monto)           AS monto
    FROM public.pago_reserva pr
    JOIN public.reserva      r  ON r.codigo_reserva = pr.codigo_reserva
    JOIN public.lugar        l  ON l.codigo_lugar   = r.codigo_lugar
    JOIN public.sucursal     su ON su.codigo_sucursal = l.codigo_sucursal
    WHERE su.nombre           = 'Santa Cruz'
      AND r.estado            = 'ejecutada'
      AND pr.fecha_pago BETWEEN (SELECT inicio_mes FROM params)
                             AND (SELECT fin_mes    FROM params)
),

-- Reservas ejecutadas en el mes cuyo pago AÚN no se registra
res_esperado AS (
    SELECT
        'Reservas ejecutadas'           AS concepto,
        'ESPERADO'                      AS categoria,
        SUM(pl.monto * (
            -- calcular horas o días según tipo_precio
            CASE
                WHEN pl.tipo_precio = 'hora'
                    THEN EXTRACT(EPOCH FROM (r.fecha_fin - r.fecha_inicio)) / 3600.0
                ELSE 1.0
            END
        ))::bigint                      AS monto
    FROM public.reserva      r
    JOIN public.lugar        l   ON l.codigo_lugar    = r.codigo_lugar
    JOIN public.sucursal     su  ON su.codigo_sucursal = l.codigo_sucursal
    -- precio vigente en la fecha de la reserva
    LEFT JOIN public.precio_lugar pl ON pl.codigo_lugar = l.codigo_lugar
        AND (pl.fecha_inicio IS NULL OR pl.fecha_inicio <= r.fecha_inicio::date)
        AND (pl.fecha_fin    IS NULL OR pl.fecha_fin    >= r.fecha_inicio::date)
    WHERE su.nombre = 'Santa Cruz'
      AND r.estado  = 'ejecutada'
      AND r.fecha_inicio::date BETWEEN (SELECT inicio_mes FROM params)
                                    AND (SELECT fin_mes    FROM params)
      -- que no tengan pago registrado
      AND NOT EXISTS (
          SELECT 1 FROM public.pago_reserva pr2
          WHERE pr2.codigo_reserva = r.codigo_reserva
      )
),

-- =========================================================
-- C) EVENTOS  –  realizados en Santa Cruz
-- =========================================================

-- Pagos de eventos ya cobrados en el mes
evt_recibido AS (
    SELECT
        'Eventos'               AS concepto,
        'RECIBIDO'              AS categoria,
        SUM(pe.monto)           AS monto
    FROM public.pago_evento pe
    JOIN public.evento      e  ON e.codigo_evento   = pe.codigo_evento
    JOIN public.sucursal    su ON su.codigo_sucursal = e.codigo_sucursal
    WHERE su.nombre       = 'Santa Cruz'
      AND pe.fecha_pago BETWEEN (SELECT inicio_mes FROM params)
                             AND (SELECT fin_mes    FROM params)
),

-- Eventos del mes cuyo saldo aún no fue cobrado
evt_esperado AS (
    SELECT
        'Eventos'               AS concepto,
        'ESPERADO'              AS categoria,
        -- monto pendiente = total evento – suma pagos ya registrados
        SUM(
            e.identificador_cliente::integer * 0   -- placeholder → calculado abajo
        )                       AS monto
    FROM public.evento e   -- necesitamos el monto total del evento
    WHERE 1=0              -- desactivado: ver subconsulta real debajo
),

-- Versión real de eventos esperados (sin columna monto_total en evento →
-- usamos tabla pago_evento suma y diferencia con total conocido)
evt_esperado_real AS (
    SELECT
        'Eventos'                                           AS concepto,
        'ESPERADO'                                          AS categoria,
        COALESCE(SUM(
            -- cada evento aporta la parte no cobrada
            e_total.monto_evento - COALESCE(e_pagado.monto_cobrado, 0)
        ), 0)::bigint                                       AS monto
    FROM (
        -- monto total declarado por evento (suma de todos sus pagos registrados
        -- tipo reserva + tipo ejecución cuando están completos)
        SELECT
            e.codigo_evento,
            SUM(pe.monto) AS monto_evento
        FROM public.evento       e
        JOIN public.pago_evento  pe ON pe.codigo_evento = e.codigo_evento
        JOIN public.sucursal     su ON su.codigo_sucursal = e.codigo_sucursal
        WHERE su.nombre = 'Santa Cruz'
          AND e.fecha_evento BETWEEN (SELECT inicio_mes FROM params)
                                  AND (SELECT fin_mes    FROM params)
        GROUP BY e.codigo_evento
    ) e_total
    LEFT JOIN (
        -- monto ya cobrado en el mes actual
        SELECT
            pe.codigo_evento,
            SUM(pe.monto) AS monto_cobrado
        FROM public.pago_evento pe
        WHERE pe.fecha_pago BETWEEN (SELECT inicio_mes FROM params)
                                AND (SELECT fin_mes    FROM params)
        GROUP BY pe.codigo_evento
    ) e_pagado USING (codigo_evento)
    -- Sólo eventos con saldo positivo pendiente
    WHERE (e_total.monto_evento - COALESCE(e_pagado.monto_cobrado, 0)) > 0
),

-- =========================================================
-- Unión final de todas las filas
-- =========================================================
todos AS (
    SELECT * FROM mem_recibido
    UNION ALL SELECT * FROM mem_esperado
    UNION ALL SELECT * FROM res_recibido
    UNION ALL SELECT * FROM res_esperado
    UNION ALL SELECT * FROM evt_recibido
    UNION ALL SELECT * FROM evt_esperado_real
)

SELECT
    (SELECT etiqueta_mes FROM params)           AS "Mes",
    concepto                                    AS "Concepto",
    categoria                                   AS "Categoría",
    COALESCE(monto, 0)                          AS "Monto ($)",
    -- porcentaje sobre el subtotal de cada categoría
    ROUND(
        100.0 * COALESCE(monto, 0) /
        NULLIF(SUM(COALESCE(monto, 0)) OVER (PARTITION BY categoria), 0)
    , 1)                                        AS "% por categoría"
FROM todos
ORDER BY
    categoria DESC,        -- RECIBIDO primero
    concepto;

-- ---- Totales por categoría ----
\echo ''
\echo '--- Subtotales ---'

WITH
params AS (
    SELECT
        DATE_TRUNC('month', CURRENT_DATE)::date   AS inicio_mes,
        (DATE_TRUNC('month', CURRENT_DATE)
         + INTERVAL '1 month' - INTERVAL '1 day')::date AS fin_mes
),
todos AS (
    -- membresías recibidas
    SELECT 'RECIBIDO' AS cat, COALESCE(SUM(pc.monto_pagado),0) AS monto
    FROM public.pago_cuota pc
    JOIN public.cuota c ON c.id_cuota=pc.cuota_numero
    JOIN public.membresia m ON m.id_membresia=c.id_membresia
    JOIN public.socio s ON s.id_socio=m.id_socio_titular
    JOIN public.sucursal su ON su.codigo_sucursal=s.codigo_sucursal_base
    WHERE su.nombre='Santa Cruz'
      AND pc.fecha_pago BETWEEN (SELECT inicio_mes FROM params) AND (SELECT fin_mes FROM params)

    UNION ALL

    -- reservas recibidas
    SELECT 'RECIBIDO', COALESCE(SUM(pr.monto),0)
    FROM public.pago_reserva pr
    JOIN public.reserva r ON r.codigo_reserva=pr.codigo_reserva
    JOIN public.lugar l ON l.codigo_lugar=r.codigo_lugar
    JOIN public.sucursal su ON su.codigo_sucursal=l.codigo_sucursal
    WHERE su.nombre='Santa Cruz' AND r.estado='ejecutada'
      AND pr.fecha_pago BETWEEN (SELECT inicio_mes FROM params) AND (SELECT fin_mes FROM params)

    UNION ALL

    -- eventos recibidos
    SELECT 'RECIBIDO', COALESCE(SUM(pe.monto),0)
    FROM public.pago_evento pe
    JOIN public.evento e ON e.codigo_evento=pe.codigo_evento
    JOIN public.sucursal su ON su.codigo_sucursal=e.codigo_sucursal
    WHERE su.nombre='Santa Cruz'
      AND pe.fecha_pago BETWEEN (SELECT inicio_mes FROM params) AND (SELECT fin_mes FROM params)

    UNION ALL

    -- membresías esperadas
    SELECT 'ESPERADO', COALESCE(SUM(c.monto_total),0)
    FROM public.cuota c
    JOIN public.membresia m ON m.id_membresia=c.id_membresia
    JOIN public.socio s ON s.id_socio=m.id_socio_titular
    JOIN public.sucursal su ON su.codigo_sucursal=s.codigo_sucursal_base
    WHERE su.nombre='Santa Cruz'
      AND c.mes=EXTRACT(MONTH FROM CURRENT_DATE)
      AND m.anio=EXTRACT(YEAR FROM CURRENT_DATE)
      AND c.estado IN ('pendiente','atrasado')
)
SELECT
    cat                  AS "Categoría",
    SUM(monto)           AS "Total ($)"
FROM todos
GROUP BY cat
ORDER BY cat DESC;
