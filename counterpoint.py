class Interval:
  _value = 0

  def __init__(self, value):
    assert abs(value) <= 127

    self._value = value

  # operations
  def __add__(self, other):
    return Interval(self._value + other._value)

  def __sub__(self, other):
    return Interval(self._value - other._value)

  def __eq__(self, other):
    return self._value == other._value

  # how big is the interval?
  def type(self):
    if abs(self._value) <= 2:
      return "step"
    elif abs(self._value) <= 5:
      return "skip"
    else:
      return "leap"

  # string representation
  def __str__(self):
    return str(self._value)

class Note:
  _value = 0

  def __init__(self, value):
    assert value >= 0
    assert value <= 127

    self._value = value

  # comparisons
  def __lt__(self, other):
    return self._value < other._value

  def __le__(self, other):
    return self._value <= other._value

  def __eq__(self, other):
    return self._value == other._value

  def __neq__(self, other):
    return self._value != other._value

  def __gt__(self, other):
    return self._value > other._value

  def __ge__(self, other):
    return self._value >= other._value

  # operations
  def __add__(self, other):
    self._value += other._value

  def __sub__(self, other):
    return Interval(self._value - other._value)


  # string representation
  def __str__(self):
    output = ""

    if self._value % 12 == 0: output += "C"
    elif self._value % 12 == 2: output += "D"
    elif self._value % 12 == 4: output += "E"
    elif self._value % 12 == 5: output += "F"
    elif self._value % 12 == 7: output += "G"
    elif self._value % 12 == 9: output += "A"
    elif self._value % 12 == 11: output += "B"

    output += str(self._value / 12)

    return output

class Voice:
  _notes = []
  _type = ""
  _range = (None, None)

  def __init__(self, voiceType, length):
    if voiceType == "soprano":
      self._range = (Note(60), Note(84))
    elif voiceType == "alto":
      self._range = (Note(53), Note(76))
    elif voiceType == "tenor":
      self._range = (Note(48), Note(72))
    elif voiceType == "bass":
      self._range = (Note(40), Note(64))

    self._type = voiceType

    # we initialise the list to None's
    self._notes = [None] * length

  # container type methods
  def __getitem__(self, key):
    return self._notes[key]

  def __setitem__(self, key, note):
    assert self._range[0] <= note
    assert note <= self._range[1]

    self._notes[key] = note

  def __len__(self):
    return len(self._notes)


  # string representation
  def __str__(self):
    output = "Voice\n"
    output += "  type: " + self._type + "\n"
    output += "  range: " + self._range[0].__str__() + " to " + self._range[1].__str__() + "\n"

    output += "  notes: "
    for note in self._notes:
      output += note.__str__() + " "

    return output

class FirstSpecies:
  _cantus = None
  _counterpoint = None

  def __str__(self):
    output = ""
    output += self._counterpoint.__str__() + "\n"
    output += self._cantus.__str__()

    return output

  def cantus(self, voice):
    self._cantus = voice # TODO check lengths?

  def counterpoint(self, voice):
    self._counterpoint = voice # TODO check lengths?

class Rule:
  def satisfied(self):
    raise NotImplementedError("This is an abstract method")

class HorizontalRule(Rule):
  _voice = None

  def __init__(self, voice):
    self._voice = voice

class TwoVoiceVerticalRule(Rule):
  _voices = [None] * 2

  def __init__(self, low, high):
    self._voices[0] = low
    self._voices[1] = high

"""
RULES
"""
class BeginOnUnisonFifthOrOctave(TwoVoiceVerticalRule):
  def __init__(self, low, high):
    TwoVoiceVerticalRule.__init__(self, low, high)

  def satisfied(self):
    print self._low[0]
    print self._high[0]


line = [48, 52, 53, 55, 52, 57, 55, 52, 53, 52, 50, 48]
cantus = Voice("tenor", 12)
for i in range(12):
  cantus[i] = Note(line[i])

counterpoint = Voice("alto", 12)

species = FirstSpecies()
species.cantus(cantus)
species.counterpoint(counterpoint)
print species
