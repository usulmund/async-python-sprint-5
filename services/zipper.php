<?php

$file = file_get_contents('https://your-bucket-name.storage.yandexcloud.net/your-file-name');

$zip = new ZipArchive();
$zip->open('file.zip', ZipArchive::CREATE);

$zip->addFromString('your-file-name', $file);

$zip->close();

header('Content-Type: application/zip');
header('Content-disposition: attachment; filename=file.zip');
header('Content-Length: ' . filesize('file.zip'));
readfile('file.zip');
?>
