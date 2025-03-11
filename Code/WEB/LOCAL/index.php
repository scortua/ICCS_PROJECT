<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invernadero - Sistema de Monitoreo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; }
        .header { font-size: 2em; color: cyan; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .connection-status { font-size: 1.2em; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .success { color: green; }
        .error { color: red; }
        table { width: 80%; border-collapse: collapse; margin-bottom: 30px; }
        th { background-color: #4CAF50; color: white; text-align: left; padding: 12px; }
        td { border: 1px solid #ddd; padding: 12px; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        .sensor-title { font-size: 1.5em; color: #333; margin: 20px 0 10px 0; }
    </style>
</head>
<body>
    <div class="header">Datos del Invernadero</div>

    <?php
    $MyUsername = "RPI4";
    $MyPassword = "raspberry4";
    $MyHostname = "localhost";
    $MyDatabase = "Invernadero";

    // Create connection
    $conn = new mysqli($MyHostname, $MyUsername, $MyPassword, $MyDatabase);

    // Check connection
    if ($conn->connect_error) {
        echo '<div class="connection-status error">Connection failed: ' . $conn->connect_error . '</div>';
    } else {
        echo '<div class="connection-status success">Connected successfully</div>';
        
        // Function to display sensor data in a table
        function displaySensorData($conn, $tableName, $limit = 10) {
            echo '<div class="sensor-title">Sensor: ' . htmlspecialchars($tableName) . '</div>';
            
            // Get column names for the table headers
            $columnsResult = $conn->query("SHOW COLUMNS FROM $tableName");
            if ($columnsResult) {
                $columns = $columnsResult->fetch_all(MYSQLI_ASSOC);
                
                // Query to get the last 10 records
                $query = "SELECT * FROM $tableName ORDER BY id DESC LIMIT $limit";
                $result = $conn->query($query);
                
                if ($result && $result->num_rows > 0) {
                    echo '<table>';
                    
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
                } else {
                    echo '<p>No hay datos disponibles para ' . htmlspecialchars($tableName) . '</p>';
                }
            }
        }
        
        // Display DHT22 sensor data
        displaySensorData($conn, "DHT22");
        
        // To add another sensor table, just add another call to the function:
        // displaySensorData($conn, "OtherSensorName");
        
        // Close the connection
        $conn->close();
    }
    ?>
</body>
</html>