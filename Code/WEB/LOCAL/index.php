<?php 
    // Start MySQL Connection
    include('connect.php'); 
?>

<html>
<head>
    <title>Raspberry Pi Weather Log</title>
    <style type="text/css">
        .table_titles, .table_cells_odd, .table_cells_even {
                padding-right: 20px;
                padding-left: 20px;
                color: #000;
        }
        .table_titles {
            color: #FFF;
            background-color: #666;
        }
        .table_cells_odd {
            background-color: #CCC;
        }
        .table_cells_even {
            background-color: #FAFAFA;
        }
        table {
            border: 2px solid #333;
        }
        body { font-family: "Trebuchet MS", Arial; }
    </style>
</head>

    <body>
        <h1>GreenHouse with Raspberry Pi</h1>

    <table border="0" cellspacing="0" cellpadding="4">
      <tr>
            <td class="table_titles">ID</td>
            <td class="table_titles">Fecha</td>
            <td class="table_titles">Temperatura</td>
            <td class="table_titles">Humedad</td>
          </tr>
<?php


    // Retrieve all records and display them
    $result = mysql_query("SELECT * FROM data ORDER BY id DESC");

    // Used for row color toggle
    $oddrow = true;

    // process every record
    while( $row = mysql_fetch_array($result) )
    {
        if ($oddrow) 
        { 
            $css_class=' class="table_cells_odd"'; 
        }
        else
        { 
            $css_class=' class="table_cells_even"'; 
        }

        $oddrow = !$oddrow;

        echo '<tr>';
        echo '   <td'.$css_class.'>'.$row["ID"].'</td>';
        echo '   <td'.$css_class.'>'.$row["Fecha"].'</td>';
        echo '   <td'.$css_class.'>'.$row["Temperatura"].'</td>';
        echo '   <td'.$css_class.'>'.$row["Humedad"].'</td>';
        echo '</tr>';
    }
?>
    </table>
    </body>
</html>