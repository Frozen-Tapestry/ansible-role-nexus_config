import json

from ansible.errors import AnsibleActionFail
from ansible.plugins.action import ActionBase


class ActionModule(ActionBase):
    def run(self, tmp=None, task_vars=None):
        if task_vars is None:
            task_vars = {}

        args = self._task.args.copy()
        body = args.get("body", None)
        body_format = args.get("body_format", None)

        if body:
            # Try to detect and validate JSON if body_format is json or body looks like JSON
            is_json_like = (
                body_format == "json"
                or (isinstance(body, str) and body.strip().startswith("{"))
                or (isinstance(body, str) and body.strip().startswith("["))
            )

            if is_json_like:
                try:
                    parsed = json.loads(body)
                    pretty_body = json.dumps(parsed, indent=2)
                    self._display.display(
                        f"\n--- URI REQUEST BODY (valid JSON) ---\n{pretty_body}\n--------------------------------------"
                    )
                except Exception as e:
                    msg = f"❌ Invalid JSON body detected before sending request:\n{str(e)}\n\nBody content:\n{body}"
                    raise AnsibleActionFail(msg)
            else:
                self._display.display(
                    f"\n--- URI REQUEST BODY (non-JSON) ---\n{body}\n-----------------------------------"
                )

        # Execute the real 'uri' module after validation
        result = self._execute_module(
            module_name="uri",
            module_args=args,
            task_vars=task_vars,
            tmp=tmp,
        )

        return result
