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

foreach ($questions_array['questions'] as $pair) {
    $question_type = $pair['type'];
    $index = ++$counter;
    $question = $pair['question'];
    $difficulty = $pair['difficulty'];

    $question_json = json_encode($pair);

    if ($question_type == "Multiple Choice") {
        $correct_answer = $pair['correct_answer'];
        $answer = "<ul>";
        foreach ($pair['options'] as $ans) {
            if ($ans == $correct_answer) {
                $answer .= "<li><strong>$ans</strong></li>";
                continue;
            }
            $answer .= "<li>$ans</li>";
        }
        $answer .= "</ul>";
    } else {
        $answer = "<strong>" . $pair['answer'] . "</strong>";
    }
    $checkbox = html_writer::checkbox("selected_questions[]", $question_json, true);
    $table->data[] = array($index, "<span class='editable-question'>$question</span>", $answer, $difficulty, $checkbox);
}

echo html_writer::table($table);
echo "<div class='d-flex justify-content-end'>";
echo "<input type='submit' value='Save Selected Questions' class='btn btn-primary'>";
echo "</div>";

echo $OUTPUT->footer();
?>

<script>
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.editable-question').forEach(function(element) {
        element.addEventListener('click', function() {
            // Prevent re-initializing the input field if it already exists
            if (this.querySelector('input')) {
                return;
            }

            var currentText = this.innerText;
            var input = document.createElement('input');
            input.type = 'text';
            input.value = currentText;
            input.classList.add('form-control');

            input.addEventListener('blur', function() {
                element.innerText = this.value;
                // Here you can add an AJAX call to save the edited question to the server if needed.
            });

            input.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    input.blur();
                }
            });

            this.innerHTML = '';
            this.appendChild(input);
            input.focus();
        });
    });
});
</script>

<style>
.editable-question {
    cursor: pointer;
    display: inline-block;
    padding: 5px;
    border: 1px dashed transparent;
}

.editable-question:hover {
    border: 1px dashed #ccc;
}
</style>
