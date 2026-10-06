from arena.client import ServiceError
from battleship.placement import PlacementError, check_placement, to_index

MAX_MOVES = 500


class Player:
    def __init__(self, service):
        self.service = service
        self.name = service.name
        self.session_id = None
        self.fleet = []
        self.taken = set()
        self.fired = set()


def start(player):
    session_id, fleet = player.service.start_game()
    check_placement(fleet)
    player.session_id = session_id
    player.fleet = [set(ship) for ship in fleet]


def expected_result(player, coordinate):
    for ship in player.fleet:
        if coordinate in ship:
            return "killed" if ship <= player.taken | {coordinate} else "hit"
    return "miss"


def is_sunk(player):
    return all(ship <= player.taken for ship in player.fleet)


def finish(players, loser, reason, log):
    for player in players:
        if player.session_id is not None:
            try:
                player.service.close(player.session_id)
            except ServiceError as error:
                log(f"сессия {player.name} не закрылась: {error}")

    if loser is None:
        log(f"ничья: {reason}")
        return {"winner": None, "loser": None, "reason": reason}

    winner = next(player for player in players if player is not loser)
    log(f"победил {winner.name}, у {loser.name} — {reason}")
    return {"winner": winner.name, "loser": loser.name, "reason": reason}


def play(first, second, log=print):
    players = [Player(first), Player(second)]
    for player in players:
        try:
            start(player)
        except PlacementError as error:
            return finish(players, player, f"невалидная расстановка ({error})", log)
        except ServiceError as error:
            return finish(players, player, str(error), log)

    attacker, defender = players
    for _ in range(MAX_MOVES):
        try:
            coordinate = attacker.service.ask_shot(attacker.session_id)
            to_index(coordinate)
        except ServiceError as error:
            return finish(players, attacker, str(error), log)
        except PlacementError:
            return finish(players, attacker, f"выстрел вне поля ({coordinate})", log)

        if coordinate in attacker.fired:
            log(f"{attacker.name} повторяет выстрел {coordinate}, ход переходит")
            try:
                repeated = defender.service.ask_opponent_shot(defender.session_id, coordinate)
            except ServiceError as error:
                return finish(players, defender, str(error), log)
            try:
                attacker.service.send_result(attacker.session_id, repeated)
            except ServiceError as error:
                return finish(players, attacker, str(error), log)

            attacker, defender = defender, attacker
            continue

        try:
            result = defender.service.ask_opponent_shot(defender.session_id, coordinate)
        except ServiceError as error:
            return finish(players, defender, str(error), log)

        honest = expected_result(defender, coordinate)
        if result != honest:
            return finish(players, defender, f"ответ {result} вместо {honest} на {coordinate}", log)

        try:
            attacker.service.send_result(attacker.session_id, result)
        except ServiceError as error:
            return finish(players, attacker, str(error), log)

        attacker.fired.add(coordinate)
        defender.taken.add(coordinate)
        log(f"{attacker.name} бьёт {coordinate}: {result}")

        if is_sunk(defender):
            return finish(players, defender, "флот потоплен", log)
        if result == "miss":
            attacker, defender = defender, attacker

    return finish(players, None, f"партия не закончилась за {MAX_MOVES} ходов", log)
