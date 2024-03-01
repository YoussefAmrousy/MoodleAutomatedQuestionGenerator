<?php
require_once('../../config.php');

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