from typing import Any, Dict, List


class DebugPanel:
    def __init__(self, request_data: Dict, response_data: Dict):
        self.request_data = request_data
        self.response_data = response_data

    def render(self) -> Dict:
        return {
            "request": self.request_data,
            "response": self.response_data,
        }

    def get_execution_trace(self) -> List[Dict]:
        return [
            {"phase": "request", "data": self.request_data},
            {"phase": "response", "data": self.response_data},
        ]


class ExecutionTracePanel(DebugPanel):
    def get_execution_trace(self) -> List[Dict]:
        trace = []

        if "timestamp" in self.request_data:
            trace.append({
                "phase": "request_received",
                "timestamp": self.request_data["timestamp"]
            })

        if self.response_data.get("execution_time"):
            trace.append({
                "phase": "response_sent",
                "execution_time": self.response_data["execution_time"]
            })

        trace.append({"phase": "request", "data": self.request_data})
        trace.append({"phase": "response", "data": self.response_data})

        return trace
