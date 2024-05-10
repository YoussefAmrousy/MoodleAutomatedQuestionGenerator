<?php
require_once ('../../config.php');

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

// $gift_filename = trim($output);
// $gift_file_url = "moodle/$gift_filename";


echo $OUTPUT->header();

$question_output = isset($_SESSION['question_output']) ? $_SESSION['question_output'] : '[]';
$json_string = implode('', $question_output);
$json_string = rtrim($json_string, ',');
$questions_array = json_decode($json_string, true);

$PAGE->set_title('Preview Questions');
$PAGE->set_heading('Preview Questions');

echo '<h2 class="lecture-name">Preview Questions</h2>';

$table = new html_table();
$table->head = array('Index', 'Question', 'Answer', 'Difficulty', 'Action');

$counter = 0;

foreach ($questions_array as $pair) {
    $question_type = $pair['type'];
    $index = ++$counter;
    $question = $pair['question'];
    $difficulty = $pair['difficulty'];

    if ($question_type == "Multiple Choice") {
        $correct_answer = $pair['correct_answer'];
        $answer = "<ol type='A'>";
        foreach ($pair['options'] as $ans) {
            if ($ans == $correct_answer) {
                $answer .= "<li><strong>$ans</strong></li>";
                continue;
            }
            $answer .= "<li>$ans</li>";
        }
        $answer .= "</ol>";
    } else {
        $answer = "<strong>" . $pair['answer'] . "</strong>";
    }
    $checkbox = html_writer::checkbox("selected_questions[]", $index, true);
    $table->data[] = array($index, $question, $answer, $difficulty, $checkbox);
}

echo html_writer::table($table);
// if (file_exists($gift_file_url)) {
//     echo "<div><a href='{$gift_file_url}' download class='btn btn-primary'>Download GIFT File</a></div>";
// } else {
//     echo "<p>The GIFT file could not be found.</p>";
// }
echo $OUTPUT->footer();