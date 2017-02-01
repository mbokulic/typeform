from . import api
from . import config

api = api.TypeFormAPI(config.API_KEY)
test = api.get_form('K6makx')

print(test.get_questions_texts())
