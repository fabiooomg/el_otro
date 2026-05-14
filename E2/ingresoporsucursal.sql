-- =============================================================
-- ingresoporsucursal.sql
-- Reporte de ingresos anual 2025 por sucursal
-- Incluye: nombre sucursal, gerente, ingresos totales y % del total
-- =============================================================

WITH ingresos_sucursal AS (
    -- 1. Ingresos por Membresías (Cuotas pagadas en 2025)
    -- Se atribuyen a la sucursal base del socio
    SELECT 
        s.codigo_sucursal_base AS codigo_sucursal,
        SUM(pc.monto_pagado) AS monto
    FROM public.pago_cuota pc
    JOIN public.socio s ON pc.id_socio = s.id_socio
    WHERE EXTRACT(YEAR FROM pc.fecha_pago) = 2025
    GROUP BY s.codigo_sucursal_base

    UNION ALL

    -- 2. Ingresos por Eventos (Pagos realizados en 2025)
    -- Se atribuyen a la sucursal donde se realizó el evento
    SELECT 
        e.codigo_sucursal,
        SUM(pe.monto) AS monto
    FROM public.pago_evento pe
    JOIN public.evento e ON pe.codigo_evento = e.codigo_evento
    WHERE EXTRACT(YEAR FROM pe.fecha_pago) = 2025
    GROUP BY e.codigo_sucursal

    UNION ALL

    -- 3. Ingresos por Reservas (Arriendos de lugares en 2025)
    -- Se atribuyen a la sucursal dueña del lugar
    SELECT 
        l.codigo_sucursal,
        SUM(pr.monto) AS monto
    FROM public.pago_reserva pr
    JOIN public.reserva r ON pr.codigo_reserva = r.codigo_reserva
    JOIN public.lugar l ON r.codigo_lugar = l.codigo_lugar
    WHERE EXTRACT(YEAR FROM pr.fecha_pago) = 2025
    GROUP BY l.codigo_sucursal
),
ingresos_totales_sucursal AS (
    -- Sumatoria consolidada por sucursal
    SELECT 
        codigo_sucursal,
        SUM(monto) AS total_ingreso
    FROM ingresos_sucursal
    GROUP BY codigo_sucursal
),
ingreso_total_club AS (
    -- Sumatoria total de todas las sucursales para el cálculo del %
    SELECT SUM(total_ingreso) AS total_global FROM ingresos_totales_sucursal
),
gerentes AS (
    -- Identificar al gerente de cada sucursal activo durante 2025
    -- Se asume que el cargo contiene la palabra 'Gerente'
    SELECT DISTINCT ON (pc.codigo_sucursal)
        pc.codigo_sucursal,
        p.nombre_completo AS nombre_gerente
    FROM public.persona_cargo pc
    JOIN public.cargo c ON pc.id_cargo = c.id_cargo
    JOIN public.persona p ON pc.run_persona = p.run
    WHERE (c.nombre ILIKE '%gerente%' OR c.nombre ILIKE '%administrador%')
      AND pc.fecha_inicio <= '2025-12-31'
      AND (pc.fecha_termino IS NULL OR pc.fecha_termino >= '2025-01-01')
    ORDER BY pc.codigo_sucursal, pc.fecha_inicio DESC
)
-- Consulta Final
SELECT 
    s.nombre AS sucursal_nombre,
    COALESCE(g.nombre_gerente, 'Sin Gerente asignado') AS gerente_a_cargo,
    COALESCE(its.total_ingreso, 0) AS ingresos_totales,
    CASE 
        WHEN (SELECT total_global FROM ingreso_total_club) > 0 
        THEN ROUND((COALESCE(its.total_ingreso, 0) * 100.0) / (SELECT total_global FROM ingreso_total_club), 2)
        ELSE 0 
    END AS porcentaje_del_total
FROM public.sucursal s
LEFT JOIN ingresos_totales_sucursal its ON s.codigo_sucursal = its.codigo_sucursal
LEFT JOIN gerentes g ON s.codigo_sucursal = g.codigo_sucursal
ORDER BY ingresos_totales DESC;
