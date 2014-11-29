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

