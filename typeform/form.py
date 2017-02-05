# -*- coding: utf-8 -*-

from . import config
from datetime import datetime
from collections import OrderedDict
import copy
import unicodedata
from string import ascii_letters
import re


class TypeForm:
    """
    Class representing one form and its associated responses
    Instatiated through typeform object
    """

    def __init__(self, data):
        self.data = data

    def get_questions(self):
        """
        returns the raw questions output from typeform API
        :returns: a list of dicts that represent questions for this typeform

        """
        # using deepcopy since I don't want the changes to the returned
        # object to change self.data
        questions = copy.deepcopy(self.data["questions"])
        return questions

    def get_questions_texts(self):
        """
        Returns a dictionary of the form {questionToken: Question Text}
        A question token is a unique key for the question
        """
        questions_dict = OrderedDict()
        questions = self.data["questions"]
        for question in questions:
            questions_dict[question["id"]] = question['question']
        return questions_dict

    def get_transformed_questions(self):
        """
        formats questions from typeform API
        :returns: a list of dicts that represent questions for this typeform
        """
        questions = self.get_questions()
        return self.transform_questions(questions)

    def transform_questions(self, questions):
        '''
        formats questions from typeform API
        :param questions: list of raw questions
        :returns: a list of dicts that represent questions for this typeform
        '''
        idx = 0
        choice_id = ''
        letters = list(ascii_letters)
        result = []

        for q_idx in range(len(questions)):
            increment_counter = True
            append_question = True

            q = questions[q_idx]
            q['typeform_id'] = q['id']
            q['question'] = self.clean_question_text(q['question'])
            q['type'] = self.parse_question_type(q['typeform_id'])

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
            q['id'] = self.create_question_id(idx, q['type'], suffix)

            if(append_question):
                result.append(q)

        return result

    def create_question_id(self, idx, type, suffix=''):
        if(type in config.TYPE_PREFIXES.keys()):
            prefix = config.TYPE_PREFIXES[type]
        else:
            prefix = config.TYPE_PREFIXES['default']
        formatter = prefix + '{:0>2}' + suffix

        return formatter.format(str(idx))

    def parse_question_type(self, id_string):
        match = re.search('[A-z]+', id_string)
        type = id_string[match.start():match.end() - 1]
        if(type in config.ALT_TYPES.keys()):
            type = config.ALT_TYPES[type]
        if(type == 'list'):
            if('list_multiple' in config.ALT_TYPES.keys() and
               'list_single' in config.ALT_TYPES.keys()):
                match = re.search('choice_[0-9]+', id_string)
                if(match):
                    type = config.ALT_TYPES['list_multiple']
                else:
                    type = config.ALT_TYPES['list_single']
        return type

    def clean_question_text(self, html):
        # removes unicode codes like \xa0
        clean = unicodedata.normalize('NFKD', html)
        # replaces <br> with line breaks
        clean = re.sub('<br ?/>', '\n', clean)
        # removes html tags
        clean = re.sub('<.*?>', '', clean)
        return(clean)

    def questions_to_markdown(self):
        questions = self.get_transformed_questions()
        md_list = []
        for q in questions:
            md_list.append(' '.join(['#', q['id']]))
            md_list.append(q['question'] + '\n')
        md_string = '\n'.join(md_list)
        return(md_string)

    def get_all_completed_responses(self):
        """
        Returns all responses in form:
        {responseToken: {questionToken: answerString....}}
        """
        return self.get_completed_responses_before(datetime.now())

    def get_completed_responses_before(self, until_time):
        """
        Returns responses before untilTime in form:
        {responseToken: {questionToken: answerString....}}
        Parameters: untilTime - a datetime object
        """
        answer = OrderedDict()
        responses = self.data["responses"]
        for response in responses:
            if response["completed"] == "1" \
                    and datetime.strptime(
                        response["metadata"]["date_submit"],
                        "%Y-%m-%d %H:%M:%S"
                    ) < until_time:
                answer[response["token"]] = response["answers"]
        return answer

    def get_average_rating(self, question_token):
        """
        Returns the average rating of a rating question from all responses
        Parameters: questionToken
        """
        # TODO throw exception if not a rating question
        answers = self.get_answers_by_question(question_token)
        total = 0.0
        count = 0
        for response in answers:
            total += int(response)
            count += 1
        return total / count

    def get_answers_by_question(self, question_token):
        """
        Returns all answers to a question as a list
        Parameters: questionToken
        """
        return self.get_answers_by_question_before(question_token,
                                                   datetime.now())

    def get_answers_by_question_before(self, question_token, until_time):
        """
        Returns answers to a question before untilTime
        """
        # Responses is a dict of form
        # {responseToken: {questionToken: answer, questionToken: answer ...}}
        answers = []
        responses = self.get_completed_responses_before(until_time)
        for response in responses:
            answers.append(responses[response][question_token])
        return answers
