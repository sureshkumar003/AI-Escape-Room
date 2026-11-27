import json
from pathlib import Path
from typing import Dict, Any

CONFIG_PATH = Path(__file__).parent / "room_config.json"


class EscapeRoomEngine:
    def __init__(self):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            self.config = json.load(f)
        self.reset()

    def reset(self):
        self.state: Dict[str, Any] = {
            "inventory": [],
            "discovered_clues": [],
            "drawer_unlocked": False,
            "door_unlocked": False,
            "escaped": False,
            "turn_count": 0,
        }

    def get_public_state(self) -> Dict[str, Any]:
        """Returns state safe to display in UI (never exposes secret codes)."""
        return {
            "inventory": list(self.state["inventory"]),
            "discovered_clues": list(self.state["discovered_clues"]),
            "drawer_unlocked": self.state["drawer_unlocked"],
            "door_unlocked": self.state["door_unlocked"],
            "escaped": self.state["escaped"],
            "turn_count": self.state["turn_count"],
        }

    def execute_action(self, action: str, target: str = "", code: str = "", item: str = "") -> Dict[str, Any]:
        """Deterministically validates and executes player actions."""
        self.state["turn_count"] += 1
        action = (action or "").lower().strip()
        target = (target or "").lower().strip()
        code = (code or "").strip()
        item = (item or "").lower().strip()

        if self.state["escaped"]:
            return {"success": True, "event": "already_escaped", "fact": "The player has already unlocked the exit and escaped."}

        
        if action in ("cheat", "admin_override", "reveal_secrets", "claim_solved"):
            return {
                "success": False,
                "event": "blocked_adversarial",
                "fact": "Action denied by game rules. System overrides, secret code requests, and unverified puzzle claims are strictly prohibited.",
            }

        
        if action == "examine":
            if target not in self.config["objects"]:
                return {
                    "success": False,
                    "event": "invalid_target",
                    "fact": f"There is no '{target}' in the library. Valid objects are: desk, bookshelf, painting, drawer, door.",
                }
            obj = self.config["objects"][target]
            if target == "painting":
                if "magnifying_glass" in self.state["inventory"]:
                    if "painting_hour" not in self.state["discovered_clues"]:
                        self.state["discovered_clues"].append("painting_hour")
                    return {"success": True, "event": "examined_painting_magnified", "fact": obj["magnified_description"]}
                return {"success": True, "event": "examined_painting_blurry", "fact": obj["description"]}

            if target == "drawer":
                if self.state["drawer_unlocked"]:
                    if "drawer_note" not in self.state["discovered_clues"]:
                        self.state["discovered_clues"].append("drawer_note")
                    return {"success": True, "event": "examined_open_drawer", "fact": obj["unlocked_description"]}
                return {"success": True, "event": "examined_locked_drawer", "fact": obj["locked_description"]}

            if target == "door":
                desc = obj["unlocked_description"] if self.state["door_unlocked"] else obj["locked_description"]
                return {"success": True, "event": "examined_door", "fact": desc}

            if "reveals_clue" in obj and obj["reveals_clue"] not in self.state["discovered_clues"]:
                self.state["discovered_clues"].append(obj["reveals_clue"])

            return {"success": True, "event": f"examined_{target}", "fact": obj["description"]}

        
        if action == "take":
            if item in ("magnifying_glass", "magnifying glass", "glass") or target == "desk":
                if "magnifying_glass" in self.state["inventory"]:
                    return {"success": False, "event": "already_collected", "fact": "You already have the magnifying glass in your inventory."}
                self.state["inventory"].append("magnifying_glass")
                return {"success": True, "event": "item_collected", "fact": "You picked up the brass magnifying glass from the wooden desk."}
            return {
                "success": False,
                "event": "item_not_found",
                "fact": f"There is no collectable item '{item or target}' available.",
            }

        
        if action == "use_item":
            normalized_item = "magnifying_glass" if "glass" in item else item
            if normalized_item not in self.state["inventory"]:
                return {
                    "success": False,
                    "event": "missing_item",
                    "fact": f"You cannot use '{item}' because it is not in your inventory.",
                }
            if normalized_item == "magnifying_glass" and target == "painting":
                if "painting_hour" not in self.state["discovered_clues"]:
                    self.state["discovered_clues"].append("painting_hour")
                return {
                    "success": True,
                    "event": "used_magnifying_glass",
                    "fact": self.config["objects"]["painting"]["magnified_description"],
                }
            return {
                "success": False,
                "event": "ineffective_use",
                "fact": f"Using {normalized_item} on {target or 'nothing'} has no special effect.",
            }

        
        if action == "unlock_drawer":
            if self.state["drawer_unlocked"]:
                return {"success": True, "event": "drawer_already_open", "fact": "The drawer is already unlocked."}
            expected = self.config["objects"]["drawer"]["code"]
            if code == expected:
                self.state["drawer_unlocked"] = True
                if "drawer_note" not in self.state["discovered_clues"]:
                    self.state["discovered_clues"].append("drawer_note")
                return {
                    "success": True,
                    "event": "drawer_unlocked",
                    "fact": f"Code {code} worked! The drawer clicks open. Inside is a note: 'Append the painting's hour to the bookshelf digits to open the exit.'",
                }
            return {
                "success": False,
                "event": "wrong_drawer_code",
                "fact": f"The code '{code}' is incorrect. The 3-digit drawer lock remains shut.",
            }

        
        if action == "unlock_door":
            expected = self.config["objects"]["door"]["code"]
            if code == expected:
                self.state["door_unlocked"] = True
                self.state["escaped"] = True
                return {
                    "success": True,
                    "event": "escaped",
                    "fact": f"Code {code} accepted! The heavy iron exit door unlocks and swings open. You have escaped the library!",
                }
            return {
                "success": False,
                "event": "wrong_door_code",
                "fact": f"BEEP! Code '{code}' is wrong. The 4-digit exit door remains locked.",
            }

        return {
            "success": False,
            "event": "unknown_action",
            "fact": "You hesitate, unsure how to do that. Try examining an object, taking an item, or entering a code.",
        }
