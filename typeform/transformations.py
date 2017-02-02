from . import config
from string import ascii_letters
import re
import unicodedata
import copy

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

    questions = copy.deepcopy(questions)
    result = []

    for q_idx in range(len(questions)):
        increment_counter = True
        append_question = True

        q = questions[q_idx]
        q['typeform_id'] = q['id']
        q['question'] = clean_question_text(q['question'])
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
        q['id'] = create_question_id(idx, q['type'], suffix)

        if(append_question):
            result.append(q)

    return result


def create_question_id(idx, type, suffix=''):
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


def clean_question_text(html):
    # removes unicode codes like \xa0
    clean = unicodedata.normalize('NFKD', html)
    # replaces <br> with line breaks
    clean = re.sub('<br ?/>', '\n', clean)
    # removes html tags
    clean = re.sub('<.*?>', '', clean)
    return(clean)


def questions_to_markdown(questions):
    questions = transform_questions(questions)
    md_list = []
    for q in questions:
        md_list.append(' '.join(['#', q['id']]))
        md_list.append(q['question'] + '\n')
    md_string = '\n'.join(md_list)
    return(md_string)
