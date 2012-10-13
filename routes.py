import bottle
import settings
import subprocess
from cork import Cork
import utils
import beaker.middleware
import json

auth = Cork('auth')

@bottle.route('/')
def index():
    return 'HAlchemy Proxy v0.1'

@bottle.route('/stats')
@utils.require(role='admin', auth=auth)
def get_stats():
    stat_parser = utils.HAStatParser(utils.query_haproxy("show stat"))
    headers, rows = stat_parser.parse_to_object()
    return json.dumps({'headers' : headers, 'rows' : rows})

@bottle.route('/<backend>/<server>/down')
@utils.require(role='admin', auth=auth)
def take_down(backend, server):
    return utils.query_haproxy('disable server {0}/{1}'.format(backend, server))

@bottle.route('/<backend>/<server>/up')
@utils.require(role='admin', auth=auth)
def bring_up(backend, server):
    return utils.query_haproxy('enable server {0}/{1}'.format(backend, server))

@bottle.route('/logout')
def logout():
    auth.logout(success_redirect="/", fail_redirect="/")

session_opts = {
    'session.type': 'cookie',
    'session.validate_key': True,
}

# Setup Beaker middleware to handle sessions and cookies
webapp = bottle.default_app()
webapp = beaker.middleware.SessionMiddleware(webapp, session_opts)

bottle.run(app=webapp, host=settings.HOST, port=settings.PORT, debug=settings.DEBUG, reloader=True)