FROM python:3.7.0
RUN pip install pipenv
COPY Pipfile Pipfile.lock /code/
WORKDIR /code
RUN pipenv install
COPY . /code
CMD pipenv run python -u main.py
