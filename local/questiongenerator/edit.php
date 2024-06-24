<?php
require_once ('../../config.php');
require_once ('lib/forms/generate_question.php');

session_start();

$courseid = optional_param('courseid', 0, PARAM_INT);
$activity_id = optional_param('id', 0, PARAM_INT);
$redirect = optional_param('redirect', 0, PARAM_BOOL);

if ($courseid == 0 && isset($_SESSION['courseid']) && $redirect == 0 && isset($_SESSION['redirect']) && $activity_id == 0 && isset($_SESSION['id'])) {
    $courseid = $_SESSION['courseid'];
    $redirect = 1;
    $activity_id = $_SESSION['id'];
}

if ($courseid) {
    $course = get_course($courseid);
}

if (!$course) {
    print_error('invalidcourse', 'error');
}

// $PAGE->set_pagelayout('course');
// $PAGE->set_context(context_course::instance($course->id));
$cm = get_coursemodule_from_id('resource', $activity_id, $course->id); // Get Activity Module

if (!$cm && $cm->course != $course->id && !$redirect) {
    print_error('Invalid Activity Id/Course Id', 'error');
}

require_login($course, false, $cm);

if (!$_SESSION['courseid'] && !$_SESSION['id']) {
    $_SESSION['courseid'] = $course->id;
    $_SESSION['redirect'] = 1;
    $_SESSION['id'] = $activity_id;
}

$activityname = $cm->name;
$_SESSION['activityname'] = $activityname;

$url = new moodle_url('/local/questiongenerator/edit.php', array('courseid' => $course->id, 'id' => $cm->id));
$PAGE->set_url($url);
$PAGE->set_title('Generate Questions');
$PAGE->set_heading('Generate Questions');

echo $OUTPUT->header();

echo '<style>';
echo '.card-container { padding: 13px; margin-top: 15px; }';
echo '</style>';

echo '<h2 class="lecture-name" id="lecture-name">Lecture ' . $activityname . '</h2>';
echo '<div class="card card-container">';

$context = context_module::instance($cm->id);
$fs = get_file_storage();
$files = $fs->get_area_files($context->id, 'mod_resource', 'content', 0, 'sortorder DESC, id ASC', false);
if (count($files) < 1) {
    print_error('Invalid File', 'error');
} else {
    $file = reset($files); // Get the first file

    // Use the file's contenthash to construct a file path
    $contenthash = $file->get_contenthash();
    $l1 = $contenthash[0] . $contenthash[1];
    $l2 = $contenthash[2] . $contenthash[3];
    $filedir = $CFG->dataroot . '/filedir/' . $l1 . '/' . $l2 . '/' . $contenthash;

    // Check if the file exists in the filedir
    if (file_exists($filedir)) {
        $filepath = $filedir; // Use this file path for the Python script
    } else {
        print_error('File not found in filedir', 'error');
    }
}

$form = new generate_question();

if ($form_data = $form->get_data()) {
    $temp_file = tempnam(sys_get_temp_dir(), 'pdf_');
    copy($filepath, $temp_file);

    echo '<div class="loading-screen" id="loadingScreen">Generating Questions...</div>';
    echo '<script>';
    echo 'document.getElementById("loadingScreen").style.display = "block";';
    echo 'document.getElementById("lecture-name").style.display = "none";';
    echo '</script>';

    ob_flush();
    flush();

    $question_type = $form_data->questiontype;

    // Set python script path based on the local path
    // Set python version based on your local python version to run the script
    $python_interpreter = '/opt/homebrew/var/www/moodle/venv/bin/python3';
    $python_script = '/opt/homebrew/var/www/moodle/local/questiongenerator/scripts/generate_questions.py';
    $command = "$python_interpreter $python_script $filepath $question_type " . (int) $form_data->questionsnumber . " " . $form_data->difficulty;
    
    exec($command, $output, $return_var);
    
    echo '<script>';
    echo 'document.getElementById("loadingScreen").style.display = "none";';
    echo '</script>';
    
    if ($return_var == 0) {
        $_SESSION['question_output'] = $output;
        redirect(new moodle_url('/local/questiongenerator/view.php', array('courseid' => $course->id, 'id' => $cm->id)));
    } else {
        echo 'Error generating questions, please try again!';
        echo '<pre>' . print_r($output, true) . '</pre>'; // Print the output for debugging
    }
    
}

$form->display();

echo '</div>';

echo $OUTPUT->footer();
