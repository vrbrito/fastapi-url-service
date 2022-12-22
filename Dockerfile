FROM amazon/aws-lambda-python:3.9

# Install python dependencies
RUN python -m pip install --upgrade pip
RUN pip install poetry
RUN poetry config virtualenvs.create false
COPY server/pyproject.toml server/poetry.lock /var/task/
RUN poetry install --only main

# Copy files
COPY server/src/app /var/task/app

# Expose port
EXPOSE 8080

# Define entrypoint
CMD ["app.main.handler"]
