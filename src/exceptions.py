class PricatError(Exception):
    pass


class FileReadError(PricatError):
    pass


class MappingError(PricatError):
    pass


class CatalogBuildError(PricatError):
    pass


class ValidationError(PricatError):
    pass
