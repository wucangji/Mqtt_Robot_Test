__author__ = 'canwu'


class req_payload:
    """
    Create the request payload.
    """

    def __init__(self, pc):
        self.nm = ""
        self.pc ="\"pc\" : {%s}" % (pc)

    def add_operation(self, op):
        self.op = "\"op\" : \"%s\"," % (op)

    def add_to(self, to):
        self.to = "\"to\" : \"%s\"," % (to)

    def add_rqi(self, rqi):
        self.rqi = "\"rqi\" : \"%s\"," % (rqi)

    def add_fr(self, fr):
        self.fr = "\"fr\" : \"%s\"," % (fr)

    def add_ty(self, ty):
        self.ty = "\"rqi\" : \"%s\"," % (ty)

    def add_nm(self, nm):
        self.nm = "\"nm\" : \"%s\"," % (nm)

    def show(self):
        self.payload = self.op + self.to + self.rqi + self.fr + self.ty
        if self.nm != None:
            self.payload += self.nm
        return "{" + self.payload + self.pc + "}"


class AE_create:
    """
    Create the create_resource_AE "pc".
    """

    def __init__(self):
        self._orr = ""
        self._lbl = ""

    def add_api(self, api):
        self.api = "\"api\" : \"%s\"," % (api)

    def add_apn(self, apn):
        self.apn = "\"apn\" : \"%s\"," % (apn)

    def add_or(self, orr):
        self._orr = "\"or\" : \"%s\"," % (orr)

    def add_lbl(self, lbl):
        """addLabel, label is a list"""
        assert isinstance(lbl,(list,tuple))
        self._lbl = "\"lbl\" : %s," % (lbl)

    def show(self):
        self.mandatory = self.api + self.apn
        if self._orr != "":
            self.mandatory += self._orr
        if self._lbl != "":
            self.mandatory += self._lbl
        return "{" + self.mandatory + "}"