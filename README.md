# InstiApp
Backend API in Django for the to-be comprehensive app for managing, finding and enjoying life at Indian Institute of Technology, Bombay!

[![TravisCI](https://api.travis-ci.org/wncc/IITBapp.svg?branch=master)](https://travis-ci.org/wncc/IITBapp)
[![codecov](https://codecov.io/gh/wncc/IITBapp/branch/master/graph/badge.svg)](https://codecov.io/gh/wncc/IITBapp)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/7e6a386dbec649c99aa6a10218cc3768)](https://www.codacy.com/app/pulsejet/IITBapp?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=wncc/IITBapp&amp;utm_campaign=Badge_Grade)
[![Requirements Status](https://requires.io/github/wncc/IITBapp/requirements.svg?branch=master)](https://requires.io/github/wncc/IITBapp/requirements/?branch=master)

Google's [Python Style Guide](https://google.github.io/styleguide/pyguide.html) is followed upto a certain extent in all modules.

Master branch of this repository is continuously deployed at [staging](https://temp-iitb.radialapps.com/).

### Documentation
Static OpenAPI specification can be found at the [project page](https://wncc.github.io/IITBapp/), at [Apiary](https://instiapp.docs.apiary.io/) or at `http://server/docs/`

If you are modifying the API, make sure you regenerate `docs` by running `python manage.py swagger`

### Contributing
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
