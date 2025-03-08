<?php
$MyUsername = "RPI4";  // enter your username for mysql
$MyPassword = "raspberry4";  // enter your password for mysql
$MyHostname = "localhost";      // this is usually "localhost" unless your database resides on a different server

$dbh = mysql_pconnect($MyHostname , $MyUsername, $MyPassword);
$selected = mysql_select_db("Invernadero",$dbh); //Enter your database name here 
?>