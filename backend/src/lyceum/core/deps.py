from typing import Annotated

from fastapi import Depends

from lyceum.core.config import Settings, get_settings

SettingsDep = Annotated[Settings, Depends(get_settings)]
