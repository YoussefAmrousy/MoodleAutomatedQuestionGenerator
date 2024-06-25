<?php
use core_privacy\local\metadata\types\type;

require_once ('../../config.php');
require_login();

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $selected_questions = isset($_POST['selected_questions']) ? $_POST['selected_questions'] : '[]';

    $questions_array = json_decode($selected_questions, true);

    if (json_last_error() !== JSON_ERROR_NONE) {
        echo 'Error decoding JSON: ' . json_last_error_msg();
        exit; // Exit if JSON decoding fails
    }

    $xml = new SimpleXMLElement('<?xml version="1.0" encoding="UTF-8"?><quiz></quiz>');

    foreach ($questions_array as $question) {
        $question_typejson = strtolower($question['type']);
        $question_type = '';
        if ($question_typejson === 'multiple choice') {
            $question_type = 'multichoice';
        } elseif ($question_typejson === 'short answer') {
            $question_type = 'shortanswer';
        } elseif ($question_typejson === 'true/false') {
            $question_type = 'truefalse';
        }
        $question_element = $xml->addChild('question');
        $question_element->addAttribute('type', $question_type);

        $name_element = $question_element->addChild('name');
        $name_element->addChild('text', htmlspecialchars($question['question']));

        $questiontext_element = $question_element->addChild('questiontext');
        $questiontext_element->addAttribute('format', 'html');
        $questiontext_element->addChild('text', '<![CDATA[<p>' . htmlspecialchars($question['question']) . '</p>');


        $question_element->addChild('generalfeedback')->addAttribute('format', 'html');
        $question_element->addChild('defaultgrade', '1.0000000');
        $question_element->addChild('penalty', '0.3333333');
        $question_element->addChild('hidden', '0');
        $question_element->addChild('idnumber');

        if ($question_type == 'multichoice') {
            $question_element->addChild('single', 'true');
            $question_element->addChild('shuffleanswers', 'true');
            $question_element->addChild('answernumbering', 'abc');
            $question_element->addChild('showstandardinstruction', '0');

            $correct_feedback = $question_element->addChild('correctfeedback');
            $correct_feedback->addAttribute('format', 'html');
            $correct_feedback->addChild('text', '<![CDATA[<p>Your answer is correct.</p>]]>');

            $partially_correct_feedback = $question_element->addChild('partiallycorrectfeedback');
            $partially_correct_feedback->addAttribute('format', 'html');
            $partially_correct_feedback->addChild('text', '<![CDATA[<p>Your answer is partially correct.</p>]]>');

            $incorrect_feedback = $question_element->addChild('incorrectfeedback');
            $incorrect_feedback->addAttribute('format', 'html');
            $incorrect_feedback->addChild('text', '<![CDATA[<p>Your answer is incorrect.</p>]]>');

            foreach ($question['options'] as $option) {
                $answer = $question_element->addChild('answer');
                $answer->addAttribute('fraction', ($option == $question['correct_answer']) ? '100' : '0');
                $answer->addAttribute('format', 'html');
                $answer->addChild('text', '<![CDATA[<p>' . htmlspecialchars($option) . '</p>');
                $answer->addChild('feedback')->addAttribute('format', 'html');
            }
        } elseif ($question_type == 'shortanswer') {
            $question_element->addChild('usecase', '0');

            $answer = $question_element->addChild('answer');
            $answer->addAttribute('fraction', '100');
            $answer->addAttribute('format', 'moodle_auto_format');
            $answer->addChild('text', htmlspecialchars($question['answer']));
            $answer->addChild('feedback')->addAttribute('format', 'html');
        } elseif ($question_type == 'truefalse') {
            $true_answer = $question_element->addChild('answer');
            $true_answer->addAttribute('fraction', ($question['answer'] == 'true') ? '100' : '0');
            $true_answer->addAttribute('format', 'moodle_auto_format');
            $true_answer->addChild('text', 'true');
            $true_answer->addChild('feedback')->addAttribute('format', 'html');

            $false_answer = $question_element->addChild('answer');
            $false_answer->addAttribute('fraction', ($question['answer'] == 'false') ? '100' : '0');
            $false_answer->addAttribute('format', 'moodle_auto_format');
            $false_answer->addChild('text', 'false');
            $false_answer->addChild('feedback')->addAttribute('format', 'html');
        }
    }

    $desktop_path = '/Users/youssefalamrousy/Downloads';
    $xml_filepath = $desktop_path . '/Moodle_Generated_Questions.xml';
    $xml->asXML($xml_filepath);

    $redirect_url = new moodle_url('/local/questiongenerator/tutorial.php');
    echo json_encode(['redirect' => $redirect_url->out()]);
    exit();

} else {
    echo 'Invalid request method.';
}
