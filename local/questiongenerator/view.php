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
$json_string = implode('', $question_output);
$json_string = rtrim($json_string, ',');
$questions_array = json_decode($json_string, true);

$PAGE->set_title('Preview Questions');
$PAGE->set_heading('Preview Questions');

echo '<h2 class="lecture-name">Preview Questions</h2>';

// Start form to submit selected questions
echo '<form id="saveQuestionsForm" action="save_questions.php" method="post">';

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
echo "<input type='submit' value='Save Selected Questions' class='btn btn-primary'>";
echo "</div>";

echo '</form>'; // End form

echo $OUTPUT->footer();
?>

<script>
document.addEventListener('DOMContentLoaded', function() {
    document.querySelectorAll('.editable-question').forEach(function(element) {
        element.addEventListener('click', function() {
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

    // Handle checkbox changes to submit form
    document.getElementById('saveQuestionsForm').addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent default form submission
        
        var selectedQuestions = [];
        var checkboxes = document.querySelectorAll('input[name="selected_questions[]"]:checked');
        checkboxes.forEach(function(checkbox) {
            selectedQuestions.push(JSON.parse(checkbox.value));
        });

        // Post selected questions to save_questions.php
        fetch('save_questions.php?courseid=<?php echo $courseid; ?>&id=<?php echo $id; ?>', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ selected_questions: selectedQuestions }),
        })
        .then(response => response.text())
        .then(data => {
            // Handle the response
            if (data.includes('Error')) {
                console.error(data);
            } else {
                // Redirect to the tutorial page or handle the result
                window.location.href = 'tutorial.php?xml=' + encodeURIComponent(data) + '&courseid=<?php echo $courseid; ?>&id=<?php echo $id; ?>';
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
});
</script>


