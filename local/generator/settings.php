<?php
defined('MOODLE_INTERNAL') || die();

if ($hassiteconfig){
    $ADMIN ->add('root', new admin_category('generator', get_string('pluginname','local_generator')));
    $ADMIN ->add('generator', new admin_externalpage('userdata',get_string('userdata','local_generator'),
    new moodle_url('/local/generator/userdata.php')));

    $ADMIN ->add('generator', new admin_externalpage('usermetdata',get_string('usermetdata','local_generator'),
    new moodle_url('/local/generator/metdata.php')));
}