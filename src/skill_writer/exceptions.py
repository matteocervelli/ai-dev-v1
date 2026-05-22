class SkillWriterError(Exception):
    pass


class InvalidNameError(SkillWriterError):
    pass


class CreationError(SkillWriterError):
    pass


class ScopeError(SkillWriterError):
    pass
