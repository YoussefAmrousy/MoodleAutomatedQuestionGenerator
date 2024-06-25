<?php
require_once ('../../config.php');

$PAGE->set_url('/local/questiongenerator/tutorial.php');
$PAGE->set_title('Tutorial Page');
$PAGE->set_heading('Tutorial Page');

echo $OUTPUT->header();

// CSS for styling
echo '<style>
    .center {
        text-align: center;
        margin-top: 20px;
    }
    .video-container {
        margin-top: 20px;
    }
    .button-container {
        text-align: center;
        margin-top: 20px;
    }
    .button {
        display: inline-block;
        padding: 10px 20px;
        background-color: #007bff;
        color: #fff;
        text-decoration: none;
        border-radius: 5px;
        transition: background-color 0.3s ease;
    }
    .button:hover {
        background-color: #0056b3;
    }
</style>';

// Success message
echo '<div class="center"><h5>Questions have been successfully generated and saved to your downloads folder as Moodle_Generated_Questions.</h5></div>';

// Video embed
echo '<div class="video-container center">';
echo '<video width="640" height="360" controls>';
echo '<source src="import-generated-questions-file-video.mov" type="video/mp4">';
echo 'Your browser does not support the video tag.';
echo '</video>';
echo '</div>';

// Additional instructions and download links
echo '<div class="center">';
echo '<p>This video demonstrates how to import the generated questions file into Question Bank.</p>';
echo '<p>Click <a href="import-generated-questions-file-video.mov" download>here</a> to download the video.</p>';
echo '</div>';

// Button to redirect to Question Bank
echo '<div class="button-container">';
echo '<a href="path/to/question/bank" class="button">Go to Question Bank</a>';
echo '</div>';

echo $OUTPUT->footer();
