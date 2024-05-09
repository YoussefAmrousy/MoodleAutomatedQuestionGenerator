<?php

defined('MOODLE_INTERNAL') || die();

require_once ($CFG->libdir . '/formslib.php');

class generate_question extends moodleform
{
    private $mform = null;
    public function definition()
    {
        $this->mform = $this->_form;

        $options = array(1 => 1, 2 => 2, 3 => 3, 4 => 4);
        $this->mform->addElement('select', 'questionsnumber', get_string('questionsnumber', 'local_questiongenerator'), $options);
        $this->mform->addHelpButton('questionsnumber', 'questionsnumber', 'local_questiongenerator');
        $this->mform->setType('questionsnumber', PARAM_INT);

        $questionTypes = array('mcq' => 'Multiple Choice', 'truefalse' => 'True/False', 'shortanswer' => 'Short Answer');
        $this->mform->addElement('select', 'questiontype', get_string('questiontype', 'local_questiongenerator'), $questionTypes);
        $this->mform->addHelpButton('questiontype', 'questiontype', 'local_questiongenerator');
        $this->mform->setType('questiontype', PARAM_TEXT);

        $difficulties = array('Easy' => 'Easy', 'Medium' => 'Medium', 'Hard' => 'Hard');
        $this->mform->addElement('select', 'difficulty', get_string('difficulty', 'local_questiongenerator'), $difficulties);
        $this->mform->addHelpButton('difficulty', 'difficulty', 'local_questiongenerator');
        $this->mform->setType('difficulty', PARAM_TEXT);

        $this->add_action_buttons(false, get_string('generatebutton', 'local_questiongenerator'));
    }
}
