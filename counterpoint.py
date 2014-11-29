import collections, copy

import Music, Rules, Species


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
      new._counterpoint[i] = Music.Note(v)

      rules = [
          Rules.InKey,
          Rules.AllowedIntervals,
          Rules.RangeAtMostTenth,
          Rules.PartOfChord,
          Rules.OnlyUnisonAtBeginOrEnd,
          Rules.NoParallelFifthsOrOctaves,
          Rules.NoSequencesOfParallelThirdsOrSixths,
          Rules.AtMostTwoConsecutiveLeaps,
          Rules.NotTooMuchMovement,
          Rules.BeginOnUnisonFifthOrOctave,
          Rules.EndOnUnisonOrOctave
        ]
      
      valid = True

      for rule in rules:
        # horizontal rules must only be applied to the counterpoint
        if issubclass(rule, Rules.HorizontalRule):
          instance = rule(new._counterpoint)

          if not instance.satisfied():
            valid = False
            break

        # vertical rules are still a bit too strict in the order of the arguments I think TODO
        if issubclass(rule, Rules.TwoVoiceVerticalRule):
          instance = rule(new._cantus, new._counterpoint)

          if not instance.satisfied():
            valid = False
            break

      if valid:
        queue.append(new)
  
  for solution in solutions:
    print solution
    print "\n"




line = [48, 52, 53, 55, 52, 57, 55, 52, 53, 52, 50, 48]
cantus = Music.Voice("tenor", 12)
for i in range(12):
  cantus[i] = Music.Note(line[i])

counterpoint = Music.Voice("alto", 12)

species = Species.FirstSpecies()
species.cantus(cantus)
species.counterpoint(counterpoint)
print species
solve(species)
