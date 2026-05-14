-- =============================================================
-- morosos.sql
-- Reporte de todos los socios con cuotas atrasadas.
-- Incluye: membresías + cuotas adicionales (socios dependientes
--          con cargo adicional dentro de la misma membresía).
-- Columnas: nombre completo, RUN, sucursal base,
--           monto total adeudado, número de cuotas atrasadas.
-- Ordenado por monto adeudado descendente.
-- Ejecución:  psql -U <usuario> -d <base> -f morosos.sql -o morosos.txt
-- =============================================================

\encoding UTF8
\pset format aligned
\pset border 2
\pset title 'Reporte de Socios Morosos – Club DCColo'

WITH morosos AS (
    SELECT
        p.nombre_completo                           AS nombre,
        s.run_persona                               AS run,
        su.nombre                                   AS sucursal,
        -- Fecha más antigua de cuota atrasada
        MIN(c.fecha_vencimiento)                    AS cuota_mas_antigua,
        -- Número total de cuotas atrasadas
        COUNT(c.id_cuota)                           AS cuotas_atrasadas,
        -- Monto total adeudado
        SUM(c.monto_total
            - COALESCE((
                SELECT SUM(pc.monto_pagado)
                FROM public.pago_cuota pc
                WHERE pc.cuota_numero = c.id_cuota
              ), 0)
        )                                           AS monto_adeudado
    FROM public.cuota      c
    JOIN public.membresia  m  ON m.id_membresia        = c.id_membresia
    JOIN public.socio      s  ON s.id_socio            = m.id_socio_titular
    JOIN public.persona    p  ON p.run                 = s.run_persona
    JOIN public.sucursal   su ON su.codigo_sucursal    = s.codigo_sucursal_base
    WHERE c.estado = 'atrasado'
    GROUP BY
        p.nombre_completo,
        s.run_persona,
        su.nombre
)
SELECT
    nombre                                  AS "Nombre completo",
    run                                     AS "RUN",
    sucursal                                AS "Sucursal base",
    cuota_mas_antigua                       AS "Cuota más antigua",
    cuotas_atrasadas                        AS "Nº cuotas atrasadas",
    monto_adeudado                          AS "Monto total adeudado ($)"
FROM morosos
WHERE monto_adeudado > 0
ORDER BY
    monto_adeudado DESC,
    nombre;
