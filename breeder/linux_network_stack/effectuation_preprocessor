
from typing import TypedDict, Literal

class Http(TypedDict):
	route: str # The route path, e.g. "/users/:id"
	path: str # The actual path called, e.g. "/users/123"
	method: str
	params: dict[str, str]
	query: dict[str, str]
	headers: dict[str, str]

class Websocket(TypedDict):
	url: str # The websocket url

class WmTrigger(TypedDict):
    kind: Literal["http", "email", "webhook", "websocket"]
    http: Http | None
    websocket: Websocket | None

def main(
    wm_trigger: WmTrigger,
	# your other args
    ):
	return {
		# return the args to be passed to the flow
      "config": {}
	}
