import httpx

TIMEOUT = 1.0
RESULTS = ("miss", "hit", "killed")


class ServiceError(Exception):
    pass


class Service:
    def __init__(self, name, url=None, client=None):
        self.name = name
        self.client = client or httpx.Client(base_url=url, timeout=TIMEOUT)

    def post(self, path, expected, body=None):
        try:
            response = self.client.post(path, json=body)
        except httpx.TimeoutException:
            raise ServiceError(f"{self.name}: ответ дольше {TIMEOUT} секунды")
        except httpx.HTTPError as error:
            raise ServiceError(f"{self.name}: сервис недоступен ({error})")

        if response.status_code != expected:
            raise ServiceError(f"{self.name}: код {response.status_code} вместо {expected} на {path}")

        try:
            return response.json()
        except ValueError:
            raise ServiceError(f"{self.name}: ответ не в формате JSON")

    def start_game(self):
        body = self.post("/game", 201)
        try:
            return body["session_id"], [ship["coordinates"] for ship in body["ships"]]
        except (KeyError, TypeError):
            raise ServiceError(f"{self.name}: ответ на старт игры не по контракту")

    def ask_shot(self, session_id):
        body = self.post(f"/game/{session_id}/shot", 200)
        coordinate = body.get("coordinate") if isinstance(body, dict) else None
        if not isinstance(coordinate, str):
            raise ServiceError(f"{self.name}: выстрел не по контракту")
        return coordinate

    def ask_opponent_shot(self, session_id, coordinate):
        body = self.post(f"/game/{session_id}/opponent-shot", 200, {"coordinate": coordinate})
        result = body.get("result") if isinstance(body, dict) else None
        if result not in RESULTS:
            raise ServiceError(f"{self.name}: непонятный результат {result!r}")
        return result

    def send_result(self, session_id, result):
        self.post(f"/game/{session_id}/shot/result", 200, {"result": result})

    def close(self, session_id):
        self.post(f"/game/{session_id}/close", 200)
