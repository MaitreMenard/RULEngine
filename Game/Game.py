import math

from . import Referee
from ..Util.Pose import Pose, Position


class Game(object):
    def __init__(self, field, referee, blue_team, yellow_team, blue_team_strategy):
        self.field = field
        self.referee = referee
        self.blue_team = blue_team
        self.yellow_team = yellow_team
        self.blue_team_strategy = blue_team_strategy

    def update_strategies(self):
        state = self.referee.command.name
        if state == "HALT":
            self.blue_team_strategy.on_halt()

        elif state == "NORMAL_START":
            self.blue_team_strategy.on_start()

        elif state == "STOP":
            self.blue_team_strategy.on_stop()

    def get_commands(self):
        blue_team_commands = self._get_blue_team_commands()

        self.blue_team_strategy.commands.clear()

        return blue_team_commands

    def _get_blue_team_commands(self):
        blue_team_commands = self.blue_team_strategy.commands
        blue_team_commands = self._remove_commands_from_opponent_team(blue_team_commands, self.yellow_team)
        return blue_team_commands

    @staticmethod
    def _remove_commands_from_opponent_team(commands, opponent_team):
        final_commands = []
        for command in commands:
            # if command.team != opponent_team:
            #     final_commands.append(command)
            final_commands.append(command)
        return final_commands

    def update_game_state(self, referee_command):
        blue_team = referee_command.teams[0]
        self.blue_team.score = blue_team.goalie_count
        yellow_team = referee_command.teams[0]
        self.yellow_team.score = yellow_team.goalie_count

        command = Referee.Command(referee_command.command.name)
        self.referee.command = command

        # TODO: Correctly update the referee with the data from the referee_command

    def update_players_and_ball(self, vision_frame):
        self._update_ball(vision_frame)
        self._update_players(vision_frame)

    def _update_ball(self, vision_frame):
        ball_position = Position(vision_frame.balls[0].position.x, vision_frame.balls[0].position.y,
                                 vision_frame.balls[0].position.z)
        self.field.move_ball(ball_position)

    def _update_players(self, vision_frame):
        blue_team = vision_frame.teams[0]
        yellow_team = vision_frame.teams[1]

        self._update_players_of_team(blue_team.robots, self.blue_team)
        self._update_players_of_team(yellow_team.robots, self.yellow_team)

    @staticmethod
    def _update_players_of_team(players, team):
        for player in players:
            player_position = Position(player.pose.coord.x, player.pose.coord.y, player.pose.coord.z)
            player_orientation = (player.pose.orientation * 180) / math.pi
            player_pose = Pose(player_position, player_orientation)
            team.move_and_rotate_player(player.robot_id, player_pose)
