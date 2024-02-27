<?php
require_once('../../config.php');
require_once('lib/forms/generate_form.php'); 

session_start();

$courseid = optional_param('courseid', 0, PARAM_INT);
$id = optional_param('id', 0, PARAM_INT); // Activity Id
$redirect = optional_param('redirect', 0, PARAM_BOOL);

if ($courseid == 0 && isset($_SESSION['courseid']) && $redirect == 0 && isset($_SESSION['redirect']) && $id == 0 && isset($_SESSION['id'])) {
    $courseid = $_SESSION['courseid'];
    $redirect = 1;
    $id = $_SESSION['id'];
}

if ($courseid) {
    $course = get_course($courseid);
}

if (!$course) {
    print_error('invalidcourse', 'error');
}

require_login($course->id, false);
$PAGE->set_pagelayout('course');
$PAGE->set_context(context_course::instance($course->id));
$cm = get_coursemodule_from_id('resource', $id, $course->id); // Get Activity Module

if (!$cm && $cm->course != $course->id && !$redirect) {
    print_error('Invalid Activity Id/Course Id', 'error');
}

require_login($course, false, $cm);

if (!$_SESSION['courseid'] && !$_SESSION['id']) {
    $_SESSION['courseid'] = $course->id;
    $_SESSION['redirect'] = 1;
    $_SESSION['id'] = $id;
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
    $file = reset($files);
    unset($files);
}

$courseurl = new moodle_url('/course/view.php', array('id' => $courseid));
$form = new generate_form();

if ($form->is_cancelled()) {
    redirect($courseurl);
} elseif ($form_data = $form->get_data()) {
    $contents = $file->get_content();
    $filepath = '/opt/homebrew/var/www/moodle/local/questiongenerator/lecture-files/' . $activityname . '.pdf';
    file_put_contents($filepath, $contents);

    echo '<div class="loading-screen" id="loadingScreen">Generating Questions...</div>';
    echo '<script>';
    echo 'document.getElementById("loadingScreen").style.display = "block";';
    echo 'document.getElementById("lecture-name").style.display = "none";';
    echo '</script>';

    ob_flush();
    flush();
    $python_script = '/opt/homebrew/var/www/moodle/local/questiongenerator/scripts/question-generator.py';
    $command = "python3 $python_script $filepath " . (int)$form_data->questionsnumber;
    exec($command, $output, $return_var);

    echo '<script>';
    echo 'document.getElementById("loadingScreen").style.display = "none";';
    echo '</script>';

    if ($return_var == 0) {
        var_dump ($output);
    } else {
        var_dump('Error executing Python script!');
    }
}

$form->display();

echo '</div>';

echo $OUTPUT->footer();
