from typing import Optional, Union, List

from core.controllers.interfaces.universal_controller import UniversalSecretController
from core.models.secret_model import (
    SecretType,
    PostDirectorAPILogin,
    PostDirectorAPIToken,
)
from core.secrets.secret_repository import SecretsDBInterface


class PDSAPIController(UniversalSecretController):
    def __init__(self, secrets_db: SecretsDBInterface):
        super().__init__(
            secrets_db, [SecretType.PDSAPI_PASSWORD, SecretType.PDSAPI_TOKEN]
        )

    def store_secrets(self, *args) -> bool:
        pass

    def update_secrets(self, *args) -> bool:
        pass

    def get_secrets(
        self, *args
    ) -> Optional[Union[PostDirectorAPILogin, PostDirectorAPIToken]]:
        pass

    def delete_secrets(self, *args) -> bool:
        pass
