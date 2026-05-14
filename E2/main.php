<?php

define('INPUT_DIR',  __DIR__ . '/');
define('OUTPUT_DIR', __DIR__ . '/');

define('SEP', ';');
function readCsv(string $path): array {
    if (!file_exists($path)) {
        die("ERROR: File not found: $path\n");
    }
    $raw = file_get_contents($path);
    // Strip UTF-8 BOM
    $raw = ltrim($raw, "\xEF\xBB\xBF");
    // Normalise line endings
    $raw = str_replace(["\r\n", "\r"], "\n", $raw);
    // Fix common encoding artifact: windows-1252 / latin chars embedded in UTF-8
    // (the c—nyuge pattern comes from \x97 em-dash in windows-1252 read as UTF-8)
    $raw = fixEncoding($raw);

    $lines  = explode("\n", trim($raw));
    if (empty($lines)) return [];

    $header = str_getcsv(array_shift($lines), SEP, '"', '\\');
    $header = array_map('trim', $header);

    $rows = [];
    foreach ($lines as $line) {
        $line = trim($line);
        if ($line === '') continue;
        $values = str_getcsv($line, SEP, '"', '\\');
        // Pad short rows
        while (count($values) < count($header)) $values[] = '';
        $row = array_combine($header, array_slice($values, 0, count($header)));
        // Trim all values
        $row = array_map('trim', $row);
        $rows[] = $row;
    }
    return $rows;
}
function fixEncoding(string $s): string {
    $s = str_replace('c—nyuge',  'cónyuge',  $s);
    $s = str_replace('c–nyuge',  'cónyuge',  $s);
    $s = str_replace("c\xc3\xb3nyuge", 'cónyuge', $s); 
    $s = str_replace('MantenciÃ³n', 'Mantención', $s);
    $s = str_replace('fecha_contrataci', 'fecha_contrataci', $s); 
    $s = str_replace("Caba\xef\xbf\xbda", 'Cabaña', $s);
    $s = str_replace('Caba?a', 'Cabaña', $s);
    $replacements = [
        'Ã³' => 'ó', 'Ã±' => 'ñ', 'Ã¡' => 'á', 'Ã©' => 'é',
        'Ã­' => 'í', 'Ãº' => 'ú', 'Ã¼' => 'ü',
        'Ã"' => 'Ó', 'Ã'  => 'Ñ', 'Ã' => 'Á',
    ];
    return str_replace(array_keys($replacements), array_values($replacements), $s);
}

/**
 * Write rows to a CSV file. $header is an array of column names.
 */
function writeCsv(string $path, array $header, array $rows): void {
    $f = fopen($path, 'w');
    // Write UTF-8 BOM so Excel opens it correctly
    fwrite($f, "\xEF\xBB\xBF");
    fputcsv($f, $header, SEP, '"', '\\');
    foreach ($rows as $row) {
        fputcsv($f, $row, SEP, '"', '\\');
    }
    fclose($f);
}

/**
 * Append a log entry: [line, field, original, action, new_value]
 */
function logAction(array &$log, int $line, string $field,
                   string $original, string $action, string $newValue = ''): void {
    $log[] = [$line, $field, $original, $action, $newValue];
}

// ============================================================
// HELPER: VALIDATION & CONVERSION
// ============================================================

/**
 * Validate and fix a Chilean RUN.
 * Returns the normalised RUN (digits-DV) or false if irreparable.
 */
function validateRun(string $run): string|false {
    $run = trim(strtoupper($run));
    // Remove dots (empresa format: 76.000.000-0)
    $run = str_replace('.', '', $run);
    // Must match NNNNNNNN-D or NNNNNNN-D or NNN...N-D
    if (!preg_match('/^(\d{7,8})-([0-9K])$/', $run, $m)) {
        return false;
    }
    $digits = $m[1];
    $dv     = $m[2];
    // Compute expected check digit
    $expected = computeDv($digits);
    if ($expected === false) return false;
    if ($dv !== (string)$expected) return false;
    return $digits . '-' . $dv;
}

/**
 * Compute Chilean RUN check digit for a numeric string.
 * Returns the digit (0-9 or 'K') or false on error.
 */
function computeDv(string $digits): string|false {
    $digits = strrev($digits);
    $sum    = 0;
    $mult   = 2;
    for ($i = 0; $i < strlen($digits); $i++) {
        $sum += intval($digits[$i]) * $mult;
        $mult = ($mult === 7) ? 2 : $mult + 1;
    }
    $r = 11 - ($sum % 11);
    if ($r === 11) return '0';
    if ($r === 10) return 'K';
    return (string)$r;
}

/**
 * Parse and normalise a date string to YYYY-MM-DD.
 * Handles: DD-MM-YY, DD-MM-YYYY, YYYY-MM-DD, YYYY-MM.
 * Returns [normalised_date, log_note] or [null, error_note].
 */
function normaliseDate(string $raw): array {
    $raw = trim($raw);
    if ($raw === '') return ['', ''];

    // Already correct
    if (preg_match('/^\d{4}-\d{2}-\d{2}$/', $raw)) {
        return [$raw, ''];
    }
    // YYYY-MM  →  YYYY-MM-01
    if (preg_match('/^(\d{4})-(\d{2})$/', $raw, $m)) {
        return [$m[1] . '-' . $m[2] . '-01',
                "Partial date '$raw' completed to {$m[1]}-{$m[2]}-01"];
    }
    // DD-MM-YY  →  YYYY-MM-DD (assume 20xx for YY < 30, else 19xx)
    if (preg_match('/^(\d{2})-(\d{2})-(\d{2})$/', $raw, $m)) {
        $yy   = (int)$m[3];
        $year = ($yy < 30) ? 2000 + $yy : 1900 + $yy;
        return [$year . '-' . $m[2] . '-' . $m[1],
                "Date '$raw' converted from DD-MM-YY to $year-{$m[2]}-{$m[1]}"];
    }
    // DD-MM-YYYY
    if (preg_match('/^(\d{2})-(\d{2})-(\d{4})$/', $raw, $m)) {
        return [$m[3] . '-' . $m[2] . '-' . $m[1],
                "Date '$raw' converted from DD-MM-YYYY to {$m[3]}-{$m[2]}-{$m[1]}"];
    }
    // -YYYY  (negative year: invalid birth year)
    if (preg_match('/^-(\d{4})$/', $raw, $m)) {
        return [null, "Invalid date '$raw' (negative year): set to NULL"];
    }
    return [null, "Unrecognisable date format '$raw': set to NULL"];
}

/**
 * Normalise a datetime string to YYYY-MM-DD HH:MM.
 */
function normaliseDatetime(string $raw): array {
    $raw = trim($raw);
    if ($raw === '') return ['', ''];

    // Already YYYY-MM-DD HH:MM or YYYY-MM-DD HH:MM:SS
    if (preg_match('/^(\d{4}-\d{2}-\d{2})\s(\d{2}:\d{2})/', $raw, $m)) {
        return [$m[1] . ' ' . $m[2], ''];
    }
    // DD-MM-YY HH:MM
    if (preg_match('/^(\d{2})-(\d{2})-(\d{2})\s(\d{2}:\d{2})$/', $raw, $m)) {
        $yy   = (int)$m[3];
        $year = ($yy < 30) ? 2000 + $yy : 1900 + $yy;
        $date = "$year-{$m[2]}-{$m[1]} {$m[4]}";
        return [$date, "Datetime '$raw' converted to $date"];
    }
    // DD-MM-YY with no time → treat as date only, append 00:00
    [$d, $note] = normaliseDate($raw);
    if ($d !== null) {
        $dt = $d . ' 00:00';
        return [$dt, ($note ? $note . '; ' : '') . "No time component, appended 00:00"];
    }
    return [null, "Unrecognisable datetime '$raw': set to NULL"];
}

/**
 * Validate an email address. Returns [fixed_email|null, note].
 */
function validateEmail(string $email): array {
    $email = trim($email);
    if ($email === '') return ['', ''];
    // Fix double dots in local part or domain
    if (strpos($email, '..') !== false) {
        $fixed = preg_replace('/\.\.+/', '.', $email);
        return [$fixed, "Fixed double dot in email '$email' → '$fixed'"];
    }
    // Basic RFC 5322-ish check
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        return [null, "Invalid email '$email': removed"];
    }
    return [$email, ''];
}

/**
 * Validate a phone number. Returns [fixed_phone, note].
 * - Must be 9 digits.
 * - Strip trailing .0 (Excel float artefact).
 * - 8-digit number: prepend '9'.
 * - Otherwise: replace with sentinel 100000000.
 */
function validatePhone(string $phone): array {
    $phone = trim($phone);
    if ($phone === '') return ['', ''];
    // Strip .0 artefact
    $phone = preg_replace('/\.0+$/', '', $phone);
    // Remove non-numeric
    $digits = preg_replace('/\D/', '', $phone);
    if (strlen($digits) === 9) return [$digits, ''];
    if (strlen($digits) === 8) {
        $fixed = '9' . $digits;
        return [$fixed, "Phone '$phone' (8 digits) padded with prefix 9 → $fixed"];
    }
    return ['100000000', "Invalid phone '$phone' replaced with placeholder 100000000"];
}

/**
 * Normalise a precio (price) field.
 * Handles text like "nueve mil" → 9000.
 * Returns [int_string|null, note].
 */
function normalisePrecio(string $raw): array {
    $raw = trim($raw);
    if ($raw === '') return ['', ''];
    if (ctype_digit($raw)) return [$raw, ''];

    // Text-number mapping (Spanish)
    $textMap = [
        'cero' => 0, 'un' => 1, 'uno' => 1, 'dos' => 2, 'tres' => 3,
        'cuatro' => 4, 'cinco' => 5, 'seis' => 6, 'siete' => 7,
        'ocho' => 8, 'nueve' => 9, 'diez' => 10, 'once' => 11,
        'doce' => 12, 'trece' => 13, 'catorce' => 14, 'quince' => 15,
        'veinte' => 20, 'treinta' => 30, 'cuarenta' => 40,
        'cincuenta' => 50, 'sesenta' => 60, 'setenta' => 70,
        'ochenta' => 80, 'noventa' => 90,
        'cien' => 100, 'ciento' => 100, 'mil' => 1000,
    ];

    $lower  = strtolower($raw);
    $words  = preg_split('/[\s\-]+/', $lower);
    $total  = 0;
    $parsed = true;
    $running = 0;
    foreach ($words as $w) {
        if (!isset($textMap[$w])) { $parsed = false; break; }
        $v = $textMap[$w];
        if ($v === 1000) {
            $running = ($running === 0) ? 1000 : $running * 1000;
            $total  += $running;
            $running = 0;
        } else {
            $running += $v;
        }
    }
    $total += $running;

    if ($parsed && $total > 0) {
        return [(string)$total, "Text price '$raw' converted to $total"];
    }
    return [null, "Unrecognisable price '$raw': record flagged as error"];
}

/**
 * Normalise region name to official Chilean name.
 */
function normaliseRegion(string $name): string {
    $map = [
        'metropolitana'  => 'Región Metropolitana de Santiago',
        'biobio'         => 'Biobío',
        'bio-bio'        => 'Biobío',
        "bio bio"        => 'Biobío',
        'valparaiso'     => 'Valparaíso',
        "o'higgins"      => "Libertador General Bernardo O'Higgins",
        'ohiggins'       => "Libertador General Bernardo O'Higgins",
        'araucania'      => 'La Araucanía',
        'los rios'       => 'Los Ríos',
        'los lagos'      => 'Los Lagos',
        'atacama'        => 'Atacama',
        'coquimbo'       => 'Coquimbo',
        'maule'          => 'Maule',
        'ñuble'          => 'Ñuble',
        'nuble'          => 'Ñuble',
        'arica'          => 'Arica y Parinacota',
        'tarapaca'       => 'Tarapacá',
        'antofagasta'    => 'Antofagasta',
        'aysen'          => 'Aysén del General Carlos Ibáñez del Campo',
        'magallanes'     => 'Magallanes y de la Antártica Chilena',
    ];
    $key = strtolower(trim($name));
    return $map[$key] ?? $name;
}

/**
 * Normalise parentesco. Valid values for beneficiarios: cónyuge, hijo, hija.
 * Returns [normalised, note].
 */
function normaliseParentesco(string $raw, string $tipo): array {
    $raw = trim($raw);
    // Fix encoding artifact
    if (in_array($raw, ['c—nyuge', 'c–nyuge', 'cónyuge'])) {
        $note = ($raw !== 'cónyuge') ? "Fixed encoding in parentesco '$raw' → cónyuge" : '';
        return ['cónyuge', $note];
    }
    if ($raw === '') return ['', ''];

    // Valid values
    $valid = ['cónyuge', 'hijo', 'hija', 'hijo/a'];
    if (in_array(strtolower($raw), $valid)) return [strtolower($raw), ''];

    // Invalid parentesco values
    if ($tipo === 'beneficiario') {
        return [null, "Invalid parentesco '$raw' for beneficiario: record flagged"];
    }
    // For non-beneficiarios, parentesco should be empty
    return ['', "Parentesco '$raw' not applicable for tipo '$tipo': cleared"];
}

// ============================================================
// PROCESS 1: personas_socios.csv
// ============================================================
function procesarPersonas(): void {
    $file   = INPUT_DIR . 'personas_socios.csv';
    $rows   = readCsv($file);
    $header = array_keys($rows[0]);

    $okRows  = [];
    $errRows = [];
    $logRows = [['linea', 'campo', 'valor_original', 'accion', 'valor_nuevo']];

    $runsSeen = []; // detect duplicates per run+tipo_persona

    foreach ($rows as $lineIdx => $row) {
        $lineNum = $lineIdx + 2; // 1-based + header
        $errors  = [];

        // --- RUN ---
        $run = validateRun($row['run_persona']);
        if ($run === false) {
            $errors[] = "run_persona '{$row['run_persona']}' inválido (dígito verificador incorrecto o formato)";
            logAction($logRows, $lineNum, 'run_persona', $row['run_persona'],
                      'ELIMINAR: RUN inválido, irreparable', '');
        } else {
            if ($run !== $row['run_persona']) {
                logAction($logRows, $lineNum, 'run_persona', $row['run_persona'],
                          'CORRECCIÓN: RUN normalizado (puntos eliminados)', $run);
            }
            $row['run_persona'] = $run;
        }

        // --- Duplicado run+tipo ---
        $dupKey = $row['run_persona'] . '|' . $row['tipo_persona'];
        if (isset($runsSeen[$dupKey])) {
            $errors[] = "Registro duplicado para run {$row['run_persona']} + tipo {$row['tipo_persona']}";
            logAction($logRows, $lineNum, 'run_persona', $row['run_persona'],
                      'ELIMINAR: duplicado run+tipo_persona', '');
        } else {
            $runsSeen[$dupKey] = true;
        }

        // --- nombre_completo ---
        if (trim($row['nombre_completo']) === '') {
            $errors[] = "nombre_completo vacío (campo obligatorio)";
            logAction($logRows, $lineNum, 'nombre_completo', '', 'ELIMINAR: campo obligatorio vacío', '');
        }

        // --- email ---
        [$email, $emailNote] = validateEmail($row['email']);
        if ($emailNote) {
            logAction($logRows, $lineNum, 'email', $row['email'], $emailNote, $email ?? '');
        }
        if ($email === null) {
            $row['email'] = '';  // clear invalid email (nullable)
        } else {
            $row['email'] = $email;
        }

        // --- telefono_celular ---
        [$tel, $telNote] = validatePhone($row['telefono_celular']);
        if ($telNote) {
            logAction($logRows, $lineNum, 'telefono_celular', $row['telefono_celular'], $telNote, $tel);
        }
        $row['telefono_celular'] = $tel;

        // --- telefono_alternativo (strip .0 artefact) ---
        [$telAlt, $telAltNote] = validatePhone($row['telefono_alternativo']);
        if ($telAltNote) {
            logAction($logRows, $lineNum, 'telefono_alternativo', $row['telefono_alternativo'], $telAltNote, $telAlt);
        }
        $row['telefono_alternativo'] = $telAlt;

        // --- region_nombre ---
        $regNorm = normaliseRegion($row['region_nombre']);
        if ($regNorm !== $row['region_nombre']) {
            logAction($logRows, $lineNum, 'region_nombre', $row['region_nombre'],
                      "Nombre de región normalizado", $regNorm);
            $row['region_nombre'] = $regNorm;
        }

        // --- region_codigo: must be 1-16 ---
        $rc = (int)$row['region_codigo'];
        if ($rc < 1 || $rc > 16) {
            $errors[] = "region_codigo '{$row['region_codigo']}' fuera de rango (1-16)";
            logAction($logRows, $lineNum, 'region_codigo', $row['region_codigo'],
                      'ELIMINAR: region_codigo fuera de rango', '');
        }

        // --- tipo_persona ---
        $validTipos = ['socio_titular', 'beneficiario', 'adicional', 'invitado', 'administrativo'];
        if (!in_array($row['tipo_persona'], $validTipos)) {
            $errors[] = "tipo_persona '{$row['tipo_persona']}' inválido";
            logAction($logRows, $lineNum, 'tipo_persona', $row['tipo_persona'],
                      'ELIMINAR: tipo_persona no reconocido', '');
        }

        // --- parentesco ---
        [$parentesco, $pNote] = normaliseParentesco($row['parentesco'], $row['tipo_persona']);
        if ($pNote) {
            logAction($logRows, $lineNum, 'parentesco', $row['parentesco'], $pNote, $parentesco ?? '');
        }
        if ($parentesco === null) {
            $errors[] = "parentesco '{$row['parentesco']}' inválido para beneficiario";
        } else {
            $row['parentesco'] = $parentesco;
        }

        // --- run_socio_titular: validate if present ---
        if ($row['run_socio_titular'] !== '') {
            $titRun = validateRun($row['run_socio_titular']);
            if ($titRun === false) {
                logAction($logRows, $lineNum, 'run_socio_titular', $row['run_socio_titular'],
                          'CORRECCIÓN: run_socio_titular inválido, campo limpiado', '');
                $row['run_socio_titular'] = '';
            } elseif ($titRun !== $row['run_socio_titular']) {
                logAction($logRows, $lineNum, 'run_socio_titular', $row['run_socio_titular'],
                          'CORRECCIÓN: run_socio_titular normalizado', $titRun);
                $row['run_socio_titular'] = $titRun;
            }
        }

        // --- fecha_nacimiento ---
        [$fnac, $fnacNote] = normaliseDate($row['fecha_nacimiento']);
        if ($fnacNote) {
            logAction($logRows, $lineNum, 'fecha_nacimiento', $row['fecha_nacimiento'], $fnacNote, $fnac ?? '');
        }
        $row['fecha_nacimiento'] = ($fnac === null) ? '' : $fnac;

        // --- fecha_inicio_membresia ---
        [$fini, $finiNote] = normaliseDate($row['fecha_inicio_membresia']);
        if ($finiNote) {
            logAction($logRows, $lineNum, 'fecha_inicio_membresia',
                      $row['fecha_inicio_membresia'], $finiNote, $fini ?? '');
        }
        $row['fecha_inicio_membresia'] = ($fini === null) ? '' : $fini;

        // --- fecha_fin_membresia ---
        [$ffin, $ffinNote] = normaliseDate($row['fecha_fin_membresia']);
        if ($ffinNote) {
            logAction($logRows, $lineNum, 'fecha_fin_membresia',
                      $row['fecha_fin_membresia'], $ffinNote, $ffin ?? '');
        }
        $row['fecha_fin_membresia'] = ($ffin === null) ? '' : $ffin;

        // --- es_usuario_sistema ---
        $eu = strtoupper(trim($row['es_usuario_sistema']));
        if (!in_array($eu, ['SI', 'NO'])) {
            logAction($logRows, $lineNum, 'es_usuario_sistema', $row['es_usuario_sistema'],
                      "Valor inválido; reemplazado por NO", 'NO');
            $eu = 'NO';
        }
        $row['es_usuario_sistema'] = $eu;

        // --- tipo_usuario: must be admin/administrativo/socio or empty ---
        $validTU = ['admin', 'administrativo', 'socio', ''];
        $tu = strtolower(trim($row['tipo_usuario']));
        if ($eu === 'SI' && !in_array($tu, $validTU)) {
            logAction($logRows, $lineNum, 'tipo_usuario', $row['tipo_usuario'],
                      "tipo_usuario inválido para usuario del sistema; limpiado", '');
            $row['tipo_usuario'] = '';
        }

        // --- sucursal_base_nombre: mandatory ---
        if (trim($row['sucursal_base_nombre']) === '') {
            $errors[] = "sucursal_base_nombre vacío (campo obligatorio)";
            logAction($logRows, $lineNum, 'sucursal_base_nombre', '',
                      'ELIMINAR: campo obligatorio vacío', '');
        }

        if (!empty($errors)) {
            $errRows[] = array_values($row);
        } else {
            $okRows[] = array_values($row);
        }
    }

    writeCsv(OUTPUT_DIR . 'personas_sociosOK.csv',  $header, $okRows);
    writeCsv(OUTPUT_DIR . 'personas_sociosERR.csv', $header, $errRows);
    writeCsv(OUTPUT_DIR . 'personas_sociosLOG.csv',
             ['linea','campo','valor_original','accion','valor_nuevo'], $logRows);

    echo "personas_socios: " . count($okRows) . " OK, " . count($errRows) . " ERR\n";
}

// ============================================================
// PROCESS 2: sucursales_lugares.csv
// ============================================================
function procesarSucursales(): void {
    $file   = INPUT_DIR . 'sucursales_lugares.csv';
    $rows   = readCsv($file);
    $header = array_keys($rows[0]);

    $okRows  = [];
    $errRows = [];
    $logRows = [['linea', 'campo', 'valor_original', 'accion', 'valor_nuevo']];

    foreach ($rows as $lineIdx => $row) {
        $lineNum = $lineIdx + 2;
        $errors  = [];

        // --- sucursal_nombre: mandatory ---
        if (trim($row['sucursal_nombre']) === '') {
            $errors[] = "sucursal_nombre vacío";
            logAction($logRows, $lineNum, 'sucursal_nombre', '', 'ELIMINAR: campo obligatorio', '');
        }

        // --- lugar_nombre: mandatory ---
        if (trim($row['lugar_nombre']) === '') {
            $errors[] = "lugar_nombre vacío";
            logAction($logRows, $lineNum, 'lugar_nombre', '', 'ELIMINAR: campo obligatorio', '');
        }

        // --- capacidad_personas: must be positive integer ---
        $cap = trim($row['capacidad_personas']);
        if (!ctype_digit($cap) || (int)$cap <= 0) {
            $errors[] = "capacidad_personas '$cap' inválida";
            logAction($logRows, $lineNum, 'capacidad_personas', $cap,
                      'ELIMINAR: capacidad debe ser entero positivo', '');
        }

        // --- precio: may be text number ---
        [$precio, $precioNote] = normalisePrecio($row['precio']);
        if ($precioNote) {
            logAction($logRows, $lineNum, 'precio', $row['precio'], $precioNote, $precio ?? '');
        }
        if ($precio === null) {
            // precio is mandatory per spec
            $errors[] = "precio '{$row['precio']}' irreparable";
        } else {
            $row['precio'] = $precio;
        }

        // --- descuento_socio_evento: 0–100 decimal ---
        $desc = trim($row['descuento_socio_evento']);
        if ($desc !== '') {
            $descFloat = filter_var($desc, FILTER_VALIDATE_FLOAT);
            if ($descFloat === false || $descFloat < 0 || $descFloat > 100) {
                logAction($logRows, $lineNum, 'descuento_socio_evento', $desc,
                          'CORRECCIÓN: descuento inválido, limpiado', '');
                $row['descuento_socio_evento'] = '';
            }
        }

        // --- tipo_precio ---
        $tp = strtolower(trim($row['tipo_precio']));
        $validTP = ['hora', 'dia', 'mesa_hora', 'noche', ''];
        if (!in_array($tp, $validTP)) {
            logAction($logRows, $lineNum, 'tipo_precio', $row['tipo_precio'],
                      "tipo_precio '$tp' no reconocido, limpiado", '');
            $row['tipo_precio'] = '';
        }

        // --- fecha_inicio_vigencia ---
        [$fini, $finiNote] = normaliseDate($row['fecha_inicio_vigencia']);
        if ($finiNote) {
            logAction($logRows, $lineNum, 'fecha_inicio_vigencia',
                      $row['fecha_inicio_vigencia'], $finiNote, $fini ?? '');
        }
        $row['fecha_inicio_vigencia'] = ($fini === null) ? '' : $fini;

        // --- fecha_fin_vigencia ---
        [$ffin, $ffinNote] = normaliseDate($row['fecha_fin_vigencia']);
        if ($ffinNote) {
            logAction($logRows, $lineNum, 'fecha_fin_vigencia',
                      $row['fecha_fin_vigencia'], $ffinNote, $ffin ?? '');
        }
        $row['fecha_fin_vigencia'] = ($ffin === null) ? '' : $ffin;

        if (!empty($errors)) {
            $errRows[] = array_values($row);
        } else {
            $okRows[] = array_values($row);
        }
    }

    writeCsv(OUTPUT_DIR . 'sucursales_lugaresOK.csv',  $header, $okRows);
    writeCsv(OUTPUT_DIR . 'sucursales_lugaresERR.csv', $header, $errRows);
    writeCsv(OUTPUT_DIR . 'sucursales_lugaresLOG.csv',
             ['linea','campo','valor_original','accion','valor_nuevo'], $logRows);

    echo "sucursales_lugares: " . count($okRows) . " OK, " . count($errRows) . " ERR\n";
}

// ============================================================
// PROCESS 3: reservas_arriendos.csv
// ============================================================
function procesarReservas(): void {
    $file   = INPUT_DIR . 'reservas_arriendos.csv';
    $rows   = readCsv($file);
    $header = array_keys($rows[0]);

    $okRows  = [];
    $errRows = [];
    $logRows = [['linea', 'campo', 'valor_original', 'accion', 'valor_nuevo']];

    $counter = 1;

    foreach ($rows as $lineIdx => $row) {
        $lineNum = $lineIdx + 2;
        $errors  = [];

        // --- codigo_reserva: generate if missing ---
        if (trim($row['codigo_reserva']) === '') {
            $codigo = sprintf('RES%05d', $counter++);
            logAction($logRows, $lineNum, 'codigo_reserva', '',
                      'ASIGNACIÓN: codigo_reserva generado automáticamente', $codigo);
            $row['codigo_reserva'] = $codigo;
        } else {
            $counter++;
        }

        // --- run_reservante: validate ---
        $run = validateRun($row['run_reservante']);
        if ($run === false) {
            $errors[] = "run_reservante '{$row['run_reservante']}' inválido";
            logAction($logRows, $lineNum, 'run_reservante', $row['run_reservante'],
                      'ELIMINAR: run_reservante inválido', '');
        } else {
            if ($run !== $row['run_reservante']) {
                logAction($logRows, $lineNum, 'run_reservante', $row['run_reservante'],
                          'CORRECCIÓN: normalizado', $run);
            }
            $row['run_reservante'] = $run;
        }

        // --- nombre_reservante: mandatory ---
        if (trim($row['nombre_reservante']) === '') {
            $errors[] = "nombre_reservante vacío";
            logAction($logRows, $lineNum, 'nombre_reservante', '', 'ELIMINAR: obligatorio', '');
        }

        // --- es_socio ---
        $es = strtoupper(trim($row['es_socio']));
        if (!in_array($es, ['SI', 'NO'])) {
            logAction($logRows, $lineNum, 'es_socio', $row['es_socio'],
                      'CORRECCIÓN: valor inválido, reemplazado por NO', 'NO');
            $es = 'NO';
        }
        $row['es_socio'] = $es;

        // --- lugar_nombre / sucursal_nombre: mandatory ---
        if (trim($row['lugar_nombre']) === '') {
            $errors[] = "lugar_nombre vacío";
            logAction($logRows, $lineNum, 'lugar_nombre', '', 'ELIMINAR: obligatorio', '');
        }
        if (trim($row['sucursal_nombre']) === '') {
            $errors[] = "sucursal_nombre vacío";
            logAction($logRows, $lineNum, 'sucursal_nombre', '', 'ELIMINAR: obligatorio', '');
        }

        // --- estado_reserva ---
        $validEstados = ['reservada', 'ejecutada', 'cancelada'];
        $estado = strtolower(trim($row['estado_reserva']));
        if (!in_array($estado, $validEstados)) {
            $errors[] = "estado_reserva '{$row['estado_reserva']}' inválido";
            logAction($logRows, $lineNum, 'estado_reserva', $row['estado_reserva'],
                      'ELIMINAR: estado no reconocido', '');
        } else {
            $row['estado_reserva'] = $estado;
        }

        // --- fecha_reserva ---
        [$fr, $frNote] = normaliseDate($row['fecha_reserva']);
        if ($frNote) logAction($logRows, $lineNum, 'fecha_reserva', $row['fecha_reserva'], $frNote, $fr ?? '');
        if ($fr === null) {
            $errors[] = "fecha_reserva irreparable";
        } else {
            $row['fecha_reserva'] = $fr;
        }

        // --- fecha_inicio (datetime) ---
        [$fi, $fiNote] = normaliseDatetime($row['fecha_inicio']);
        if ($fiNote) logAction($logRows, $lineNum, 'fecha_inicio', $row['fecha_inicio'], $fiNote, $fi ?? '');
        if ($fi === null) {
            $errors[] = "fecha_inicio irreparable";
        } else {
            $row['fecha_inicio'] = $fi;
        }

        // --- fecha_fin (datetime) ---
        [$ff, $ffNote] = normaliseDatetime($row['fecha_fin']);
        if ($ffNote) logAction($logRows, $lineNum, 'fecha_fin', $row['fecha_fin'], $ffNote, $ff ?? '');
        if ($ff === null) {
            $errors[] = "fecha_fin irreparable";
        } else {
            $row['fecha_fin'] = $ff;
        }

        // --- monto_total: mandatory positive integer ---
        $monto = trim($row['monto_total']);
        if (!ctype_digit($monto) || (int)$monto < 0) {
            $errors[] = "monto_total '$monto' inválido";
            logAction($logRows, $lineNum, 'monto_total', $monto, 'ELIMINAR: monto inválido', '');
        }

        // --- monto_pagado: nullable, clean ---
        $mp = trim($row['monto_pagado']);
        if ($mp !== '' && !ctype_digit($mp)) {
            logAction($logRows, $lineNum, 'monto_pagado', $mp,
                      'CORRECCIÓN: monto_pagado no numérico, limpiado', '');
            $row['monto_pagado'] = '';
        }

        // --- fecha_pago: nullable ---
        [$fp, $fpNote] = normaliseDate($row['fecha_pago']);
        if ($fpNote) logAction($logRows, $lineNum, 'fecha_pago', $row['fecha_pago'], $fpNote, $fp ?? '');
        $row['fecha_pago'] = ($fp === null) ? '' : $fp;

        if (!empty($errors)) {
            $errRows[] = array_values($row);
        } else {
            $okRows[] = array_values($row);
        }
    }

    writeCsv(OUTPUT_DIR . 'reservas_arriendosOK.csv',  $header, $okRows);
    writeCsv(OUTPUT_DIR . 'reservas_arriendosERR.csv', $header, $errRows);
    writeCsv(OUTPUT_DIR . 'reservas_arriendosLOG.csv',
             ['linea','campo','valor_original','accion','valor_nuevo'], $logRows);

    echo "reservas_arriendos: " . count($okRows) . " OK, " . count($errRows) . " ERR\n";
}

// ============================================================
// PROCESS 4: eventos.csv
// ============================================================
function procesarEventos(): void {
    $file   = INPUT_DIR . 'eventos.csv';
    $rows   = readCsv($file);
    $header = array_keys($rows[0]);

    $okRows  = [];
    $errRows = [];
    $logRows = [['linea', 'campo', 'valor_original', 'accion', 'valor_nuevo']];

    $eventIdsSeen = [];

    foreach ($rows as $lineIdx => $row) {
        $lineNum = $lineIdx + 2;
        $errors  = [];

        // --- evento_id → codigo_evento ---
        // The schema uses codigo_evento (varchar 20), evento_id is numeric from CSV
        $eid = trim($row['evento_id'] ?? $row[array_key_first($row)] ?? '');
        $codigoEvento = 'EVT' . str_pad($eid, 5, '0', STR_PAD_LEFT);
        if (isset($eventIdsSeen[$codigoEvento])) {
            $errors[] = "evento_id '$eid' duplicado";
            logAction($logRows, $lineNum, 'evento_id', $eid, 'ELIMINAR: evento_id duplicado', '');
        }
        $eventIdsSeen[$codigoEvento] = true;
        $row['evento_id'] = $codigoEvento; // will be mapped to codigo_evento in SQL

        // --- nombre_evento: mandatory ---
        if (trim($row['nombre_evento']) === '') {
            $errors[] = "nombre_evento vacío";
            logAction($logRows, $lineNum, 'nombre_evento', '', 'ELIMINAR: obligatorio', '');
        }

        // --- fecha_evento ---
        $fechaField = isset($row['fecha_evento']) ? 'fecha_evento' : 'fecha_contratación';
        [$fe, $feNote] = normaliseDate($row['fecha_evento']);
        if ($feNote) logAction($logRows, $lineNum, 'fecha_evento', $row['fecha_evento'], $feNote, $fe ?? '');
        if ($fe === null) {
            $errors[] = "fecha_evento irreparable";
        } else {
            $row['fecha_evento'] = $fe;
        }

        // --- fecha_contratación (optional, may not exist in schema directly) ---
        if (isset($row['fecha_contratación'])) {
            [$fc, $fcNote] = normaliseDate($row['fecha_contratación']);
            if ($fcNote) logAction($logRows, $lineNum, 'fecha_contratación', $row['fecha_contratación'], $fcNote, $fc ?? '');
            $row['fecha_contratación'] = ($fc === null) ? '' : $fc;
        }

        // --- tipo_cliente: normalise empresa-institucion → empresa ---
        $tc = strtolower(trim($row['tipo_cliente']));
        if ($tc === 'empresa-institucion') {
            logAction($logRows, $lineNum, 'tipo_cliente', $row['tipo_cliente'],
                      "CORRECCIÓN: 'empresa-institucion' normalizado a 'empresa'", 'empresa');
            $tc = 'empresa';
        }
        $validTC = ['socio', 'persona', 'empresa'];
        if (!in_array($tc, $validTC)) {
            $errors[] = "tipo_cliente '$tc' inválido";
            logAction($logRows, $lineNum, 'tipo_cliente', $row['tipo_cliente'], 'ELIMINAR: tipo inválido', '');
        }
        $row['tipo_cliente'] = $tc;

        // --- run_cliente: validate (person RUN or empresa RUT) ---
        $runCliente = trim($row['run_cliente']);
        $validatedRun = validateRun($runCliente);
        if ($validatedRun === false) {
            $errors[] = "run_cliente '$runCliente' inválido";
            logAction($logRows, $lineNum, 'run_cliente', $runCliente, 'ELIMINAR: RUN/RUT inválido', '');
        } else {
            if ($validatedRun !== $runCliente) {
                logAction($logRows, $lineNum, 'run_cliente', $runCliente,
                          'CORRECCIÓN: RUT normalizado (puntos eliminados)', $validatedRun);
            }
            $row['run_cliente'] = $validatedRun;
        }

        // --- rut_contacto_empresa: validate if present ---
        if (trim($row['rut_contacto_empresa']) !== '') {
            $rc = validateRun($row['rut_contacto_empresa']);
            if ($rc === false) {
                logAction($logRows, $lineNum, 'rut_contacto_empresa', $row['rut_contacto_empresa'],
                          'CORRECCIÓN: RUT contacto inválido, limpiado', '');
                $row['rut_contacto_empresa'] = '';
            } elseif ($rc !== $row['rut_contacto_empresa']) {
                logAction($logRows, $lineNum, 'rut_contacto_empresa', $row['rut_contacto_empresa'],
                          'CORRECCIÓN: RUT contacto normalizado', $rc);
                $row['rut_contacto_empresa'] = $rc;
            }
        }

        // --- monto_total_evento: mandatory positive integer ---
        $monto = trim($row['monto_total_evento']);
        if (!ctype_digit($monto) || (int)$monto <= 0) {
            $errors[] = "monto_total_evento '$monto' inválido";
            logAction($logRows, $lineNum, 'monto_total_evento', $monto, 'ELIMINAR: monto inválido', '');
        }

        // --- monto_pagado_reserva / monto_pagado_ejecucion: nullable integers ---
        foreach (['monto_pagado_reserva', 'monto_pagado_ejecucion'] as $montoField) {
            $mv = trim($row[$montoField]);
            if ($mv !== '' && !ctype_digit($mv)) {
                logAction($logRows, $lineNum, $montoField, $mv,
                          'CORRECCIÓN: monto no numérico, limpiado', '');
                $row[$montoField] = '';
            }
        }

        // --- lugar_nombre / sucursal_nombre: mandatory ---
        foreach (['lugar_nombre', 'sucursal_nombre'] as $f) {
            if (trim($row[$f]) === '') {
                $errors[] = "$f vacío";
                logAction($logRows, $lineNum, $f, '', 'ELIMINAR: campo obligatorio', '');
            }
        }

        if (!empty($errors)) {
            $errRows[] = array_values($row);
        } else {
            $okRows[] = array_values($row);
        }
    }

    writeCsv(OUTPUT_DIR . 'eventosOK.csv',  $header, $okRows);
    writeCsv(OUTPUT_DIR . 'eventosERR.csv', $header, $errRows);
    writeCsv(OUTPUT_DIR . 'eventosLOG.csv',
             ['linea','campo','valor_original','accion','valor_nuevo'], $logRows);

    echo "eventos: " . count($okRows) . " OK, " . count($errRows) . " ERR\n";
}

// ============================================================
// PROCESS 5: pagos_membresias.csv
// ============================================================
function procesarPagos(): void {
    $file   = INPUT_DIR . 'pagos_membresias.csv';
    $rows   = readCsv($file);
    $header = array_keys($rows[0]);

    $okRows  = [];
    $errRows = [];
    $logRows = [['linea', 'campo', 'valor_original', 'accion', 'valor_nuevo']];

    foreach ($rows as $lineIdx => $row) {
        $lineNum = $lineIdx + 2;
        $errors  = [];

        // --- run_socio_titular ---
        $run = validateRun($row['run_socio_titular']);
        if ($run === false) {
            $errors[] = "run_socio_titular '{$row['run_socio_titular']}' inválido";
            logAction($logRows, $lineNum, 'run_socio_titular', $row['run_socio_titular'],
                      'ELIMINAR: RUN inválido', '');
        } else {
            if ($run !== $row['run_socio_titular']) {
                logAction($logRows, $lineNum, 'run_socio_titular', $row['run_socio_titular'],
                          'CORRECCIÓN: normalizado', $run);
            }
            $row['run_socio_titular'] = $run;
        }

        // --- anio_membresia: 4-digit year ---
        $anio = trim($row['anio_membresia']);
        if (!preg_match('/^\d{4}$/', $anio) || (int)$anio < 2000 || (int)$anio > 2100) {
            $errors[] = "anio_membresia '$anio' inválido";
            logAction($logRows, $lineNum, 'anio_membresia', $anio, 'ELIMINAR: año inválido', '');
        }

        // --- mes_cuota: 1–12 ---
        $mes = trim($row['mes_cuota']);
        if (!ctype_digit($mes) || (int)$mes < 1 || (int)$mes > 12) {
            $errors[] = "mes_cuota '$mes' inválido";
            logAction($logRows, $lineNum, 'mes_cuota', $mes, 'ELIMINAR: mes fuera de rango 1-12', '');
        }

        // --- fecha_vencimiento ---
        [$fv, $fvNote] = normaliseDate($row['fecha_vencimiento']);
        if ($fvNote) logAction($logRows, $lineNum, 'fecha_vencimiento', $row['fecha_vencimiento'], $fvNote, $fv ?? '');
        if ($fv === null) {
            $errors[] = "fecha_vencimiento irreparable";
        } else {
            $row['fecha_vencimiento'] = $fv;
        }

        // --- monto_membresia / monto_total: mandatory positive integers ---
        foreach (['monto_membresia', 'monto_total'] as $mf) {
            $mv = trim($row[$mf]);
            if (!ctype_digit($mv) || (int)$mv <= 0) {
                $errors[] = "$mf '$mv' inválido";
                logAction($logRows, $lineNum, $mf, $mv, 'ELIMINAR: monto inválido', '');
            }
        }

        // --- monto_adicionales: nullable integer ---
        $ma = trim($row['monto_adicionales']);
        if ($ma !== '' && !ctype_digit($ma)) {
            logAction($logRows, $lineNum, 'monto_adicionales', $ma,
                      'CORRECCIÓN: monto no numérico, reemplazado por 0', '0');
            $row['monto_adicionales'] = '0';
        }

        // --- estado_pago ---
        $ep = strtolower(trim($row['estado_pago']));
        if (!in_array($ep, ['pagado', 'atrasado', 'pendiente'])) {
            $errors[] = "estado_pago '$ep' inválido";
            logAction($logRows, $lineNum, 'estado_pago', $row['estado_pago'],
                      'ELIMINAR: estado no reconocido', '');
        } else {
            $row['estado_pago'] = $ep;
        }

        // --- fecha_pago: nullable ---
        [$fp, $fpNote] = normaliseDate($row['fecha_pago']);
        if ($fpNote) logAction($logRows, $lineNum, 'fecha_pago', $row['fecha_pago'], $fpNote, $fp ?? '');
        $row['fecha_pago'] = ($fp === null) ? '' : $fp;

        if (!empty($errors)) {
            $errRows[] = array_values($row);
        } else {
            $okRows[] = array_values($row);
        }
    }

    writeCsv(OUTPUT_DIR . 'pagos_membresiasOK.csv',  $header, $okRows);
    writeCsv(OUTPUT_DIR . 'pagos_membresiasERR.csv', $header, $errRows);
    writeCsv(OUTPUT_DIR . 'pagos_membresiasLOG.csv',
             ['linea','campo','valor_original','accion','valor_nuevo'], $logRows);

    echo "pagos_membresias: " . count($okRows) . " OK, " . count($errRows) . " ERR\n";
}

// ============================================================
// PROCESS 6: cargos_administrativos.csv
// ============================================================
function procesarCargos(): void {
    $file   = INPUT_DIR . 'cargos_administrativos.csv';
    $rows   = readCsv($file);
    $header = array_keys($rows[0]);

    $okRows  = [];
    $errRows = [];
    $logRows = [['linea', 'campo', 'valor_original', 'accion', 'valor_nuevo']];

    foreach ($rows as $lineIdx => $row) {
        $lineNum = $lineIdx + 2;
        $errors  = [];

        // --- run_persona ---
        $run = validateRun($row['run_persona']);
        if ($run === false) {
            $errors[] = "run_persona '{$row['run_persona']}' inválido";
            logAction($logRows, $lineNum, 'run_persona', $row['run_persona'],
                      'ELIMINAR: RUN inválido', '');
        } else {
            if ($run !== $row['run_persona']) {
                logAction($logRows, $lineNum, 'run_persona', $row['run_persona'],
                          'CORRECCIÓN: normalizado', $run);
            }
            $row['run_persona'] = $run;
        }

        // --- sucursal_nombre: mandatory ---
        if (trim($row['sucursal_nombre']) === '') {
            $errors[] = "sucursal_nombre vacío";
            logAction($logRows, $lineNum, 'sucursal_nombre', '', 'ELIMINAR: obligatorio', '');
        }

        // --- nombre_cargo: mandatory ---
        if (trim($row['nombre_cargo']) === '') {
            $errors[] = "nombre_cargo vacío";
            logAction($logRows, $lineNum, 'nombre_cargo', '', 'ELIMINAR: obligatorio', '');
        }

        // --- fecha_inicio_cargo: mandatory ---
        [$fi, $fiNote] = normaliseDate($row['fecha_inicio_cargo']);
        if ($fiNote) logAction($logRows, $lineNum, 'fecha_inicio_cargo',
                               $row['fecha_inicio_cargo'], $fiNote, $fi ?? '');
        if ($fi === null || $fi === '') {
            $errors[] = "fecha_inicio_cargo irreparable o vacía";
            logAction($logRows, $lineNum, 'fecha_inicio_cargo', $row['fecha_inicio_cargo'],
                      'ELIMINAR: fecha obligatoria irreparable', '');
        } else {
            $row['fecha_inicio_cargo'] = $fi;
        }

        // --- fecha_termino_cargo: nullable ---
        [$ft, $ftNote] = normaliseDate($row['fecha_termino_cargo']);
        if ($ftNote) logAction($logRows, $lineNum, 'fecha_termino_cargo',
                               $row['fecha_termino_cargo'], $ftNote, $ft ?? '');
        $row['fecha_termino_cargo'] = ($ft === null) ? '' : $ft;

        if (!empty($errors)) {
            $errRows[] = array_values($row);
        } else {
            $okRows[] = array_values($row);
        }
    }

    writeCsv(OUTPUT_DIR . 'cargos_administrativosOK.csv',  $header, $okRows);
    writeCsv(OUTPUT_DIR . 'cargos_administrativosERR.csv', $header, $errRows);
    writeCsv(OUTPUT_DIR . 'cargos_administrativosLOG.csv',
             ['linea','campo','valor_original','accion','valor_nuevo'], $logRows);

    echo "cargos_administrativos: " . count($okRows) . " OK, " . count($errRows) . " ERR\n";
}

// ============================================================
// PROCESS 7: regiones_comunas.csv
// ============================================================
function procesarRegiones(): void {
    $file   = INPUT_DIR . 'regiones_comunas.csv';
    $rows   = readCsv($file);
    $header = array_keys($rows[0]);

    $okRows  = [];
    $errRows = [];
    $logRows = [['linea', 'campo', 'valor_original', 'accion', 'valor_nuevo']];

    $seen = [];

    foreach ($rows as $lineIdx => $row) {
        $lineNum = $lineIdx + 2;
        $errors  = [];

        // Get values by position (headers have accents that may vary)
        $vals = array_values($row);
        if (count($vals) < 4) {
            $errors[] = "Fila con columnas insuficientes";
            $errRows[] = $vals;
            logAction($logRows, $lineNum, '*', implode(';', $vals), 'ELIMINAR: columnas insuficientes', '');
            continue;
        }
        $codigoComuna = trim($vals[0]);
        $nombreComuna = trim($vals[1]);
        $codigoRegion = trim($vals[2]);
        $nombreRegion = trim($vals[3]);

        // Remap headers to standard names
        $row = [
            'codigo_comuna' => $codigoComuna,
            'nombre_comuna' => $nombreComuna,
            'codigo_region' => $codigoRegion,
            'nombre_region' => $nombreRegion,
        ];

        // --- codigo_comuna: must be integer ---
        if (!ctype_digit($codigoComuna)) {
            $errors[] = "codigo_comuna '$codigoComuna' inválido";
            logAction($logRows, $lineNum, 'codigo_comuna', $codigoComuna, 'ELIMINAR: no numérico', '');
        }

        // --- Duplicates ---
        if (isset($seen[$codigoComuna])) {
            $errors[] = "codigo_comuna '$codigoComuna' duplicado";
            logAction($logRows, $lineNum, 'codigo_comuna', $codigoComuna, 'ELIMINAR: duplicado', '');
        } else {
            $seen[$codigoComuna] = true;
        }

        // --- codigo_region: 1–16 ---
        $cr = (int)$codigoRegion;
        if ($cr < 1 || $cr > 16) {
            $errors[] = "codigo_region '$codigoRegion' fuera de rango";
            logAction($logRows, $lineNum, 'codigo_region', $codigoRegion,
                      'ELIMINAR: fuera de rango 1-16', '');
        }

        // --- nombre_region: normalise ---
        $nrNorm = normaliseRegion($nombreRegion);
        if ($nrNorm !== $nombreRegion) {
            logAction($logRows, $lineNum, 'nombre_region', $nombreRegion,
                      'CORRECCIÓN: normalizado', $nrNorm);
            $row['nombre_region'] = $nrNorm;
        }

        if (!empty($errors)) {
            $errRows[] = array_values($row);
        } else {
            $okRows[] = array_values($row);
        }
    }

    $stdHeader = ['codigo_comuna', 'nombre_comuna', 'codigo_region', 'nombre_region'];
    writeCsv(OUTPUT_DIR . 'regiones_comunasOK.csv',  $stdHeader, $okRows);
    writeCsv(OUTPUT_DIR . 'regiones_comunasERR.csv', $stdHeader, $errRows);
    writeCsv(OUTPUT_DIR . 'regiones_comunasLOG.csv',
             ['linea','campo','valor_original','accion','valor_nuevo'], $logRows);

    echo "regiones_comunas: " . count($okRows) . " OK, " . count($errRows) . " ERR\n";
}

// ============================================================
// MAIN
// ============================================================

echo "=== DCColo Data Cleaning - main.php ===\n";
echo "Input  dir: " . INPUT_DIR  . "\n";
echo "Output dir: " . OUTPUT_DIR . "\n\n";

procesarPersonas();
procesarSucursales();
procesarReservas();
procesarEventos();
procesarPagos();
procesarCargos();
procesarRegiones();

echo "\nDone. Check *OK.csv, *ERR.csv, *LOG.csv files.\n";
