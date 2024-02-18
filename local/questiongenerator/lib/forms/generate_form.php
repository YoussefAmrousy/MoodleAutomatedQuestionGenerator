<?php

defined('MOODLE_INTERNAL') || die();

require_once($CFG->libdir . '/formslib.php');

class generate_form extends moodleform {
    public function definition() {
        $mform = $this->_form;

        $options = array(1 => 1, 2 => 2, 3 => 3, 4 => 4); 
        $mform->addElement('select', 'questionsnumber', get_string('questionsnumber', 'local_questiongenerator'), $options);
        $mform->addHelpButton('questionsnumber', 'questionsnumber', 'local_questiongenerator');
        $mform->setType('questionsnumber', PARAM_INT);

        $questionTypes = array('mcq' => 'Multiple Choice', 'truefalse' => 'True/False', 'shortanswer' => 'Short Answer');
        $mform->addElement('select', 'questiontype', get_string('questiontype', 'local_questiongenerator'), $questionTypes);
        $mform->addHelpButton('questiontype', 'questiontype', 'local_questiongenerator');
        $mform->setType('questiontype', PARAM_TEXT);

        $this->add_action_buttons(true, get_string('generatebutton', 'local_questiongenerator'));
    }
}
