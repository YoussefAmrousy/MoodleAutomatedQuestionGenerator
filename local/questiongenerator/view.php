<?php
require_once('../../config.php');

$courseid = optional_param('courseid', 0, PARAM_INT);
$id = optional_param('id', 0, PARAM_INT);
$questionType = optional_param('questiontype', '', PARAM_TEXT);


$course = get_course($courseid);
$cm = get_coursemodule_from_id('resource', $id, $course->id);

if (!$course) {
    print_error('invalidcourse', 'error');
}

if (!$cm && $cm->course != $course->id) {
    print_error('Invalid Activity Id/Course Id', 'error');
}

$PAGE->set_context(context_course::instance($courseid));
$PAGE->set_pagelayout('course');
$PAGE->set_url('/local/questiongenerator/view.php', array('courseid' => $courseid, 'id' => $id));
$PAGE->set_title($cm->name . ' - ' . 'Preview Questions');
$PAGE->set_heading($course->fullname);

require_login($course, false);


session_start();


echo $OUTPUT->header();


$question_output = isset($_SESSION['question_output']) ? $_SESSION['question_output'] : '[]';
//Decode the JSON output based on the question type
if ($questionType == "truefalse") {
    $decoded_output = json_decode($question_output, true);
// Check if the result is a string (indicating double-encoding)
if (is_string($decoded_output)) {
    // Decode the inner JSON string
    $question_pairs = json_decode($decoded_output, true);
} else {
    // The output was not double-encoded, so use the decoded output directly
    $question_pairs = $decoded_output;
}
} else {
   $decoded_output = json_decode($question_output, true);
   // Check if the result is a string (indicating double-encoding)
   if (is_string($decoded_output)) {
    // Decode the inner JSON string
        $question_pairs = json_decode($decoded_output, true);
   } else {
    // The output was not double-encoded, so use the decoded output directly
        $question_pairs = $decoded_output;}
}


$PAGE->set_title('Preview Questions');
$PAGE->set_heading('Preview Questions');

echo '<h2 class="lecture-name">Preview Questions</h2>';


$table = new html_table();
$table->head = array('Index', 'Question', 'Answer', 'Action');

$counter = 0;


if ($questionType == "truefalse") {
    foreach ($question_pairs as $pair) {
        $question = $pair[0]; // Correct index for the question text
        $answer = $pair[1] ? 'True' : 'False'; // Correct index for the answer value
        $index = ++$counter;
        $checkbox = html_writer::checkbox("selected_questions[]", $index, false);
        $table->data[] = array($index, $question, $answer, $checkbox);
    }
}
 else {
    // Assume "essay" type
    foreach ($question_pairs as $pair) {
        $question = $pair[0];
        $answer = $pair[1];
        $index = ++$counter;
        $checkbox = html_writer::checkbox("selected_questions[]", $index, false);
        $table->data[] = array($index, $question, $answer, $checkbox);
    }
}


echo html_writer::table($table);

echo $OUTPUT->footer();