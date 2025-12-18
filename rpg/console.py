"""
Console based front end for CSB rpg engine
"""
from typing import Sequence

from util.ansi import ANSI

import rpg.engine as rpg

class Fight:

    def __init__(self, allies: Sequence[rpg.Character], enemies: Sequence[rpg.Character], show_debug: bool = True) -> None:
        self.show_debug: bool = show_debug

        fighters = [
            *(rpg.Fighter(character, False) for character in allies),
            *(rpg.Fighter(character, True) for character in enemies)
        ]
        self.encounter = rpg.Encounter(fighters, None, "", "you won!", "you lost!")

    def display_game(self):
        print(ANSI.CLEAR, end="")
        print(f"TURN: {self.encounter.turn}")

    def process_ally(self, ally: rpg.Fighter):
        print(f"Select attack for {ally.display_name}:")
        c = len(ally.character.attacks)
        for idx in range(c):
            attack = ally.attacks[idx]
            if attack.available:
                print(f"\t{idx} for {ally.attacks[idx].name}: {ally.attacks[idx].attack.description}")
            else:
                print(ANSI.RENDER(ANSI.STRIKETHROUGH, f"\t{idx} for {ally.attacks[idx].name}: {ally.attacks[idx].attack.description}"))
        print(f"\t{c} to defend")

        inp = input("attack option: ")
        try:
            idx = int(inp)
            if not ally.attacks[idx].available:
                print(f"{ally.attacks[idx].name} is not available, defending instead!")
                idx = c
        except ValueError:
            idx = c
        except IndexError:
            print("Not a valid attack option, defending instead!")
            idx = c

        if idx == c:
            self.encounter.defend_fighter(ally)
            return
        ally.next_attack = attack = ally.attacks[idx]
        possible_targets = self.encounter.possible_targets(ally, attack.attack)
        if attack.attack.targets == rpg.TargetType.SELF or attack.attack.target_count == 0:
            ally.next_targets = possible_targets
            return
        if attack.attack.target_count == 1 and len(possible_targets) == 1:
            ally.next_targets = possible_targets
            return

        # Pick targets
        count: int = attack.attack.target_count
        targets: list[rpg.Fighter] = []
        print(f"select {count} targets for {ally.display_name}:")
        for idx, target in enumerate(possible_targets):
            print(f"\t{idx} for {target.display_name}")
        while len(targets) != count:
            inp = input(f"target {len(targets) + 1} options: ")
            try:
                idx = int(inp)
                target = possible_targets[idx]
            except ValueError | IndexError:
                print(f"failed to select target {inp}! try again")
                continue
            targets.append(target)
        ally.next_targets = tuple(targets)

    def process_signals(self):
        while self.encounter.has_signals():
            signal = self.encounter.get_next_signal()
            if signal is None:
                continue

            if signal.typ == rpg.MessageType.INDICATOR:
                self.process_indicator(signal) # type: ignore -- TODO: this is due to bad handling of messages
            else:
                self.process_message(signal) # type: ignore -- TODO: this is due to bad handling of messages

    def process_indicator(self, signal: rpg.Signal[rpg.Indicator]):
        indicator = signal.message
        match indicator.typ:
            case rpg.IndicatorType.HP:
                print(ANSI.RENDER(ANSI.BACKGROUND_BRIGHT_RED, f"{indicator.source.display_name}: {indicator.typ} {indicator.value}"))
            case rpg.IndicatorType.DEF:
                print(ANSI.RENDER(ANSI.BACKGROUND_BRIGHT_GREEN, f"{indicator.source.display_name}: {indicator.typ} {indicator.value}"))
            case rpg.IndicatorType.ATK:
                print(ANSI.RENDER(ANSI.BACKGROUND_BRIGHT_BLUE, f"{indicator.source.display_name}: {indicator.typ} {indicator.value}"))
            case rpg.IndicatorType.ACC:
                print(ANSI.RENDER(ANSI.BACKGROUND_BRIGHT_MAGENTA, f"{indicator.source.display_name}: {indicator.typ} {indicator.value}"))
            case _:
                # indicator is effect and should use icon
                pass

    def process_message(self, signal: rpg.Signal[str]):
        match signal.typ:
            case rpg.MessageType.DEBUG:
                if not self.show_debug:
                    return
                print(ANSI.RENDER(ANSI.FOREGROUND_RED, signal.message))
            case rpg.MessageType.ATTACK:
                print(ANSI.RENDER(ANSI.BACKGROUND_RED, signal.message))
            case rpg.MessageType.CHARACTER:
                print(ANSI.RENDER(ANSI.BACKGROUND_GREEN, signal.message))
            case rpg.MessageType.EFFECT:
                print(ANSI.RENDER(ANSI.BACKGROUND_BLUE, signal.message))
            case rpg.MessageType.INDICATOR:
                return

    def run(self):
        while self.encounter.won is None:
            self.user_input = input("start turn?")
            self.display_game()
            for fighter in self.encounter.allies:
                self.process_ally(fighter)
            self.encounter.run_attacks()
            self.process_signals()
            # Could run this before running effects but nah
            self.encounter.run_effects()
            self.process_signals()
            self.encounter.cleanup_turn()
            self.process_signals()

        print(self.encounter.on_win if self.encounter.won else self.encounter.on_lose)
