def extractRawWithoutEmptyErrors(self, setErrors=True):
    """Uggly monkeypatch to remove 'required' errors on fields in empty rows"""
    empty = True
    for wid in self.widgets:
        val = self.widgets[wid].value
        if val and val != ("--NOVALUE--",):
            empty = False
    self.widgets.setErrors = setErrors
    data, errors = self.widgets.extractRaw()
    if empty:
        # remove errors on empty lines
        errors = ()
    return (data, errors)


def toFieldValueWithDefaultValue(self, value):
    """Uggly monkeypatch to avoid error with missing fields in rows"""
    _converted = {}
    for name, fld in self.field.schema.namesAndDescriptions():
        converter = self._getConverter(fld)
        if name not in value:
            value[name] = ""
        try:
            _converted[name] = converter.toFieldValue(value[name])
        except Exception:
            # XXX: catch exception here in order to not break
            # versions prior to this fieldValue converter
            _converted[name] = value[name]
    return _converted
