<?php
require_once('../../config.php');

$courseid = optional_param('courseid', 0, PARAM_INT);
$id = optional_param('id', 0, PARAM_INT);


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

$json_string = str_replace(array('(', ')', "'", ","), array('[', ']', '"', ','), $question_output[0]);

$question_pairs = json_decode($json_string, true);

$PAGE->set_title('Preview Questions');
$PAGE->set_heading('Preview Questions');

echo '<h2 class="lecture-name">Preview Questions</h2>';


$table = new html_table();
$table->head = array('Index', 'Question', 'Answer', 'Action');

$counter = 0;

foreach ($question_pairs as $pair) {
    $question = $pair[0];
    $answer = $pair[1];
    $index = ++$counter;
    $checkbox = html_writer::checkbox("selected_questions[]", $index, false);

    $table->data[] = array($index, $question, $answer, $checkbox);
}

echo html_writer::table($table);

echo $OUTPUT->footer();