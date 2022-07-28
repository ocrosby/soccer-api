# Soccer API

A restful API for soccer information.

Create a virtual environment and store it's tools in the "env" folder.

```bash
> python3 -m venv env
```

## Running a virtual environment

To activate your virtual environment, from the directory of your folder, type the following command this will activate our virtual environment in the “env” folder as we demonstrated in the previous step.

```bash
> source env/bin/activate
> python3 -m pip install --upgrade pip
```

If you have successfully activated your virtual environment, you should see the (env) word indicating that we are working in a virtual environment.

The second command serves to upgrade the pip installer in the virtual environment.

Installing Flask

```bash
> pip install flask
```

Generating a requirements.txt file

```bash
(env)$ pip freeze > requirements.txt
```

You can run your application by opening your terminal with the virtual environment active and run the following command line:

```bash
(env)$ flask run
```

Activating a Virtual Env Session

```bash
> ./env/bin/activate
```

Deactivating a Virtual Env Session

```bash
(env) deactivate
```

Running in Debug Mode

```bash
> export FLASK_DEBUG=1
> flask run
```

Specifying the Startup File

```bash
> export FLASK_APP=wsgi.py
> flask run
```

## References

* [Beginners Guide on Installing Flask](https://www.section.io/engineering-education/complete-guide-on-installing-flask-for-beginners/)
* [Structuring Large Applications](https://www.section.io/engineering-education/structuring-large-applications-with-blueprints-and-application-factory-in-flask/)
* [Flask Blueprint Architect](https://realpython.com/flask-blueprint/)
* [Flask Restful](https://dev.to/paurakhsharma/flask-rest-api-part-2-better-structure-with-blueprint-and-flask-restful-2n93)
* [Flask Caching](https://flask-caching.readthedocs.io/en/latest/)

[![Coverage Status](https://coveralls.io/repos/github/ocrosby/soccer-api/badge.svg?branch=main)](https://coveralls.io/github/ocrosby/soccer-api?branch=main)
