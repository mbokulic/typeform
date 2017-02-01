from . import config
from string import ascii_letters
import re

TYPE_PREFIXES = {
    'group': 'g',
    'statement': 's',
    'default': 'q'
}


def transform_questions(questions):
    '''
    formats questions from typeform API
    :param questions: list of raw questions
    :returns: a list of dicts that represent questions for this typeform
    '''
    idx = 0
    choice_id = ''
    letters = list(ascii_letters)

    result = []
    while len(questions) > 0:
        increment_counter = True
        append_question = True

        q = questions.pop(0)
        q['typeform_id'] = q['id']
        q['type'] = parse_question_type(q['typeform_id'])

        suffix = ''
        if('group' in q.keys()):
            suffix = letters.pop(0)
            increment_counter = False

        if(q['type'] == 'group'):
            letters = list(ascii_letters)
            if(not config.KEEP_NONQUESTIONS):
                append_question = False

        if(q['type'] == 'statement'):
            if(not config.KEEP_NONQUESTIONS):
                append_question = False
            increment_counter = False

        if(q['type'] == 'choice(multiple answers)'):
            if(q['field_id'] == choice_id):
                increment_counter = False
                append_question = False
            else:
                choice_id = q['field_id']

        if(increment_counter):
            idx += 1
        q['id'] = get_id_string(idx, q['type'], suffix)

        if(append_question):
            result.append(q)

    return result


def get_id_string(idx, type, suffix=''):
    if(type in TYPE_PREFIXES.keys()):
        prefix = TYPE_PREFIXES[type]
    else:
        prefix = TYPE_PREFIXES['default']
    formatter = prefix + '{:0>2}' + suffix

    return formatter.format(str(idx))


def parse_question_type(id_string):
    match = re.search('[A-z]+', id_string)
    type = id_string[match.start():match.end() - 1]
    if(type == 'list'):
        match = re.search('choice_[0-9]+', id_string)
        if(match):
            type = 'choice(multiple answers)'
        else:
            type = 'choice(single answer)'
    return type