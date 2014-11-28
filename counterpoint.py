import collections, copy

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
class InKey(HorizontalRule):
  def satisfied(self):
    for i in range(len(self._voice)):
      if self._voice[i] != None:
        if self._voice[i]._value % 12 not in [0, 2, 4, 5, 7, 9, 11]:
          return False

    return True

class AllowedIntervals(HorizontalRule):
  def satisfied(self):
    for first, second in zip(self._voice, self._voice[1:]):
      if first != None and second != None:
        if abs((first - second)._value) not in [1, 2, 3, 4, 5, 7, 8, 9, 12]: # TODO should 0 be in here?
          return False

    return True

class AtMostTwoConsecutiveLeaps(HorizontalRule):
  def satisfied(self):
    for first, second, third in zip(self._voice, self._voice[1:], self._voice[2:]):
      if first != None and second != None and third != None:
        if (second - first).type() == "leap" and (third - second).type() == "leap":
          return False

    return True

class RangeAtMostTenth(HorizontalRule):
  def satisfied(self):
    if max(filter(None, self._voice)) - min(filter(None, self._voice)) >= Interval(15): # TODO apply the filter trick more often (!)
      return False

    return True

class BeginOnUnisonFifthOrOctave(TwoVoiceVerticalRule):
  def satisfied(self):
    return self._voices[1][0] - self._voices[0][0] in [Interval(-12), Interval(0), Interval(7), Interval(12)]

class EndOnUnisonOrOctave(TwoVoiceVerticalRule):
  def satisfied(self):
    if self._voices[0][-1] != None and self._voices[1][-1] != None:
      return self._voices[1][-1] - self._voices[0][-1] in [Interval(-12), Interval(0), Interval(12)]

    return True

class OnlyUnisonAtBeginOrEnd(TwoVoiceVerticalRule):
  def satisfied(self):
    for first, second in zip(self._voices[0][1:-1], self._voices[1][1:-1]):
      if first != None and second != None and first == second:
        return False

    return True

class PartOfChord(TwoVoiceVerticalRule):
  def satisfied(self):
    for first, second in zip(self._voices[0], self._voices[1]):
      if first != None and second != None and (second - first)._value not in [0, 3, 4, 7, 8, 9, 12, 15, 16]:
        return False
    
    return True

class NoParallelFifthsOrOctaves(TwoVoiceVerticalRule):
  def satisfied(self):
    for first, second in zip(zip(self._voices[0], self._voices[1]), zip(self._voices[0][1:], self._voices[1][1:])):
      if first[0] != None and first[1] != None and second[0] != None and second[1] != None:
        if first[1] - first[0] == second[1] - second[0] and (first[1] - first[0])._value in [0, 7, 12]:
          return False
    
    return True

class NoSequencesOfParallelThirdsOrSixths(TwoVoiceVerticalRule):
  def satisfied(self):

    for first, second, third, fourth in zip(zip(self._voices[0], self._voices[1]), zip(self._voices[0][1:], self._voices[1][1:]), zip(self._voices[0][2:], self._voices[1][2:]), zip(self._voices[0][3:], self._voices[1][3:])):
      if first[0] != None and first[1] != None and second[0] != None and second[1] != None and third[0] != None and third[1] != None and fourth[0] != None and fourth[1] != None:
        intervals = set([(first[1] - first[0])._value % 12, (second[1] - second[0])._value % 12, (third[1] - third[0])._value % 12, (fourth[1] - fourth[0])._value % 12])

        if intervals == set([3, 4]) or intervals == set([8, 9]):
          return False

    return True

class NotTooMuchMovement(HorizontalRule):
  def satisfied(self):
    pairs = list(zip(self._voice, self._voice[1:]))
    pairs = filter(lambda pair: pair[0] != None and pair[1] != None, pairs)

    # if there are at most 5 pairs of consecutive notes we won't consider it
    if len(pairs) <= 5:
      return True

    steps = filter(lambda pair: (pair[1] - pair[0]).type() == "step", pairs)
    skips = filter(lambda pair: (pair[1] - pair[0]).type() == "skip", pairs)
    leaps = filter(lambda pair: (pair[1] - pair[0]).type() == "leap", pairs)

    if len(steps) < len(skips):
      return False

    if len(leaps) >= 2:
      return False

    return True



def solve(species):
  queue = collections.deque([species])

  solutions = []

  while len(queue) > 0:
    print len(queue)

    species = queue.popleft()

    if len(filter(None, species._counterpoint)) == 12: # TODO hardcoded...
      solutions.append(species)
      continue

    # look for first undefined note
    i = 0
    while species._counterpoint[i] != None:
      i = i + 1

    print "up to", i, "notes now"

    for v in [53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76] : # TODO hardcoded voice range...
      new = copy.deepcopy(species)
      new._counterpoint[i] = Note(v)

      rule = InKey(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = AllowedIntervals(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = RangeAtMostTenth(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = PartOfChord(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = OnlyUnisonAtBeginOrEnd(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = NoParallelFifthsOrOctaves(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = NoSequencesOfParallelThirdsOrSixths(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = AtMostTwoConsecutiveLeaps(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = NotTooMuchMovement(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = BeginOnUnisonFifthOrOctave(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = EndOnUnisonOrOctave(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue


      queue.append(new)
  
  for solution in solutions:
    print solution
    print "\n"




line = [48, 52, 53, 55, 52, 57, 55, 52, 53, 52, 50, 48]
cantus = Voice("tenor", 12)
for i in range(12):
  cantus[i] = Note(line[i])

counterpoint = Voice("alto", 12)

species = FirstSpecies()
species.cantus(cantus)
species.counterpoint(counterpoint)
print species
solve(species)
