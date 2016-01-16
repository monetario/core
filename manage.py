#!/usr/bin/env python

import os
import sys

from flask.ext.script import Manager, prompt, Shell
from flask.ext.migrate import Migrate, MigrateCommand

from monetario.app import create_app
from monetario.models import App
from monetario.models import User
from monetario.extensions import db

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return {'app': app, 'db': db, 'User': User}

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    import coverage
    cov = coverage.coverage(branch=True, include='rentiko/*')
    cov.start()
    tests = unittest.TestLoader().discover('rentiko.tests')
    unittest.TextTestRunner(verbosity=3).run(tests)
    cov.stop()
    cov.save()
    print("Coverage Summary: ")
    cov.report()
    basedir = os.path.abspath(os.path.dirname(__file__))
    covdir = os.path.join(basedir, 'tmp/coverage')
    cov.html_report(directory=covdir)
    print('HTML version: file://%s/index.html' % covdir)
    cov.erase()


@manager.command
def profile(length=25, profile_dir=None):
    """Start the application under the code profiler."""
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def create_api_app():
    """
    Create an API application with secret key.
    """

    name = prompt('API application name')

    api_app = App(name=name)
    db.session.add(api_app)
    db.session.commit()

    api_app.secret = api_app.generate_auth_token(expires_in=157680000)
    db.session.add(api_app)
    db.session.commit()

    sys.exit('\nApp "{}" was created with secret "{}"'.format(name, api_app.secret))


if __name__ == '__main__':
    manager.run()
