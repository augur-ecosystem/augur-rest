import flask
from flask import Response
from flask.json import jsonify
from flask_restful import Resource, abort, reqparse
from pony.orm import db_session, commit

from augur import api as augur_api
from augur.serializers import StaffSchema


class AugurStaff(Resource):
    @db_session
    def get(self, staff_id):
        staff = augur_api.get_staff(staff_id)
        if staff:
            schema = StaffSchema()
            return jsonify(schema.dump(staff))
        else:
            return Response("Unable to find staff", status=404)

    @db_session
    def put(self, staff_id):
        staff_props = flask.request.get_json()
        if 'staff' in staff_props:
            try:
                staff = augur_api.get_staff(staff_id)
                if staff:
                    updated_ob = augur_api.update_staff(staff_id, staff_props['staff'])
                    if updated_ob:
                        schema = StaffSchema()
                        return jsonify(schema.dump(updated_ob))
                    else:
                        return Response("Unable to update staff member", status=500)
                else:
                    return Response("Unable to find staff member", status=404)
            except ValueError,e:
                return Response("Add staff failed with this error: %s"%e.message, status=500)
        else:
            return Response("No staff information given", status=500)


class AugurStaffList (Resource):
    @db_session
    def get(self):
        staff = augur_api.get_all_staff(context=None)
        if staff:
            schema = StaffSchema(many=True)
            return jsonify(schema.dump(staff))
        else:
            return Response("Staff lookup failed", status=500)

    @db_session
    def post(self):
        staff_props = flask.request.get_json()
        if 'staff' in staff_props:

            try:
                staff = augur_api.add_staff(staff_props['staff'])
                if staff:
                    return jsonify({"staff_id": staff.id})
                else:
                    return Response("Unable to create staff member", status=500)
            except ValueError,e:
                return Response("Add staff failed with this error: %s"%e.message, status=500)
        else:
            return Response("No staff information given", status=500)