-- =============================================================
-- finbeneficiario.sql
-- Listado de beneficiarios-hijos que, en la PRÓXIMA RENOVACIÓN
-- de membresía (1 de enero del año siguiente), cumplirán 29 años,
-- lo que implica un costo adicional en esa renovación.
--
-- Lógica: el beneficiario tiene parentesco 'hijo' o 'hija' y
--   AGE('YYYY-01-01'::date, fecha_nacimiento) = 29 años.
-- (Si la próxima renovación es el 01-01-{anio+1}, entonces la
--  fecha de nacimiento del hijo debe ser en el año {anio+1}-29.)
--
-- Columnas (una sola línea por beneficiario):
--   RUN beneficiario, nombre beneficiario, correo beneficiario,
--   teléfono beneficiario,
--   RUN titular, nombre titular, correo titular, teléfono titular
--
-- Ejecución:
--   psql -U <usuario> -d <base> -f finbeneficiario.sql -o finbeneficiario.txt
-- =============================================================

\encoding UTF8
\pset format aligned
\pset border 2
\pset title 'Beneficiarios-hijos que cumplen 29 años en la próxima renovación'

WITH
-- Año de la próxima renovación (1-ene del año que viene)
proxima_renovacion AS (
    SELECT
        MAKE_DATE(EXTRACT(YEAR FROM CURRENT_DATE)::integer + 1, 1, 1) AS fecha_renovacion
),

-- Beneficiarios de tipo hijo/hija que cumplen 29 en la próxima renovación
beneficiarios AS (
    SELECT
        pb.run                                  AS run_beneficiario,
        pb.nombre_completo                      AS nombre_beneficiario,
        pb.email                                AS email_beneficiario,
        pb.telefono_celular                     AS telefono_beneficiario,
        sb.id_socio                             AS id_socio_beneficiario,
        st.id_socio                             AS id_socio_titular
    FROM public.socio      sb                              -- socio dependiente
    JOIN public.persona    pb ON pb.run = sb.run_persona   -- datos personales del hijo
    JOIN public.relacion_socio rs
           ON rs.id_socio_dependiente = sb.id_socio
          AND LOWER(rs.parentesco) IN ('hijo', 'hija', 'hijo/a')
    JOIN public.socio      st ON st.id_socio = rs.id_socio_titular
    CROSS JOIN proxima_renovacion
    WHERE pb.fecha_nacimiento IS NOT NULL
      -- En la fecha de renovación el beneficiario tendrá exactamente 29 años
      AND DATE_PART('year', AGE(
              (SELECT fecha_renovacion FROM proxima_renovacion),
              pb.fecha_nacimiento
          )) = 29
)

SELECT
    -- Datos del BENEFICIARIO
    b.run_beneficiario              AS "RUN beneficiario",
    b.nombre_beneficiario           AS "Nombre beneficiario",
    COALESCE(b.email_beneficiario, '—')
                                    AS "Correo beneficiario",
    COALESCE(b.telefono_beneficiario, '—')
                                    AS "Teléfono beneficiario",
    -- Datos del SOCIO TITULAR
    pt.run                          AS "RUN titular",
    pt.nombre_completo              AS "Nombre titular",
    COALESCE(pt.email, '—')         AS "Correo titular",
    COALESCE(pt.telefono_celular,'—')
                                    AS "Teléfono titular"
FROM beneficiarios b
JOIN public.socio   st ON st.id_socio  = b.id_socio_titular
JOIN public.persona pt ON pt.run       = st.run_persona
ORDER BY
    b.nombre_beneficiario;
