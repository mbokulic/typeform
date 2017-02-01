# -*- coding: utf-8 -*-

import requests
import urllib
import json
from .form import TypeForm


class TypeFormAPI:
    """
    Class representing one connection to typeform
    Parameters: API_KEY - retrieved from your typeform account settings
    """

    def __init__(self, api_key):
        self.API_KEY = api_key
        self.redirect_url = "https://api.typeform.com/login/"

    def get_form(self, form_key):
        """
        Returns a form object which can be queried to get
        responses to typeforms
        Parameters: formKey - Check the typeform API docs for info
        """
        # TODO implement exception for no network etc.
        api_url = "https://api.typeform.com/v0/form/{0}?key={1}".format(
            form_key, self.API_KEY)
        response = requests.get(api_url)
        status_code = response.status_code
        if status_code == 200 and response.url != self.redirect_url:
            return TypeForm(response.json())
        else:
            self.raise_error(status_code)

    def get_form_list(self):
        '''
        returns the forms available for this self.API_KEY
        :returns: list of dictionaries with keys "name" and "id"
        '''

        api_url = 'https://api.typeform.com/v1/forms?key={}'.format(
            self.API_KEY)
        response = requests.get(api_url)
        status_code = response.status_code
        if(status_code == 200 and response.url != self.redirect_url):
            json_str = response.content.decode('utf8')
            form_list = json.loads(json_str)
            return(form_list)
        else:
            self.raise_error(status_code)

    def print_form_list(self):
        '''
        prints a formatted list of form names and IDs
        that are available for this self.API_KEY
        '''
        form_list = self.get_form_list()

        id_length = 6  # form IDs have 6 chars
        max_length_name = 30  # names longer than this will be truncated

        truncate = '{:.' + str(max_length_name) + '}'
        pad = '{:' + str(max_length_name) + '}'

        print(pad.format('NAME') + ' | ' + 'ID')
        print('-' * (id_length + max_length_name + 3))

        for form in form_list:
            formatted = truncate.format(form['name'])
            formatted = pad.format(formatted)
            print(formatted + ' | ' + form['id'])

    def raise_error(self, status_code):
        if(status_code == 400):
            raise ValueError('API call error: invalid date in query')
        elif(status_code == 403):
            raise ValueError('API call error: expired or invalid token')
        elif(status_code == 404):
            raise ValueError('API call error: invalid typeform ID')
        elif(status_code == 429):
            raise ValueError('API call error: request limit reached')
        else:
            raise ValueError('API call error: unknown status code {}'.format(
                str(status_code)))
