<?php
require_once('../../config.php');

$PAGE->set_url('/local/questiongenerator/tutorial.php');
$PAGE->set_title('Tutorial Page');
$PAGE->set_heading('Tutorial Page');

echo $OUTPUT->header();

if (isset($_GET['xml'])) {
    $xml_file = htmlspecialchars($_GET['xml']);
    $xml_filename = basename($xml_file);

    // Display download link
    echo '<a href="' . $xml_file . '" download="' . $xml_filename . '">Download Generated XML</a>';
} else {
    echo '<p>No XML file available for download.</p>';
}

echo $OUTPUT->footer();
?>
