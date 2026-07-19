"""
CSB RPG Engine V2
"""

from __future__ import annotations
import random  # replaces renpy random

from dataclasses import dataclass
from queue import Queue
from typing import ParamSpec, Protocol, Callable, Concatenate, Any, Self
from functools import wraps
from collections.abc import Sequence
from enum import StrEnum, IntFlag, auto

from rpg3 import data
from rpg3.data import ActionStep, Character, AI, Battlefield, BATTLEFIELD

# | -- RENPY REPLACEMENTS -- |
Displayable = Any


def Image(*args: Any):
    return args


# | -- Engine Data Objects -- |
# These objects are created by the engine to manage stateful effects


class Fighter:
    def __init__(self, character: Character, enemy: bool, level: float, ai: AI | None):
        self.character: Character = character
        self.enemy: bool = enemy
        self.level: float = level
        self.ai: AI | None = ai

        self.base_hp: int = int(level * character.base_hp)
        self.base_def: int = int(level * character.base_def)
        self.base_atk: int = int(level * character.base_atk)
        self.base_acc: int = int(level * character.base_acc)

        self.hp: int = self.base_hp
        self.defence: int = self.base_def
        self.attack: int = self.base_atk
        self.accuracy: int = self.base_acc

        self.next_action: Any | None = None
        self.next_targets: list[Sequence[Fighter]] | None = None

    @property
    def dead(self):
        return self.hp <= 0

    @property
    def name(self):
        return self.character.name

    @property
    def display_name(self):
        return self.character.display_name

    def override_stats(
        self,
        hp: int | None = None,
        defence: int | None = None,
        attack: int | None = None,
        accuracy: int | None = None,
    ):
        # Override the base stats. This is only used by the parser.
        self.base_hp = self.base_hp if hp is None else int(self.level * hp)
        self.hp = self.base_hp
        self.base_def = self.base_def if defence is None else int(self.level * defence)
        self.defence = self.base_def
        self.base_atk = self.base_atk if attack is None else int(self.level * attack)
        self.attack = self.base_atk
        self.base_acc = self.base_acc if accuracy is None else int(self.level * accuracy)
        self.accuracy = self.base_acc


# | -- Engine Messages -- |


@dataclass
class Signal:
    # Plain old Signal, Not used by anything, but is the base class for cool match block stuff
    pass


@dataclass
class MessageSignal(Signal):
    # A simple message with just some text
    message: str


@dataclass
class CharacterSignal(Signal):
    # A simple message with an attached fighter
    message: str
    fighter: Fighter


@dataclass
class DebugSignal(Signal):
    # A debug message with a dict of details, and a source str
    message: str
    source: str
    details: dict[str, Any]


@dataclass
class ActionSignal(Signal):
    # A message to mark that a fighter is doing a specific action
    message: str
    fighter: Fighter
    action: Any


class IndicatorType(StrEnum):
    HP = "hp"
    DEF = "def"
    ATK = "atk"
    ACC = "acc"


@dataclass
class Indicator:
    # An indicator marks that a stat of a character has changed and by how much
    target: Fighter
    typ: IndicatorType
    value: int | None = None


@dataclass
class ActionStepSignal(Signal):
    # An action step describes what happens in a single step of an action
    # Each action has atleast one.
    message: str
    fighter: Fighter
    action: Any
    step: int
    targets: tuple[Fighter, ...]
    indicators: tuple[Indicator, ...]


class Signals:  # Can't be an enum if we want the cool type mapping in match blocks
    BASE = Signal
    MESSAGE = MessageSignal
    CHARACTER = CharacterSignal
    DEBUG = DebugSignal
    ACTION = ActionSignal
    ACTIONSTEP = ActionStepSignal


# | -- Engine -- |


class Engine:
    """
    The RPG engine which handles logic, and is used by actions/effects to manipulate fighters.
    The front end should have no reason to use the engine directly and should go solely through
    the Encounter.
    """

    def __init__(self) -> None:
        self._battlefield: Battlefield

        # The state of each character in the battle
        self.allies: tuple[Fighter, ...] = ()
        self.enemies: tuple[Fighter, ...] = ()
        self.fighters: tuple[Fighter, ...] = ()

        # Every message that the engine has generated through the turns
        self.message_queue: Queue[Signal] = Queue()

        # All of the indicators that the engine has generated.
        # Certain Messages will save the indicators and clear the collection.
        self.indicator_collection: list[Indicator] = []

    def initialise(self, battlefield: Battlefield | None = None):
        if battlefield is None:
            battlefield = BATTLEFIELD

        self.clear_messages()
        self.clear_indicators()

    # -- Message Methods --

    def clear_messages(self):
        self.message_queue = Queue()

    def has_messages(self) -> bool:
        return not self.message_queue.empty()

    def peak_next_message(self) -> Signal | None:
        if self.message_queue.empty():
            return None
        # This isn't thread-safe, but that is fine this is renpy
        return self.message_queue.queue[0]

    def get_next_message(self) -> Signal | None:
        if self.message_queue.empty():
            return None
        return self.message_queue.get()

    def send_message(self, message: Signal):
        self.message_queue.put(message)

    # -- Indicator Methods --

    def clear_indicators(self):
        self.indicator_collection.clear()

    def collect_indicators(self) -> tuple[Indicator, ...]:
        indicators = tuple(self.indicator_collection)
        self.clear_indicators()
        return indicators

    def display_indicator(self, target: Fighter, typ: IndicatorType, value: int | None = None):
        self.indicator_collection.append(Indicator(target, typ, value))

    # -- Fighter Manipulation Methods --

    # -- Turn Loop Methods --

    # For when I wake up. If indicators should link up with health actually being lost
    # Then turns need to happen iteratively between messages happening on the front end
    # Think about that


ENGINE = Engine()

# | -- Encounter -- |


class EncounterState(StrEnum):
    NOTHING = "nothing"
    ATTACK = "attack"
    TARGETING = "targeting"
    DEFEND = "defend"


class Encounter:
    def __init__(self, engine: Engine | None) -> None:
        self._battlefield: Battlefield
        self._engine: Engine

        # State Variables
        self.state: EncounterState
        self.selected_character: Fighter | None
        self.selected_action: None
        self.next_targets: list[Fighter]
        self.selected_targets: list[list[Fighter]]

    def initialise(self, battlefield: Battlefield | None = None, engine: Engine | None = None):
        # Use the global instances if specific instances aren't provided.
        if battlefield is None:
            battlefield = BATTLEFIELD
        if engine is None:
            engine = ENGINE

        self._battlefield = battlefield
        self._engine = engine
        self._engine.initialise(battlefield)

        self.state: EncounterState = EncounterState.NOTHING
        self.selected_character: Fighter | None = None
        self.selected_action: None = None
        self.next_targets: list[Fighter] = []
        self.selected_targets: list[list[Fighter]] = []

    # -- General Encounter Properties --

    @property
    def fighters(self) -> tuple[Fighter, ...]:
        return self._engine.fighters

    @property
    def won(self) -> bool | None:
        if len([f for f in self.allies if (f.hp != float("inf") and not f.dead)]) == 0:
            return False
        elif len([f for f in self.enemies if not f.dead]) == 0:
            return True
        return None

    @property
    def allies(self) -> tuple[Fighter, ...]:
        return tuple(fighter for fighter in self._engine.fighters if not fighter.enemy)

    @property
    def enemies(self) -> tuple[Fighter, ...]:
        return tuple(fighter for fighter in self.fighters if fighter.enemy)

    def get_team(self, enemy: bool = False) -> tuple[Fighter, ...]:
        return tuple(fighter for fighter in self.fighters if fighter.enemy == enemy)

    def get_incomplete_fighters(self, allies: bool | None = None):
        # Rather than trying to keep a sub-turn counter this lets front-end check who still needs
        # To take an action
        if allies is None:
            return tuple(fighter for fighter in self.fighters if self.fighter_is_complete(fighter))
        elif allies:
            return tuple(fighter for fighter in self.allies if self.fighter_is_complete(fighter))
        return tuple(fighter for fighter in self.enemies if self.fighter_is_complete(fighter))

    def fighter_is_complete(self, fighter):
        # Is the fighter complete, that is do they have a selected action and targets?
        # If they do, the front-end may want to mark them as complete is some way
        pass

    def team_is_complete(self, enemy: bool = False) -> bool:
        # Is the whole team complete? (see `fighter_is_complete`)
        incomplete = self.get_incomplete_fighters(not enemy)
        return len(incomplete) == 0

    # -- Player Action Functions --
    # Each function here is called when the player does some specific thing on the front end
    # There is nothing in the Engine that is special about a selected fighter so that is left
    # to the encounter and front end.

    def select_fighter(self, fighter):
        # Select an ally fighter, this sets them as the selected fighter and clears the
        # selected action and targets, unless they already have an action selected.
        # In this case the front-end should offer the ability to change the action.
        pass

    def deselect_fighter(self, fighter):
        # deselect the current fighter, and reset the state of the Encounter.
        pass

    def defend_fighter(self, fighter):
        # The given fighter is set as the selected fighter, and DEFEND is set as the selected action
        pass

    def select_action(self, action):
        # The currently selected action is set to this action.
        pass

    def confirm_action(self):
        # Confirm the currently selected action for the currently selected fighter.
        # Does nothing (does a debug alert) if one or both are None.
        # If the action has one step, and the target is self, or some other automatic
        # target criteria, then also skip the targeting step
        pass

    def get_valid_targets(self):
        # For the currently selected fighter, action, and action_step get the valid
        # targets. This is all of the targets that could be selected. If the targeting
        # flags includes `Unique`, that isn't handler here, but `is_valid_target` instead.
        # This is so the front end can call `get_valid_targets` once and then gray
        # the fighter out or smth when the fighter is no longer a valid target.
        pass

    def is_valid_target(self, target):
        # Is the provided fighter a valid target for the selected fighter, action, and
        # action_step. This differs from get_valid_targets, in that is also accounts for
        # the `Unique` flag. The front end should use this method to ensure the unique flag
        # is upheld. Also returns false when the target group is 'full'
        pass

    def add_target(self, target):
        # Add a target to the current set of targets. Since combo attacks can have multiple sets
        # of targets this gets added to the current target group.
        pass

    def remove_target(self, target, all: bool = False):
        # Remove an instance of target from the current group of targets. Or all instances
        # of the target if all is True.
        pass

    def enough_targets_selected(self) -> bool:
        # For the selected fighter, action, and action_step have enough fighters been selected?
        # For attacks with the `Variable` flag this will be true when one or more have been selected
        pass

    def max_targets_selected(self) -> bool:
        # For the selected fighter, action, and action_step have all the required targets for this
        # step been selected? If so the front-end should prevent further targeting.
        pass

    def confirm_target_group(self):
        # Move the current group of targets to the selected targets array. If that adds
        # the last required target group then the whole targeting step is complete, but
        # the targets aren't attached to the selected fighter until the front-end says so.
        # This will also create the target groups for any autotargeting groups.
        pass

    def drop_target_group(self):
        # Drop the last target group confirmed. This is so the player may return to the
        # previous target group.
        # If a target group was automatically chosen it will also be dropped.
        pass

    def all_targets_selected(self) -> bool:
        # If every targeting step has the required targets then return true. This method
        # should be used by the front-end to ensure that when the player clicks confirm
        # that the 'confirm_fighter` method should be called.
        pass

    def confirm_fighter(self):
        # Attach all target groups to the selected fighter and update the engine. Then
        # reset the state back to the base main menu state.
        pass

    def proceed_with_turn(self):
        # ALl of the player characters are confirmed (or if they aren't they will defend).
        # So let's tell the engine to start with the round of combat. This sets of a long chain
        # of messages as the engine figures out everything that happens as a consequence.
        pass

    # -- Message Methods --

    def has_messages(self) -> bool:
        # Does the engine still have messages that haven't been cleared from the queue?
        pass

    def peek_message(self):
        # Fetch the next message in the queue without removing it.
        pass

    def get_message(self):
        # Get the next message from the engine's queue and remove it.
        pass

    def clear_messages(self):
        # Remove every message from the engine without viewing them.
        pass
