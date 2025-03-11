<?php
$MyUsername = "RPI4";  // enter your username for mysql
$MyPassword = "raspberry4";  // enter your password for mysql
$MyHostname = "localhost";      // this is usually "localhost" unless your database resides on a different server
$MyDatabase = "Invernadero"; // Enter your database name here

// Create connection
$conn = new mysqli($MyHostname, $MyUsername, $MyPassword, $MyDatabase);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}
$sql = "SELECT id, fecha, temperatura, humedad FROM DHT22 ORDER BY fecha DESC LIMIT 10";
$result = $conn->query($sql);

$data = array();
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
}

$conn->close();

header('Content-Type: application/json');
echo json_encode($data);
?>