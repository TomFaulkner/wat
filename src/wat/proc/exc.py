class ProcessingException(Exception):
    pass


class CallbackNoNodeFound(ProcessingException):
    def __init__(self, ni_id: str) -> None:
        super().__init__(
            f"Callback requested for a node instance that doesn't exist: {ni_id}"
        )


class NodeInstanceInInvalidState(ProcessingException):
    def __init__(self, state):
        super().__init__(f"Node Instance is an unhandled/invalid state: {state}")
