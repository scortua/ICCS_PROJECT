<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Invernadero - Sistema de Monitoreo</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f8f9fa; }
        .header { font-size: 2em; color: #009688; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .connection-status { font-size: 1.2em; font-weight: bold; text-align: center; margin-bottom: 20px; }
        .success { color: green; }
        .error { color: red; }
        
        .sensor-container { margin-bottom: 30px; background-color: white; border-radius: 8px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); overflow: hidden; }
        .sensor-title { font-size: 1.5em; color: #333; padding: 15px; cursor: pointer; display: flex; justify-content: space-between; align-items: center; }
        .sensor-title:hover { background-color: #f1f1f1; }
        
        .sensor-content { display: none; padding: 0 15px 15px 15px; }
        .sensor-content.active { display: block; }
        
        table { width: 100%; border-collapse: collapse; margin-bottom: 15px; }
        th { background-color: #4CAF50; color: white; text-align: left; padding: 12px; }
        td { border: 1px solid #ddd; padding: 12px; }
        tr:nth-child(even) { background-color: #f2f2f2; }
        
        .button-container { display: flex; justify-content: center; gap: 15px; margin: 20px 0; }
        .btn { 
            padding: 10px 20px; 
            background-color: #4CAF50; 
            color: white; 
            border: none; 
            border-radius: 4px; 
            cursor: pointer; 
            font-size: 16px; 
            transition: background-color 0.3s;
        }
        .btn:hover { background-color: #45a049; }
        .btn.active { background-color: #367c39; box-shadow: 0 0 5px rgba(0,0,0,0.3); }
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
        echo '<div class="connection-status error">Conexión fallida: ' . $conn->connect_error . '</div>';
    } else {
        echo '<div class="connection-status success">Conectado exitosamente</div>';
        
        // Get all table names from the database to create buttons dynamically
        $tablesResult = $conn->query("SHOW TABLES");
        $tables = [];
        
        if ($tablesResult) {
            while ($row = $tablesResult->fetch_row()) {
                $tables[] = $row[0];
            }
        }
        
        // Create buttons for each table
        if (!empty($tables)) {
            echo '<div class="button-container">';
            foreach ($tables as $index => $table) {
                $activeClass = ($index === 0) ? ' active' : '';
                echo '<button class="btn' . $activeClass . '" onclick="showSensor(\'' . $table . '\')">' . $table . '</button>';
            }
            echo '</div>';
        }
        
        // Create containers for each sensor table
        foreach ($tables as $index => $table) {
            $activeClass = ($index === 0) ? ' active' : '';
            
            echo '<div id="' . $table . '-container" class="sensor-container">';
            echo '<div class="sensor-title" onclick="toggleSensor(\'' . $table . '\')">';
            echo 'Sensor: ' . htmlspecialchars($table);
            echo '<span id="' . $table . '-toggle">▼</span>';
            echo '</div>';
            
            echo '<div id="' . $table . '-content" class="sensor-content' . $activeClass . '">';
            
            // Get column names for the table headers
            $columnsResult = $conn->query("SHOW COLUMNS FROM $table");
            if ($columnsResult) {
                $columns = $columnsResult->fetch_all(MYSQLI_ASSOC);
                
                // Query to get the last 10 records
                $query = "SELECT * FROM $table ORDER BY id DESC LIMIT 10";
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
                    echo '<p>No hay datos disponibles para ' . htmlspecialchars($table) . '</p>';
                }
            }
            
            echo '</div>'; // End sensor-content
            echo '</div>'; // End sensor-container
        }
        
        // Close the connection
        $conn->close();
    }
    ?>
    
    <script>
        // Function to show a specific sensor and hide others
        function showSensor(sensorId) {
            // Update button states
            document.querySelectorAll('.btn').forEach(btn => {
                btn.classList.remove('active');
            });
            document.querySelector('button[onclick="showSensor(\'' + sensorId + '\')"]').classList.add('active');
            
            // Show the selected sensor container and hide others
            document.querySelectorAll('.sensor-container').forEach(container => {
                if (container.id === sensorId + '-container') {
                    container.style.display = 'block';
                } else {
                    container.style.display = 'none';
                }
            });
            
            // Ensure the content is visible
            document.getElementById(sensorId + '-content').classList.add('active');
            document.getElementById(sensorId + '-toggle').textContent = '▼';
        }
        
        // Function to toggle a sensor's content
        function toggleSensor(sensorId) {
            const content = document.getElementById(sensorId + '-content');
            const toggle = document.getElementById(sensorId + '-toggle');
            
            if (content.classList.contains('active')) {
                content.classList.remove('active');
                toggle.textContent = '►';
            } else {
                content.classList.add('active');
                toggle.textContent = '▼';
            }
        }
        
        // Initialize - show only the first sensor on page load
        document.addEventListener('DOMContentLoaded', function() {
            const tables = <?php echo json_encode($tables ?? []); ?>;
            
            if (tables.length > 0) {
                tables.forEach((table, index) => {
                    const container = document.getElementById(table + '-container');
                    if (container) {
                        if (index === 0) {
                            container.style.display = 'block';
                        } else {
                            container.style.display = 'none';
                        }
                    }
                });
            }
        });
    </script>
</body>
</html>