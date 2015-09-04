#!/usr/bin/env python
import os
from flask.ext.script import Manager, Shell
from flask.ext.migrate import Migrate

from monetario.app import create_app
from monetario.extensions import db

app = create_app()
manager = Manager(app)
migrate = Migrate(app, db)


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


if __name__ == '__main__':
    manager.run()
