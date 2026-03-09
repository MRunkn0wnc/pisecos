#!/usr/bin/env python3

import json
import os


class AEGIS:

    def __init__(self):

        self.script_dir = os.path.dirname(os.path.abspath(__file__))
        self.config_dir = os.path.join(
            os.path.dirname(self.script_dir),
            "configs"
        )

        self.intents = self.load_intents()

    def load_intents(self):

        file = os.path.join(self.config_dir, "intent_map.json")

        try:

            with open(file) as f:
                return json.load(f)

        except:
            return {}

    def understand_command(self, cmd):

        cmd = cmd.lower()

        for intent in self.intents:

            if intent in cmd:

                return {
                    "intent": intent,
                    "tool": self.intents[intent][0]
                }

        return {"intent": None}

    def explain_action(self, action, target):

        explanations = {

            "scan": f"Scanning {target} for open ports.",
            "subdomains": f"Enumerating subdomains of {target}",
            "ports": f"Running port scan on {target}",
            "vulnerabilities": f"Checking vulnerabilities on {target}"
        }

        return explanations.get(action, f"Running {action} on {target}")