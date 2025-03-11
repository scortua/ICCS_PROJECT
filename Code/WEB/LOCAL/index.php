<?php
$MyUsername = "RPI4";  // enter your username for mysql
$MyPassword = "raspberry4";  // enter your password for mysql
$MyHostname = "localhost";      // this is usually "localhost" unless your database resides on a different server
$MyDatabase = "Invernadero"; // Enter your database name here

// Create connection
$conn = new mysqli($MyHostname, $MyUsername, $MyPassword, $MyDatabase);

// Check connection
if ($conn->connect_error) {
    $status = "Connection failed: " . $conn->connect_error;
    $dates = [];
    $temperatures = [];
    $humidities = [];
} else {
    $status = "Connected successfully";
    $sql = "SELECT fecha, temperatura, humedad FROM DHT22 ORDER BY fecha DESC LIMIT 10";
    $result = $conn->query($sql);

    $dates = array();
    $temperatures = array();
    $humidities = array();

    if ($result->num_rows > 0) {
        while($row = $result->fetch_assoc()) {
            $dates[] = $row['fecha'];
            $temperatures[] = $row['temperatura'];
            $humidities[] = $row['humedad'];
        }
    }

    $conn->close();
}
?>
<!DOCTYPE html>
<html>
<head>
    <title>Datos del Invernadero</title>
    <style>
        table {
            width: 100%;
            border-collapse: collapse;
        }
        th, td {
            border: 1px solid black;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .chart-container {
            width: 80%;
            margin: auto;
        }
    </style>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <h1>Datos del Invernadero</h1>
    <p><?php echo $status; ?></p>
    <div class="chart-container">
        <canvas id="temperatureChart"></canvas>
        <canvas id="humidityChart"></canvas>
    </div>
    <script>
        document.addEventListener("DOMContentLoaded", function() {
            const labels = <?php echo json_encode($dates); ?>;
            const temperatures = <?php echo json_encode($temperatures); ?>;
            const humidities = <?php echo json_encode($humidities); ?>;

            const temperatureCtx = document.getElementById('temperatureChart').getContext('2d');
            const humidityCtx = document.getElementById('humidityChart').getContext('2d');

            new Chart(temperatureCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Temperatura',
                        data: temperatures,
                        borderColor: 'rgba(255, 99, 132, 1)',
                        backgroundColor: 'rgba(255, 99, 132, 0.2)',
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Fecha'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Temperatura (°C)'
                            }
                        }
                    }
                }
            });

            new Chart(humidityCtx, {
                type: 'line',
                data: {
                    labels: labels,
                    datasets: [{
                        label: 'Humedad',
                        data: humidities,
                        borderColor: 'rgba(54, 162, 235, 1)',
                        backgroundColor: 'rgba(54, 162, 235, 0.2)',
                        fill: false
                    }]
                },
                options: {
                    scales: {
                        x: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Fecha'
                            }
                        },
                        y: {
                            display: true,
                            title: {
                                display: true,
                                text: 'Humedad (%)'
                            }
                        }
                    }
                }
            });
        });
    </script>
</body>
</html>