import copy

import Music


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
helper functions
"""
def horizontalIntervals(voice):
  """ Get all melodic intervals """
  pairs = zip(voice, voice[1:])
  pairs = filter(lambda pair: pair[0] != None and pair[1] != None, pairs)

  return [pair[0] - pair[1] for pair in pairs]

def verticalIntervals(first, second):
  """ Get all harmonic intervals between two voices """
  pairs = zip(first, second)
  return [pair[0] - pair[1] for pair in pairs if pair[0] != None and pair[1] != None]

def consecutiveVerticalIntervals(first, second, length):
  """ Get all tuples of a specified length of consecutive harmonic intervals between two voices """
  pairs = []
  for i in range(length):
    pairs.append(verticalIntervals(first[i:], second[i:]))

  return zip(*pairs)


"""
RULES
"""
class InKey(HorizontalRule):
  """Check whether all notes in the voice are in the key"""
  def satisfied(self):
    key = [Music.P1, Music.M2, Music.M3, Music.P4, Music.P5, Music.M6, Music.M7]
    tonic = Music.Note(48) # TODO hardcoded C major
    return all(map(lambda note: Music.octaveReduce(note - tonic) in key, filter(None, self._voice)))

class AllowedIntervals(HorizontalRule):
  def satisfied(self):
    for interval in horizontalIntervals(self._voice):
      descending = [-Music.P8, -Music.P5, -Music.P4, -Music.M3, -Music.m3, -Music.M2, -Music.m2, -Music.P1]
      ascending = [Music.P1, Music.m2, Music.M2, Music.m3, Music.M3, Music.P4, Music.P5, Music.m6, Music.P8]
      
      allowed = descending + ascending
      
      if interval not in allowed:
        return False

    return True

class AtMostTwoConsecutiveLeaps(HorizontalRule):
  def satisfied(self):
    for first, second, third in zip(self._voice, self._voice[1:], self._voice[2:]):
      if first != None and second != None and third != None:
        if (second - first).type() == "leap" and (third - second).type() == "leap":
          return False

    return True

class AtMostOneRepetition(HorizontalRule):
  def satisfied(self):
    return horizontalIntervals(self._voice).count(Music.P1) <= 1


class RangeAtMostTenth(HorizontalRule):
  def satisfied(self):
    if max(filter(None, self._voice)) - min(filter(None, self._voice)) >= Music.Interval(15): # TODO apply the filter trick more often (!)
      return False

    return True

class BeginOnUnisonFifthOrOctave(TwoVoiceVerticalRule):
  def satisfied(self):
    if self._voices[0][0] != None and self._voices[1][0] != None:
      return self._voices[1][0] - self._voices[0][0] in [Music.Interval(-12), Music.Interval(0), Music.Interval(7), Music.Interval(12)]

class EndOnUnisonOrOctave(TwoVoiceVerticalRule):
  def satisfied(self):
    if self._voices[0][-1] != None and self._voices[1][-1] != None:
      return self._voices[1][-1] - self._voices[0][-1] in [Music.Interval(-12), Music.Interval(0), Music.Interval(12)]

    return True


class NoUnisonExceptAtBeginOrEnd(TwoVoiceVerticalRule):
  def satisfied(self):
    for first, second in zip(self._voices[0][1:-1], self._voices[1][1:-1]):
      if first != None and second != None and first == second:
        return False

    return True


class PartOfChord(TwoVoiceVerticalRule):
  """Check whether all harmonic intervals are part of a chord"""
  def satisfied(self):
    for interval in verticalIntervals(self._voices[1], self._voices[0]): # TODO Python has a any or all method
      if interval._value % 12 not in [0, 3, 4, 7, 8, 9, 12, 15, 16]:
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
