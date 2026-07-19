"""
CSB RPG Reference Data Objects V2

Separated from the engine for clarity
"""

from __future__ import annotations

from typing import Callable, Concatenate, Any
from collections.abc import Sequence
from enum import StrEnum, IntFlag, auto

# | -- RENPY REPLACEMENTS -- |
Displayable = Any


def Image(*args: Any):
    return args


# | -- UTIL -- |
class classproperty[V]:
    def __init__(self, f: Callable[..., V]):
        self.f = f

    def __get__(self, _, owner: type):
        return self.f(owner)


CRIT_CHANCE = 5.0 / 100.0  # 5% chance for a critical hit
MISS_CHANCE = 1.0 / 100.0  # 1% change for a critical hit

UNKNOWN_FIELD = "game/gui/rpg/unknown_field_sprite.png"
UNKNOWN_PORTRAIT = "game/gui/rpg/portraits/unknown.png"

# | -- Reference Data Objects -- |
# These objects are used by the designers to create content for the RPG


class ActionFlag(IntFlag):
    NOTHING = 0
    DAMAGE = auto()
    HEAL = auto()
    STATS = auto()
    BUFF = auto()
    DEBUFF = auto()
    AOE = auto()
    EFFECT = auto()
    COMBO = auto()


class TargetFlag(IntFlag):
    NOTHING = 0
    ENEMY = auto()
    ALLY = auto()  # Anyone else on same team
    SELF = auto()  # The actor
    TEAM = ALLY | SELF  # Anyone on the actors team including themself
    ALL = ENEMY | TEAM  # Anyone in the combat
    UNIQUE = auto()  # Each target has to be unique
    VARIABLE = auto()  # You can select up-to n targets


type ActionFunction[**P] = Callable[Concatenate[Any, P], Any]


class ActionStep[**P]:  # Replaces the "attackfunc" python meta-magic from V1
    """
    An action step describes an action function and any parameters for that function.
    This is a reference data object, and should not change after creation.
    """

    def __init__(
        self,
        func: ActionFunction[P],
        *_: P.args,
        **attributes: P.kwargs,
    ):
        self.function = func
        self.attributes: dict[str, Any] = attributes


class Action:  # Was "Attack" in V1
    """
    An action describes something a character can do on their turn.
    This is a reference data object, and should not change after creation.

    "Combo" actions with multiple steps are still actions, however rather than
    passing in a single ActionStep a tuple of ActionSteps is passed in.

    The target(s) of each step can be set separately. When they are, each target type
    must also give a specific number of targets. The target_count argument will be ignored
    in this case.
    """

    def __init__(
        self,
        name: str,
        description: str,
        steps: ActionStep | Sequence[ActionStep],
        targets: TargetFlag | Sequence[tuple[TargetFlag, int] | None] = TargetFlag.ENEMY,
        target_count: int = 1,
        cooldown: int = 0,
        accuracy: int = 80,
        *,
        start_used: bool = False,
        flag_override: ActionFlag | None = None,
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.cooldown: int = cooldown  # How many turns after use before it can be used again
        self.accuracy: int = accuracy  # % chance of hitting the target (multiplied by char acc)
        self.start_used: bool = start_used  # Should the action be on cooldown immediately

        # TODO: handle flags for actions. Currently there is no way of flagging action functions
        self.flags: ActionFlag = flag_override if flag_override is not None else ActionFlag.NOTHING

        # Convert a single action step to a tuple. So all Actions are "Combo" Actions
        self.steps: Sequence[ActionStep] = (steps,) if isinstance(steps, ActionStep) else steps
        # Same with the targeting
        if isinstance(targets, TargetFlag):
            targets = ((targets, target_count),)
        self.targets: Sequence[tuple[TargetFlag, int] | None] = targets


# TODO: These need a total overhaul
class Effect:
    """
    Effects apply to characters temporarily (even if temporarily is the rest of the fight).
    They can have immediate effects (IME) and/or effects over time (EOT).
    This is a reference data object, and should not change after creation.
    """

    def __init__(
        self,
        name: str,
        description: str,
        positive: bool,
        icon: Displayable | None = None,
        duration: int = 0,
    ) -> None:
        self.name: str = name
        self.description: str = description
        self.icon: Displayable = icon  # Icon to show on character status menu
        self.positive: bool = positive  # Whether the effect is considered helpful by the engine
        self.duration: int = duration  # How many turns does the effect last? If 0 then forever


class AIFocus(StrEnum):
    STRONG = "strong"
    WEAK = "weak"
    NONE = "none"


class AI:
    """
    The parameters that help decide how an NPC will act each turn.
    This is a reference data object, and should not change after creation.
    """

    def __init__(
        self,
        heal_chance: float = 0.33,
        heal_threshold: float = 0.50,
        aggression: float = 1.0,
        crowd_control: float = 1.0,
        tacticity: float = 1.0,
        focus: AIFocus = AIFocus.NONE,
        preferred_targets: Sequence[str] = (),
        preference_weight: float = 2.0,
        *,
        name: str = "",  # name override
    ) -> None:
        self.name: str = name
        self.heal_chance: float = heal_chance  # Percent chance to outright pick a heal action
        self.heal_threshold: float = heal_threshold  # What is HP threshold to pick a heal action
        self.aggression: float = aggression  # The multiplier given to damaging actions
        self.crowd_control: float = crowd_control  # The multiplier given to AOE actions
        self.tacticity: float = tacticity  # The multiplier on Status Effects and Buffs
        self.focus: AIFocus = focus  # Whether to target the weakest enemy or strongest
        self.preferred_targets: Sequence[str] = preferred_targets  # Specific targets to pick more
        self.preference_weight: float = preference_weight  # Multiplier on target pick chance

    def __set_name__(self, owner: type, name: str):
        # rather than setting the name manually just grab it from the variable def.
        if self.name:
            return
        self.name: str = name.capitalize()


class CharacterFlag(IntFlag):
    NOTHING = 0
    ALLY = auto()
    ENEMY = auto()
    UCN = auto()
    UCN_ALLY = UCN | ALLY
    UCN_ENEMY = UCN | ENEMY


class HealthBarType(StrEnum):
    NORMAL = "normal"
    POLICE = "police"
    SECRET_T = "secret_t"


class Character:
    """
    The attributes of a character that can participate in fights. There
    can be multiple character objects for a narritve character. They must
    have different names, but can be unified by their display name.
    This is a reference data object, and should not change after creation.
    """

    def __init__(
        self,
        name: str,
        hp: int,
        defense: int,
        attack: int,
        actions: Sequence[Action],
        accuracy: int = 100,
        ai: AI | None = None,
        display_name: str | None = None,
        portrait: str | None = None,
        sprite: str | None = None,
        anim_sprite: str | None = None,
        health_bar: HealthBarType = HealthBarType.NORMAL,
        health_str: str = "{hp}/{base}",
        flags: CharacterFlag = CharacterFlag.NOTHING,
    ) -> None:
        self.name: str = name
        self.assigned_name: str = ""  # name that is used for fetching programmatically
        self.display_name: str = display_name or name
        self.flags: CharacterFlag = flags

        self.base_hp: int = hp  # how much hp will the fighter start with, and what is their max hp
        self.base_def: int = defense  # how much defense will the fighter start with
        self.base_atk: int = attack  # how much attack will the fighter start with
        self.base_acc: int = accuracy  # how accurate will the fighter start with

        self.attacks: tuple[Action, ...] = tuple(actions)  # What attacks can the character use
        self.base_ai: AI | None = ai  # Default AI for character

        # What image should represent the character on the player's side
        # Gets turned into an Imae
        self.portrait: str = portrait or UNKNOWN_PORTRAIT
        # What image should represent the character on the field side
        self.sprite: str = sprite or UNKNOWN_FIELD
        self.anim_sprite: str | None = anim_sprite

        # Details on what health bar texture should be used
        self.health_bar = health_bar
        # What should the health string for the character look like
        # Uses {} format strings {hp} formats to the current hp {base} to base hp
        self.health_str = health_str

    @property
    def infinite(self) -> bool:
        return self.base_hp == float("inf")

    def __set_name__(self, owner: type, name: str):
        # Get the name of the character as it is in the Character Reference
        self.assigned_name = name

    def __str__(self):
        return f'<Character {self.assigned_name} "{self.name}">'

    def __repr__(self):
        return self.__str__()


# I added the override functionality, but it is causing so much pain.
type _Overrides = None | tuple[AI, int | None, int | None, int | None, int | None]


class Battlefield:
    """
    The battlefield is the data directly taken from the parsed rpg block.
    It is a constant that is referred to by the Engine, Encounter, and Front End.
    It gets updated in-place when `execute_rpg` is called.
    """

    def __init__(self) -> None:
        self.allies: tuple[Character, ...]
        self.ally_overrides: tuple[_Overrides, ...]
        self.enemies: tuple[Character, ...]
        self.enemy_overrides: tuple[_Overrides, ...]
        self.characters: tuple[Character, ...]

        self.music: str
        self.on_win: str
        self.on_lose: str
        self.intro_text: str
        self.initial_turn: int

        self.debug: bool

    def update_data(
        self,
        music: str | None = None,
        on_win: str | None = None,
        on_lose: str | None = None,
        intro_text: str | None = None,
        initial_turn: int | None = None,
        *,
        debug: bool | None = None,
    ):
        # Update a
        self.music = music if music is not None else self.music
        self.on_win = on_win if on_win is not None else self.on_win
        self.on_lose = on_lose if on_lose is not None else self.on_lose
        self.intro_text = intro_text if intro_text is not None else self.intro_text
        self.initial_turn = initial_turn if initial_turn is not None else self.initial_turn

        self.debug = debug if debug is not None else self.debug

    def update_characters(
        self,
        chars: Sequence[Character],
        overrides: Sequence[None | tuple[AI, int | None, int | None, int | None, int | None]] = (),
        enemies: bool = False,
    ):
        if len(overrides) < len(chars):
            # If there are not enough overrides for the number of allies then pad with None
            overrides = tuple(overrides) + (None,) * (len(chars) - len(overrides))

        if enemies:
            self.enemies = tuple(chars)
            self.enemy_overrides = tuple(overrides)
        else:
            self.allies = tuple(chars)
            self.ally_overrides = tuple(overrides)
        self.characters = self.allies + self.enemies


BATTLEFIELD = Battlefield()
