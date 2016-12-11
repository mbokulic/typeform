# -*- coding: utf-8 -*-

from datetime import datetime
from collections import OrderedDict

class TypeForm:
    """
    Class representing one form and its associated responses
    Instatiated through typeform object
    """

    def __init__(self, json):
        self.json = json

    def get_questions(self):
        """
        Returns a dictionary of the form {questionToken: Question Text}
        A question token is a unique key for the question
        """
        questions_dict = OrderedDict()
        questions = self.json["questions"]
        for question in questions:
            questions_dict[question["id"]] = question
        return questions_dict

    def get_questions_texts(self):
        """
        Returns a dictionary of the form {questionToken: Question Text}
        A question token is a unique key for the question
        """
        questions_dict = OrderedDict()
        questions = self.json["questions"]
        for question in questions:
            questions_dict[question["id"]] = question['question']
        return questions_dict

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
        responses = self.json["responses"]
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
