# typeform
A python wrapper for the typeform API

#Installation
Clone the repo

```bash
git clone https://github.com/WarmongeR1/typeformPython.git

# In the base directory run:
python setup.py install
```

#Usage

## Instantiating a form object

```python
from typeform import TypeFormAPI
api = TypeFormAPI(API_KEY)
exampleForm = api.get_form(formKey)
```

## Retrieving questions from a form object
```python
# Returns a dictionary of the form {questionToken: Question Text}
questionDict = exampleFrom.get_questions()

# returns a transformation questions list
# that has numbered IDs of the type "q01"
# and more sensible type names
questionList = exampleFrom.get_transformed_questions()

# returns a markdown string with question IDs as headers and question text as the text
questionList = exampleFrom.questions_to_markdown()
```


## Retrieving responses from a form object

```python
# Returns all responses in form: {responseToken: {questionToken: answerString....}}
responseDict = exampleForm.get_all_completed_responses()
```

## Get average rating of a rating or opinion question

```python
rating = exampleForm.get_average_rating(questionToken)
```

## Contributing

1. Fork it
2. Create your feature branch (`git checkout -b my-new-feature`)
3. Commit your changes (`git commit -am 'Add some feature'`)
4. Push to the branch (`git push origin my-new-feature`)
5. Create a new Pull Request
