<?php
require_once('../../config.php');

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if (!empty($data['selected_questions'])) {
        $selected_questions = $data['selected_questions'];
        $temp_file = tempnam(sys_get_temp_dir(), 'questions_');
        file_put_contents($temp_file, json_encode($selected_questions));

        // Path to Python interpreter and script
        $python_script = '/usr/local/var/www/moodle/local/questiongenerator/scripts/save_xml.py';
        
        // Command to execute the Python script
        $command = escapeshellcmd("python3 $python_script $temp_file");

        // Execute the command and capture the output
        exec($command . ' 2>&1', $output, $return_var);

        // Check if execution was successful
        if ($return_var == 0 && !empty($output)) {
            $xml_filepath = trim(end($output));

            // Debugging: Log the output and the filepath
            error_log("Python script output: " . print_r($output, true));
            error_log("XML filepath: " . $xml_filepath);

            // Check if the file exists before attempting to read it
            if (file_exists($xml_filepath)) {
                // Redirect to the tutorial page with the URL to download the XML file
                $download_url = new moodle_url('/local/questiongenerator/tutorial.php', array('xml' => $xml_filepath, 'courseid' => $course->id, 'id' => $cm->id ));                redirect($download_url);
            } else {
                echo 'Error: XML file does not exist.';
                echo '<pre>' . htmlspecialchars(implode("\n", $output)) . '</pre>';
            }
        } else {
            // Error handling if script execution fails
            echo 'Error saving questions to XML, please try again!';
            echo '<pre>' . htmlspecialchars(implode("\n", $output)) . '</pre>';
        }
    } else {
        echo 'No questions selected, please go back and select questions.';
    }
} else {
    echo 'Invalid request method.';
}
