from dataclasses import dataclass
from enum import Enum

@dataclass
class Signal:
    source: str

@dataclass
class B(Signal):
    b: int = 0

@dataclass
class C(Signal):
    d: int = 1

class Signals:
    Signal = Signal
    B = B
    C = C

a = C("1", 2)
c = C("2", 3)

print(a == C("1", 1))

def check_signal(signal: Signal):
    match signal:
        case Signals.B:
            print(signal, "is B")
        case Signals.C("2"):
            print(signal, "is specifcly C2")
        case Signals.C:
            print(signal, "is C")
        case Signals.Signal:
            print(signal, "is Signal")
        case _:
            pass

check_signal(a)
check_signal(c)