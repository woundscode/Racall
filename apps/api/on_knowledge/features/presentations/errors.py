"""Keep malformed model protocols distinct from semantic rejections in traces."""

from ..studio.generator import UnverifiedMaterial


class PresentationProtocolError(UnverifiedMaterial):
    pass


class UnsupportedPresentation(UnverifiedMaterial):
    def __init__(self, rejected):
        self.rejected = tuple(rejected)
        super().__init__("Presentation claims were rejected or uncertain: " + ", ".join(self.rejected))
