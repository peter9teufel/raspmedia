 <?php

  $f = fopen("kioskhost.txt", "r");

  // Liest eine Zeile aus der Textdatei und gibt deren Inhalt aus
  $url = fgets($f); 
  //echo $url;
  echo '<iframe src="' . $url . '" width="100%" height="100%">$url is not compatible with RaspMedia Kiosk!</iframe>';
  fclose($f);

?>