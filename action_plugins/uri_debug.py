import json
from json import JSONDecodeError

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    """Validate and (optionally) pretty-print request body before calling uri."""

    def run(self, tmp=None, task_vars=None):
        task_vars = task_vars or {}

        args = self._task.args.copy()
        body = args.get("body")
        body_format = args.get("body_format")
        logging_allowed = not bool(getattr(self._task, "no_log", True))

        if logging_allowed and body is not None:
            # Decide if we should treat it as JSON
            is_json_like = (
                body_format == "json"
                or isinstance(body, (dict, list))
                or (isinstance(body, str) and body.lstrip().startswith(("{", "[")))
            )

            if is_json_like:
                try:
                    if isinstance(body, str):
                        parsed = json.loads(body)
                    else:
                        parsed = body
                    pretty = json.dumps(parsed, indent=2, ensure_ascii=False)
                    self._display.display(
                        "\n--- URI REQUEST BODY (JSON) ---\n"
                        + f"{pretty}\n"
                        + "--------------------------------"
                    )
                except (JSONDecodeError, TypeError, ValueError) as e:
                    raise AnsibleActionFail(
                        "Invalid JSON body detected before sending request:\n"
                        + f"{e}\n\nBody content:\n{body}"
                    )
            else:
                self._display.display(
                    f"\n--- URI REQUEST BODY ---\n{body}\n------------------------"
                )

        return self._execute_module(
            module_name="uri",
            module_args=args,
            task_vars=task_vars,
            tmp=tmp,
        )
