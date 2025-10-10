"""
Taxonomy Payload Builder

This module defines the TaxonomyPayload class, which is a subclass of PayloadBuilder.
It is used to build a payload for a WordPress Taxonomy request, which is a type of request
that is consumed in JSON format by the PostWizard Server API.

Author: Yoham Gabriel Urbine@GitHub
Email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

from typing import Self

from postwizard_sdk.builders.interfaces.payload_builder import PayloadBuilder
from postwizard_sdk.models.client_schema import Taxonomy, TaxonomyMeta, TaxonomyInfo


class TaxonomyPayload(PayloadBuilder):
    def __init__(self):
        super().__init__()

    def term(self, term: str) -> Self:
        return self._plus(TaxonomyInfo.TERM, term)

    def slug(self, slug: str) -> Self:
        return self._plus(TaxonomyInfo.SLUG, slug)

    def taxonomy_description(self, description: str):
        return self._nest(
            TaxonomyMeta.TAXONOMY, TaxonomyMeta.TAXONOMY_DESCRIPTION, description
        )

    def taxonomy_name(self, taxonomy: Taxonomy):
        return self._nest(
            TaxonomyMeta.TAXONOMY, TaxonomyMeta.TAXONOMY_NAME, taxonomy.value
        )
