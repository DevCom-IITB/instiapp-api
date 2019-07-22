# InstiApp
API in Django for InstiApp, the one platform for all student activities at Indian Institute of Technology, Bombay! InstiApp's features include upcoming events, placement blog, news and general information on every active club/body in the Institute.

[![InstiApp](https://insti.app/instiapp-badge-gh.svg)](https://insti.app)
[![TravisCI](https://api.travis-ci.org/wncc/IITBapp.svg?branch=master)](https://travis-ci.org/wncc/IITBapp)
[![CircleCI](https://circleci.com/gh/wncc/IITBapp.svg?style=shield)](https://circleci.com/gh/wncc/IITBapp)

[![codecov](https://codecov.io/gh/wncc/IITBapp/branch/master/graph/badge.svg)](https://codecov.io/gh/wncc/IITBapp)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7e6a386dbec649c99aa6a10218cc3768)](https://www.codacy.com/app/pulsejet/IITBapp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=wncc/IITBapp&amp;utm_campaign=Badge_Grade)
[![Requirements Status](https://requires.io/github/wncc/IITBapp/requirements.svg?branch=master)](https://requires.io/github/wncc/IITBapp/requirements/?branch=master)
[![GitHub license](https://img.shields.io/github/license/wncc/IITBapp.svg)](https://github.com/wncc/IITBapp/blob/master/LICENSE)

## Setup
To setup dependenices, make a new `virtualenv`, activate it and run `pip install -r requirements.txt`. Then you can run
* `python manage.py migrate` to create a new database.
* `python manage.py createsuperuser` will let you create a new user to use the admin panel for testing.
* `python manage.py runserver` to start a local server.
* `flake8` to lint with `flake8`.
* `pylint_runner` to check for code style and other errors statically with `pylint` in all files.

It is recommended to set up your IDE with both `pylint` and `flake8`, since these will cause the CircleCI build to fail. Google's [Python Style Guide](https://google.github.io/styleguide/pyguide.html) is followed upto a certain extent in all modules.

## Running Tests
Tests can be run in two configurations:
### Without Celery
This is the recommended and default configuration, and should suffice for all developmental purposes except if you are working with async tasks or notifications. Simply use `python manage.py test --settings backend.settings_test` to run automated tests.
### With Celery
This is the default configuration for CircleCI builds. To test under this configuration, start a local PostgresQL and RabbitMQ server, and an instance of celery in background with `celery -A backend worker --pool=solo -l info`. Once celery is processing background tasks, you can run tests as `python manage.py test --settings backend.settings_test --keepdb`, ensuring that the database `test_instiapp` is created in postgres beforehand. The following environment variables must be set:
* `DJANGO_SETTINGS_MODULE` to `backend.settings_test`
* `NO_CELERY` to `false`
### FTS
Full-Text Search is implemented with [Sonic](https://github.com/valeriansaliou/sonic). To set up, install `cargo` and `sonic` and start it on `localhost`. Then set the `USE_SONIC` setting to `True`.

## Documentation
Static OpenAPI specification can be found at the [project page](https://wncc.github.io/IITBapp/), at [Apiary](https://instiapp.docs.apiary.io/) or at `http://server/api/docs/`

If you are modifying the API, make sure you regenerate `docs` by running `python manage.py swagger`

## Contributing
Pull requests are welcome, but make sure the following criteria are satisfied
* If you are (possibly) breaking an existing feature, state this explicitly in the PR description
* Commit messages should be in present tense, descriptive and relevant, closely following the [GNOME Commit Message Guidelines](https://wiki.gnome.org/Git/CommitMessages). Adding a tag to the message is optional (for now). Commits should not have git tags unless they indicate a version change.
* Documentation should be updated when the API is modified
* All required status checks must pass. Barring exceptional cases, relevant tests should be added/updated whenever necessary.
* Barring exceptional cases, Codacy should not report any new issues
* Follow the general style of the project. Badly written or undocumented code might be rejected
* If you are proposing a new model or modifications to an existing one, create an issue first, explaining why it is useful
* Outdated, unsupported or closed-source libraries should not be used
* Be nice!
