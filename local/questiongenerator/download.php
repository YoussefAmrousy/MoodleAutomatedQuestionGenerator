<?php
require_once ('../../config.php');
require_login();

$file = required_param('file', PARAM_FILE);

// Decode the file name from URL
$filename = urldecode(basename($file));

// Ensure the file exists in the temporary directory
$temp_dir = sys_get_temp_dir();
$filepath = $temp_dir . '/' . $filename;

if (file_exists($filepath)) {
    // Set headers to force download
    header('Content-Description: File Transfer');
    header('Content-Type: application/xml');
    header('Content-Disposition: attachment; filename="' . $filename . '"');
    header('Expires: 0');
    header('Cache-Control: must-revalidate');
    header('Pragma: public');
    header('Content-Length: ' . filesize($filepath));

    // Read the file content and output it
    readfile($filepath);

    // Optionally, delete the file after download
    unlink($filepath);

    exit();
} else {
    echo 'File not found.';
}