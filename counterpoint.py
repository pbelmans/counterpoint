import collections, copy

import Music, Rules, Species


def solve(species):
  # TODO remove this
  considered = collections.defaultdict(int)
  failed = collections.defaultdict(int)
  
  total = 0

  queue = collections.deque([species])

  solutions = []

  while len(queue) > 0:
    total = total + 1

    species = queue.popleft()
    if verbose:
      print "popped from the queue:"
      print species

    if len(filter(None, species._counterpoint)) == len(species._cantus):
      solutions.append(species)
      continue

    # look for first undefined note
    i = 0
    while species._counterpoint[i] != None:
      i = i + 1

    if verbose: print "up to", i, "notes now"

    for v in [53, 55, 57, 59, 60, 62, 64, 65, 67, 69, 71, 72, 74, 76] : # TODO hardcoded voice range...
      if verbose: print "considering adding " + Music.Note(v).__str__()
      new = copy.deepcopy(species)
      new._counterpoint[i] = Music.Note(v)

      rules = [
          # harmonic rules
          Rules.PartOfChord,
          Rules.NoUnisonExceptAtBeginOrEnd,
          Rules.NoParallelFifthsOrOctaves,
          Rules.NoSequencesOfParallelThirdsOrSixths,
          Rules.EndOnUnisonOrOctave,
          Rules.BeginOnUnisonFifthOrOctave,
          Rules.NotTooMuchMovement,
          # melodic rules
          Rules.InKey, # TODO this isn't failing at the moment because we only add notes in the key
          Rules.RangeAtMostTenth,
          Rules.AllowedIntervals,
          Rules.AtMostOneRepetition,
          Rules.AtMostTwoConsecutiveLeaps,
        ]
      
      valid = True

      for rule in rules:
        considered[rule.__name__] += 1
        
        # horizontal rules must only be applied to the counterpoint
        if issubclass(rule, Rules.HorizontalRule):
          instance = rule(new._counterpoint)

          if not instance.satisfied():
            failed[rule.__name__] += 1

            valid = False
            break

        # vertical rules are still a bit too strict in the order of the arguments I think TODO
        if issubclass(rule, Rules.TwoVoiceVerticalRule):
          instance = rule(new._cantus, new._counterpoint)

          if not instance.satisfied():
            failed[rule.__name__] += 1

            valid = False
            break

      if valid:
        queue.append(new)
        
      if verbose:
        if valid: print " + this attempt was successful"
        else: print "   this attempt failed because of " + rule.__name__
  
  for solution in solutions:
    print solution
    print "\n"

  def pretty(considered, failed):
    for key in considered.keys():
      print key + ":\n\t" + str(considered[key]) + " vs " + str(failed[key])
  
  print pretty(considered, failed)
  print "performed", total, "steps"
  print "found", len(solutions), "solutions"


verbose = True

#line = [48, 52, 53, 55, 52, 57, 55, 52, 53, 52, 50, 48]
#line = [48, 50, 52, 47, 48, 45, 43, 48]
line = [48, 50, 52, 47, 45, 43, 48]
#line = [48, 50, 48]
cantus = Music.Voice("bass", len(line))
for i in range(len(line)):
  cantus[i] = Music.Note(line[i])

counterpoint = Music.Voice("alto", len(line))

species = Species.FirstSpecies()
species.cantus(cantus)
species.counterpoint(counterpoint)
print "starting with:"
print species
solve(species)
