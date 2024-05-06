<?php
require_once ('../../config.php');

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
$question_pairs = json_decode($question_output, true);

$PAGE->set_title('Preview Questions');
$PAGE->set_heading('Preview Questions');

echo '<h2 class="lecture-name">Preview Questions</h2>';

$table = new html_table();
$table->head = array('Index', 'Question', 'Answer', 'Difficulty', 'Action');

$counter = 0;

if ($questionType == "truefalse") {
    foreach ($question_pairs as $pair) {
        $question = $pair[0];
        $answer = $pair[1] ? 'True' : 'False';
        $difficulty = $pair[2];
        $index = ++$counter;
        $checkbox = html_writer::checkbox("selected_questions[]", $index, true);
        $table->data[] = array($index, $question, $answer, $difficulty, $checkbox);
    }
} else {
    foreach ($question_pairs as $pair) {
        $question = $pair[0];
        $answer = $pair[1];
        $difficulty = $pair[2];
        $index = ++$counter;
        $checkbox = html_writer::checkbox("selected_questions[]", $index, true);
        $table->data[] = array($index, $question, $answer, $difficulty, $checkbox);
    }
}

echo html_writer::table($table);

echo $OUTPUT->footer();