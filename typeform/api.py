# -*- coding: utf-8 -*-

import requests
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
