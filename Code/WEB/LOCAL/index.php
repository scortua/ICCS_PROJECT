<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invernadero - Sistema de Monitoreo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { font-size: 2em; color: black; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .connection-status { font-size: 1.2em; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .success { color: green; }
        .error { color: red; }
        
        /* Estilos para centrar las tablas con efecto de profundidad */
        .table-container {
            display: flex;
            justify-content: center;
            width: 100%;
            margin-bottom: 40px;
        }
        
        table { 
            width: 80%; 
            border-collapse: separate;
            border-spacing: 0;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2); /* Efecto de profundidad */
        }
        
        th { 
            color: white; 
            text-align: left; 
            padding: 12px; 
            font-weight: bold;
        }
        
        td { 
            border: none;
            border-bottom: 1px solid rgba(0,0,0,0.1);
            padding: 12px; 
        }
        
        tr:last-child td {
            border-bottom: none;
        }
        
        tr:nth-child(even) { 
            background-color: rgba(0,0,0,0.05); 
        }
        
        /* Estilos para diferentes colores de tablas */
        .tabla-verde th { background-color: #4CAF50; }
        .tabla-azul th { background-color: #2196F3; }
        .tabla-naranja th { background-color: #FF9800; }
        .tabla-roja th { background-color: #F44336; }
        .tabla-morada th { background-color: #9C27B0; }
        
        /* Centrar el título del sensor con estilo */
        .sensor-title { 
            font-size: 1.5em; 
            font-weight: bold;
            padding: 5px 15px;
            margin: 20px auto 10px auto;
            border-radius: 5px;
            display: inline-block;
            text-align: center;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        
        /* Colores para los títulos de sensores */
        .titulo-verde { 
            color: #4CAF50; 
            border-bottom: 3px solid #4CAF50;
        }
        .titulo-azul { 
            color: #2196F3; 
            border-bottom: 3px solid #2196F3;
        }
        .titulo-naranja { 
            color: #FF9800; 
            border-bottom: 3px solid #FF9800;
        }
        .titulo-roja { 
            color: #F44336; 
            border-bottom: 3px solid #F44336;
        }
        .titulo-morada { 
            color: #9C27B0; 
            border-bottom: 3px solid #9C27B0;
        }
        
        /* Para centrar los títulos de los sensores */
        .sensor-heading {
            text-align: center;
            margin-top: 30px;
        }

        /* Estilos para los cuadros */
        .cuadros-container {
            display: flex;
            flex-wrap: wrap;
            justify-content: center;
            gap: 20px;
        }
        .cuadro {
            width: calc(33.333% - 20px);
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            border-radius: 8px;
            padding: 20px;
            text-align: center;
        }
        .cuadro-title {
            font-size: 1.2em;
            font-weight: bold;
            margin-bottom: 10px;
        }
    </style>
</head>
<body>
    <div class="header">🪴Datos del Invernadero</div>

    <?php
    $MyUsername = "RPI4";
    $MyPassword = "raspberry4";
    $MyHostname = "localhost";
    $MyDatabase = "Invernadero";

    // Create connection
    $conn = new mysqli($MyHostname, $MyUsername, $MyPassword, $MyDatabase);

    // Check connection
    if ($conn->connect_error) {
        echo '<div class="connection-status error">❌ Connection failed: ' . $conn->connect_error . '</div>';
    } else {
        echo '<div class="connection-status success">✅ Connected successfully</div>';
        
        // Array de colores disponibles
        $colores = array(
            'verde' => 'tabla-verde',
            'azul' => 'tabla-azul',
            'naranja' => 'tabla-naranja',
            'rojo' => 'tabla-roja',
            'morado' => 'tabla-morada'
        );
        
        // Colores asignados a cada sensor (esto puedes modificarlo según tus preferencias)
        $coloresSensores = array(
            'DHT22' => 'verde',
            'MQ_135' => 'azul'
            // Puedes añadir más sensores aquí
        );

        // Títulos de las cajas
        $titulosCajas = array('Temperatura', 'Humedad', 'CO2', 'Nitrógeno', 'Cuadro 5', 'Cuadro 6');

        // Consultas SQL para obtener los valores máximos, mínimos y promedios
        $queries = array(
            'Temperatura' => "SELECT MAX(temperatura) as max, MIN(temperatura) as min, AVG(temperatura) as avg FROM DHT22",
            'Humedad' => "SELECT MAX(humedad) as max, MIN(humedad) as min, AVG(humedad) as avg FROM DHT22",
            'CO2' => "SELECT MAX(co2) as max, MIN(co2) as min, AVG(co2) as avg FROM MQ_135",
            'Nitrógeno' => "SELECT MAX(N) as max, MIN(N) as min, AVG(N) as avg FROM MQ_135",
            'Cuadro 5' => "SELECT 100 as max, 50 as min, 75 as avg", // Ejemplo estático
            'Cuadro 6' => "SELECT 200 as max, 100 as min, 150 as avg" // Ejemplo estático
        );

        echo '<div class="cuadros-container">';
        foreach ($titulosCajas as $titulo) {
            $result = $conn->query($queries[$titulo]);
            if ($result && $row = $result->fetch_assoc()) {
                echo "<div class='cuadro'>";
                echo "<div class='cuadro-title'>" . htmlspecialchars($titulo) . "</div>";
                echo "<p>Máximo: " . htmlspecialchars($row['max']) . "</p>";
                echo "<p>Mínimo: " . htmlspecialchars($row['min']) . "</p>";
                echo "<p>Promedio: " . htmlspecialchars($row['avg']) . "</p>";
                echo "</div>";
            }
        }
        echo '</div>';
        
        // Function to display sensor data in a table with custom color
        function displaySensorData($conn, $tableName, $color, $colores, $limit = 10) {
            // Determinar la clase de color para la tabla y el título
            $colorClase = isset($colores[$color]) ? $colores[$color] : 'tabla-verde';
            $colorTitulo = isset($colores[$color]) ? 'titulo-' . $color : 'titulo-verde';
            
            echo '<div class="sensor-heading">';
            echo '<div class="sensor-title ' . $colorTitulo . '">Sensor: ' . htmlspecialchars($tableName) . '</div>';
            echo '</div>';
            
            // Get column names for the table headers
            $columnsResult = $conn->query("SHOW COLUMNS FROM $tableName");
            if ($columnsResult) {
                $columns = $columnsResult->fetch_all(MYSQLI_ASSOC);
                
                // Query to get the last 10 records
                $query = "SELECT * FROM $tableName ORDER BY id DESC LIMIT $limit";
                $result = $conn->query($query);
                
                if ($result && $result->num_rows > 0) {
                    echo '<div class="table-container">';
                    echo '<table class="' . $colorClase . '">';
                    
                    // Table header
                    echo '<tr>';
                    foreach ($columns as $column) {
                        echo '<th>' . htmlspecialchars($column['Field']) . '</th>';
                    }
                    echo '</tr>';
                    
                    // Table data
                    while ($row = $result->fetch_assoc()) {
                        echo '<tr>';
                        foreach ($columns as $column) {
                            $fieldName = $column['Field'];
                            echo '<td>' . htmlspecialchars($row[$fieldName]) . '</td>';
                        }
                        echo '</tr>';
                    }
                    
                    echo '</table>';
                    echo '</div>';
                } else {
                    echo '<p style="text-align: center;">No hay datos disponibles para ' . htmlspecialchars($tableName) . '</p>';
                }
            }
        }
        
        // Display sensor data with custom colors
        foreach ($coloresSensores as $sensor => $color) {
            displaySensorData($conn, $sensor, $color, $colores);
        }
        
        // Close the connection
        $conn->close();
    }
    ?>
</body>
</html>