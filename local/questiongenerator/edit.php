<?php
require_once('../../config.php');
require_once('lib/forms/generate_question.php');

session_start();

$courseid = optional_param('courseid', 0, PARAM_INT);
$id = optional_param('id', 0, PARAM_INT); // Activity Id
$redirect = optional_param('redirect', 0, PARAM_BOOL);
$questionType = optional_param('questiontype', '', PARAM_TEXT);

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

// $context = context_module::instance($cm->id);
// $fs = get_file_storage();
// $files = $fs->get_area_files($context->id, 'mod_resource', 'content', 0, 'sortorder DESC, id ASC', false);
// if (count($files) < 1) {
//     print_error('Invalid File', 'error');
// } else {
//     $file = reset($files);
//     unset($files);
// }

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


$courseurl = new moodle_url('/local/questiongenerator/view.php', array('courseid' => $course->id, 'id' => $cm->id, 'questiontype' => $questionType));

$form = new generate_question();

if ($form->is_cancelled()) {
    redirect($courseurl);
} elseif ($form_data = $form->get_data()) {
    $contents = $file->get_content();
    $lecturename = str_replace(' ', '', $activityname);
//    $filepath = '/Users/mymac/Downloads/test.pdf'; // Change to the path you want
    file_put_contents($filepath, $contents);

    echo '<div class="loading-screen" id="loadingScreen">Generating Questions...</div>';
    echo '<script>';
    echo 'document.getElementById("loadingScreen").style.display = "block";';
    echo 'document.getElementById("lecture-name").style.display = "none";';
    echo '</script>';

    ob_flush();
    flush();
   // Get the selected question type from the form data
   $questionType = $form_data->questiontype;

   // Set the path to the Python script based on the selected question type
   switch ($questionType) {
    case 'mcq':
        $python_script = '/usr/local/var/www/moodle/local/questiongenerator/scripts/mcq.py';
        break;
    case 'truefalse':
        $python_script = '/usr/local/var/www/moodle/local/questiongenerator/scripts/true_false.py';
        break;
    case 'shortanswer':
        default:
        $python_script = '/usr/local/var/www/moodle/local/questiongenerator/scripts/question-generator.py';
        break;
    }

// Execute the Python script

    $command = "python3.12 $python_script $filepath " . (int) $form_data->questionsnumber;
    exec($command, $output, $return_var);
    


    echo '<script>';
    echo 'document.getElementById("loadingScreen").style.display = "none";';
    echo '</script>';

    if ($return_var == 0) {
        $output_json = implode("\n", $output);  // Combine the output lines into a single string
        $_SESSION['question_output'] = $output_json;  // Store the JSON string in the session
        redirect(new moodle_url('/local/questiongenerator/view.php', array('courseid' => $course->id, 'id' => $cm->id, 'questiontype' => $questionType)));
    } else {
        var_dump('Error executing Python script!');
    }
}


$form->display();

echo '</div>';

echo $OUTPUT->footer();
