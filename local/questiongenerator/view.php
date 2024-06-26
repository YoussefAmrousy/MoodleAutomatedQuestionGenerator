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
$lecture = isset($_SESSION['lecture']) ? $_SESSION['lecture'] : '';

// Check if $question_output is an array and implode it if necessary
if (is_array($question_output)) {
    $json_string = implode('', $question_output);
} else {
    $json_string = $question_output;
}

$questions_array = json_decode($json_string, true);

if (json_last_error() !== JSON_ERROR_NONE) {
    echo '<p>Error decoding JSON: ' . json_last_error_msg() . '</p>';
    echo $OUTPUT->footer();
    exit;
}

$PAGE->set_title('Preview Questions');
$PAGE->set_heading('Preview Questions');

echo '<h2 class="lecture-name">Preview Questions</h2>';

// Start form to submit selected questions
echo '<form id="saveQuestionsForm" method="post">';
echo '<input type="hidden" name="courseid" value="' . $courseid . '">';
echo '<input type="hidden" name="lecture" value =' . $lecture . '">';
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

    // Checkbox to select question
    $checkbox = html_writer::checkbox("selected_questions[]", $question_json, false);
    $table->data[] = array($index, "<span class='editable-question'>$question</span>", $answer, $difficulty, $checkbox);
}

echo html_writer::table($table);

echo "<div class='d-flex justify-content-end'>";
echo "<input type='button' id='submitBtn' value='Save Selected Questions' class='btn btn-primary'>";
echo "</div>";

echo '</form>'; // End form

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

    document.getElementById('submitBtn').addEventListener('click', function() {
    var selectedQuestions = [];
    var checkboxes = document.querySelectorAll('input[name="selected_questions[]"]:checked');
    var courseid = document.querySelector('input[name="courseid"]').value;
    var lecture = document.querySelector('input[name="lecture"]').value;
    
    if (checkboxes.length === 0) {
        alert('You must select at least one question!');
        return;
    }

    checkboxes.forEach(function(checkbox) {
        selectedQuestions.push(JSON.parse(checkbox.value));
    });

    var formData = new FormData();
    formData.append('selected_questions', JSON.stringify(selectedQuestions));
    formData.append('courseid', courseid);
    formData.append('lecture', lecture);

    fetch('save_questions.php', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        window.location.href = data.download_url;

        setTimeout(function() {
                window.location.href = 'tutorial.php?courseid=' + courseid;
            }, 2000);
    })
    .catch(error => {
        console.error('Error:', error);
    });
});

});
</script>
