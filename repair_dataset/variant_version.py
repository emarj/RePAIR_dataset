from typing import Union
import semver

class Version(semver.Version):
    @classmethod
    def parse(cls, version_str: str):
        ver = super().parse(version_str, optional_minor_and_patch=True)
        if ver.build:
            raise ValueError("Build metadata is not supported in version strings.")
        return ver

    def to_py_str(self) -> str:
        ver_str = super().__str__()
        return ver_str.replace('-', '_').replace('.', '_').replace('+', '_')
    
    def full_str(self) -> str:
        return super().__str__()
    
    def __str__(self) -> str:
        out = str(self.major)
        if self.minor != 0 or self.patch != 0:
            out += f".{self.minor}"
        if self.patch != 0:
            out += f".{self.patch}"
        if self.prerelease is not None:
            out += f"-{self.prerelease}"
        return out
  
    
    def matches(self, other: 'Version') -> bool:
        return (self.major == other.major
                    and (self.minor == 0 or self.minor == other.minor)
                    and (self.patch == 0 or self.patch == other.patch)
                    and (self.prerelease is None or self.prerelease == other.prerelease)
                    and (self.build is None or self.build == other.build))

class VariantVersion:
    def __init__(self, version: Union[str, Version], variant: str) -> None:

        if isinstance(version, str):
            self.version = Version.parse(version)
        elif isinstance(version, Version):
            self.version = version
        else:
            raise ValueError("Version must be a string or a Version instance.")
        
        if not isinstance(variant, str) or not variant.strip():
            raise ValueError("Variant must be a non-empty string")
        
        self.variant = variant

    def __str__(self) -> str:
        return f"{self.variant}_v{self.version}"
    
    def __repr__(self) -> str:
        return f"VersionType(variant={self.variant}, version={self.version.full_str()})" 
    


