import flask
from flask.json import jsonify
from flask_restful import Resource, abort, reqparse
from pony.orm import db_session, commit

from augur import api as augur_api
from augur.serializers import TeamSchema, StaffSchema


class AugurTeam(Resource):
    @db_session
    def get(self, team_id):
        team = augur_api.get_team_by_id(team_id)
        if team:
            schema = TeamSchema()
            return schema.dump(team)


class AugurTeamMemberList(Resource):
    """
    This resource is used to manipulate members that are part of a team.
        GET: /team/<team_id>/members --- Returns all members of the team
        PUT: /team/<team_id>/members --- Adds the list of staff in body (json) to team
    """
    @db_session
    def get(self, team_id):
        team = augur_api.get_team_by_id(team_id)
        if team:
            schema = StaffSchema(many=True)
            return jsonify(schema.dump(team.members))

    @db_session
    def put(self, team_id):
        team = augur_api.get_team_by_id(team_id)
        staff_list = flask.request.get_json()
        if 'staff' in staff_list:
            augur_api.add_staff_to_team(team, staff_list['staff'])

            commit()

            # reload team
            team = augur_api.get_team_by_id(team_id)

            schema = TeamSchema()
            return jsonify(schema.dump(team))


class AugurTeamMember(Resource):
    """
    This resource is used to manipulate members that are part of a team.
        DELETE: /team/<team_id>/members/<staff_id> --- Removes the given staff ID
    """
    @db_session
    def delete(self, team_id, staff_id):
        team = augur_api.get_team_by_id(team_id)

        if not team:
            abort(404, "Team not found")
        else:
            staff = team.members.select(lambda s: s.id == staff_id).first()
            if staff:
                team.members.remove(staff)
            else:
                abort(404, "Staff not found in given team")


class AugurTeamList(Resource):
    @db_session
    def get(self):
        teams = augur_api.get_teams()
        if teams:
            schema = TeamSchema(many=True)
            return schema.dump(teams)

    @db_session
    def post(self):
        team_props = flask.request.get_json()
        if 'team' in team_props:
            team = augur_api.add_team(team_props['team'])
            if team:
                return {"team_id": team.id}
            else:
                abort(500, message="Unable to create team")
        else:
            abort(500, message="No team information given")
