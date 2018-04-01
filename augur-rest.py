import os
import json
from flask import Flask
import flask_restful
from augur import settings as augur_settings
from augur import db as augur_db
import api as augur_api

##############
# Configure Flask
##############
app = Flask(__name__)
api = flask_restful.Api(app)

##############
# Configure Augur
##############
augur_conf = None
augur_conf_path = os.environ.get('AUGUR_CONF_FILE','./augur.conf.json')
try:
    with open(augur_conf_path,'r') as f:
        augur_conf = json.load(f)
except IOError,e:
    app.logger.error("Unable to open augur configuration file: %s" % (augur_conf_path or "None given"))
    exit(1)

# Augur loads settings from environment variables so these have to be set prior to
#   calling load_settings.  The augur readme lists the configuration options.
augur_settings.load_settings(env=augur_conf)

# Initdb configures pony, creates the base db object from which model objects are derived and establishes
#   a connection to the database.
augur_db.init_db()

##############
# Configure Routes
##############

@app.route('/')
def hello_world():
    return 'Hello World!'


#####################
# Team Related APIs
#####################
api.add_resource(augur_api.AugurTeamMember, '/team/<int:team_id>/member/<int:staff_id>')
api.add_resource(augur_api.AugurTeamMemberList, '/team/<int:team_id>/members')
api.add_resource(augur_api.AugurTeam, '/team/<int:team_id>')
api.add_resource(augur_api.AugurTeamList, '/teams')

#####################
# Staff Related APIs
#####################
api.add_resource(augur_api.AugurStaffList, '/staff')
api.add_resource(augur_api.AugurStaff, '/staff/<int:staff_id>')

if __name__ == '__main__':
    app.run()
