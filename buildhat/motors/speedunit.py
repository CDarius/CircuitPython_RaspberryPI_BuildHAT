from ..models.enumstr import EnumStr


class SpeedUnit(EnumStr):
    """Motor speed unit"""

    """Revolution per minute"""
    RPM = None
    """Degree per seconds"""
    DGS = None


SpeedUnit.RPM = SpeedUnit("RPM")
SpeedUnit.DGS = SpeedUnit("DGS")
