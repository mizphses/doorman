"""This is the program to make GraphQL queries working"""

from json import dumps as json_dumps, loads as json_load
from graphene import (
    ObjectType,
    Mutation,
    String,
    Schema,
    NonNull,
    Field,
    List,
    DateTime,
)
from connection import get_connection

with open("config.json", "r", encoding="utf-8") as f:
    config = json_load(f.read())


class Room(ObjectType):
    """
    This class defines the room information object
    """

    roomid = String()
    roomname = String()
    note = String()


class ReservationRoom(ObjectType):
    """
    This class defines the room reservation information object
    """

    roomid = String()
    userid = String()
    start_time = DateTime()
    end_time = DateTime()
    type_of_usage = String()
    allowed_users = List(String)
    note = String()


class RegisterNewRoom(Mutation):
    """
    This class defines the mutation of registering new room
    """

    class Arguments:
        """
        Arguments
        """

        roomid = String()
        roomname = String()
        note = String()

    room = Field(Room)

    def mutate(self, info, roomid, roomname, note):
        """
        Put things into config.json
        """
        if roomid in [obj["roomid"] for obj in config["rooms"]]:
            raise Exception("Room ID already exists.")
        else:
            config["rooms"].append_time(
                {"roomid": roomid, "roomname": roomname, "note": note}
            )
            with open("config.json", "w", encoding="utf-8") as config_file:
                config_file.write(json_dumps(config))
        return RegisterNewRoom(room=config["rooms"][-1])


class DropRoom(Mutation):
    """
    This class is to delete room info from config.json
    """

    class Arguments:
        """
        Arguments
        """

        roomid = String()

    room = Field(Room)
    obj_to_delete = {}

    def mutate(self, info, roomid):
        """
        Delete things of config.json
        """
        for obj_to_del in config["rooms"]:
            if obj_to_del["roomid"] == roomid:
                obj_to_delete = obj_to_del
        config["rooms"].remove(obj_to_delete)
        with open("config.json", "w") as f:
            f.write(json_dumps(config))
        return DropRoom(room=obj_to_del)


class MakeReservation(Mutation):
    """
    Register reservation data
    """

    class Arguments:
        """
        Arguments
        """

        roomid = NonNull(String)
        userid = NonNull(String)
        start_time = NonNull(DateTime)
        end_time = NonNull(DateTime)
        type_of_usage = NonNull(String)
        allowed_users = List(String)
        note = String()

    reservation = Field(ReservationRoom)

    def mutate(
        self,
        info,
        roomid,
        userid,
        start_time,
        end_time,
        type_of_usage,
        allowed_users,
        note,
    ):
        """
        This function will check room usage and register reservation data
        """
        if roomid not in [obj["roomid"] for obj in config["rooms"]]:
            raise Exception("Room ID does not exist.")
        elif type_of_usage not in ["unlocked", "require_id"]:
            raise Exception("Room ID does not exist.")
        elif type_of_usage == "require_id":
            raise Exception("Room ID does not exist.")
        else:
            rsv_data = {
                "roomid": roomid,
                "userid": userid,
                "start_time": start_time,
                "end_time": end_time,
                "type_of_usage": type_of_usage,
                "allowed_users": json_dumps(allowed_users),
                "note": note,
            }
            with get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(
                        "INSERT INTO reservations (roomid, userid, start_time, end_time, type_of_usage, allowed_users, note) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                        (
                            rsv_data["roomid"],
                            rsv_data["userid"],
                            rsv_data["start_time"],
                            rsv_data["end_time"],
                            rsv_data["type_of_usage"],
                            rsv_data["allowed_users"],
                            rsv_data["note"],
                        ),
                    )
                conn.commit()
        return MakeReservation(
            reservation={
                "roomid": roomid,
                "userid": userid,
                "start_time": start_time,
                "end_time": end_time,
                "note": note,
            }
        )


class DoMutation(ObjectType):
    """
    Class for execution of mutation
    """

    register_new_room = RegisterNewRoom.Field()
    drop_room = DropRoom.Field()
    make_reservation = MakeReservation.Field()


class Query(ObjectType):
    """
    Queries
    """

    rooms = List(Room)
    goodbye = String()
    reservation = List(ReservationRoom)

    def resolve_rooms(self, info):
        """
        Returns room list
        """
        return config["rooms"]

    def resolve_reservation(self, info):
        """
        Returns reservation list
        """
        with get_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute(
                    "SELECT roomid, userid, start_time, end_time, type_of_usage, allowed_users, note, approval, created_at, updated_at FROM reservations WHERE userid = '21B2125025E'"
                )
                columns = [
                    "roomid",
                    "userid",
                    "start_time",
                    "end_time",
                    "type_of_usage",
                    "allowed_users",
                    "note",
                    "approval",
                    "created_at",
                    "updated_at",
                ]
                contents = cursor.fetchall()
                return [dict(zip(columns, row)) for row in contents]


schema = Schema(query=Query, mutation=DoMutation)
