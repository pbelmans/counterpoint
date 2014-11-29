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

      rule = Rules.InKey(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.AllowedIntervals(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.RangeAtMostTenth(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.PartOfChord(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.OnlyUnisonAtBeginOrEnd(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.NoParallelFifthsOrOctaves(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.NoSequencesOfParallelThirdsOrSixths(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.AtMostTwoConsecutiveLeaps(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.NotTooMuchMovement(new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.BeginOnUnisonFifthOrOctave(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue

      rule = Rules.EndOnUnisonOrOctave(new._cantus, new._counterpoint)
      if not rule.satisfied():
        continue


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
