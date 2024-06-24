<?php
require_once('../../config.php');

if ($_SERVER['REQUEST_METHOD'] === 'POST' && !empty($_POST['selected_questions'])) {
    $selected_questions = $_POST['selected_questions'];
    $temp_file = tempnam(sys_get_temp_dir(), 'questions_');
    file_put_contents($temp_file, json_encode($selected_questions));

    // Path to Python interpreter and script
    $python_interpreter = '/opt/homebrew/var/www/moodle/venv/bin/python3';
    $python_script = '/opt/homebrew/var/www/moodle/local/questiongenerator/scripts/save_xml.py';
    
    // Command to execute the Python script
    $command = "$python_interpreter $python_script $temp_file";

    // Execute the command
    exec($command . ' 2>&1', $output, $return_var);

    // Check if execution was successful
    if ($return_var == 0 && !empty($output)) {
        $xml_filepath = trim(end($output));

        // Set headers to force download
        header('Content-Type: application/xml');
        header('Content-Disposition: attachment; filename="generated_questions.xml"');
        readfile($xml_filepath);  // Output the file contents
        exit();
    } else {
        // Error handling if script execution fails
        echo 'Error saving questions to XML, please try again!';
        echo '<pre>' . htmlspecialchars(implode("\n", $output)) . '</pre>';
    }
} else {
    echo 'No questions selected, please go back and select questions.';
}
?>
