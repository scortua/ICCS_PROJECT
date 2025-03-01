<!-- filepath: /c:/Users/Scort/OneDrive/Documentos/santiago cortes tovar/ELECTRONICA/9.noveno semestre/ICCS/PROYECTO/ICCS_PROJECT/LoRa RYLR998/WEB/LOCAL/fetch_data.php -->
<?php
$servername = "localhost";
$username = "RPI4";
$password = "raspberry4";
$dbname = "Invernadero";

// Create connection
$conn = new mysqli($servername, $username, $password, $dbname);

// Check connection
if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

$sql = "SELECT id, fecha, temperatura, humedad FROM your_table_name";
$result = $conn->query($sql);

$data = array();
if ($result->num_rows > 0) {
    while($row = $result->fetch_assoc()) {
        $data[] = $row;
    }
}

$conn->close();

echo json_encode($data);
?>