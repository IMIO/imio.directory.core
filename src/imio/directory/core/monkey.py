def extractRawWithoutEmptyErrors(self, setErrors=True):
    """Uggly monkeypatch to remove 'required' errors on fields in empty rows"""
    empty = True
    for wid in self.widgets:
        val = self.widgets[wid].value
        if val and val != ("--NOVALUE--",):
            empty = False
    if empty:
        # remove errors on empty lines
        data, errors = self.widgets.extractRaw()
        return (data, ())
    self.widgets.setErrors = setErrors
    return self.widgets.extractRaw()
