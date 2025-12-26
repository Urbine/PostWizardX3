# SPDX-License-Identifier: MPL-2.0
# Copyright (c) 2025 Yoham Gabriel B.

"""
PostWizardREST Taxonomy Utility CLI

This module is implements a convenience CLI utility for operating on taxonomies from the server via PostWizardREST
in case the user wants to.

As of now, this utility supports taxonomy removal only and it is useful in case malformed data is sent to the
server database, in such case the utility will contact the server and the term and post associations
with the latter will be cleaned automatically.

author: Yoham Gabriel Urbine@GitHub
email: yohamg@programmer.net
"""

__author__ = "Yoham Gabriel Urbine@GitHub"
__author_email__ = "yohamg@programmer.net"

import argparse

from pprint import pprint
from typing import Dict, List, Union

from postwizard_sdk.models.client_schema import Taxonomy
from postwizard_sdk.builders.taxonomy_builder import TaxonomyNestedPayload
from postwizard_sdk.utils.operations import remove_taxonomy


class TaxonomyUtility:
    def __init__(self):
        self.taxonomy_type = None
        self.taxonomy_term = None
        self.remove = False

    def parse_arguments(self) -> None:
        parser = argparse.ArgumentParser(description="PostWizardREST Taxonomy Manager")
        parser.add_argument(
            "--type",
            type=str,
            required=True,
            choices=["tag", "model"],
            help="Type of the taxonomy you want to modify",
        )
        parser.add_argument(
            "--term", type=str, required=True, help="Target term to be modified"
        )
        parser.add_argument(
            "--remove",
            action="store_true",
            required=True,
            help="Taxonomy removal from the server via PostWizardREST",
        )
        args = parser.parse_args()
        self.remove = args.remove
        self.taxonomy_type = args.type
        self.taxonomy_term = args.term

    def remove_taxonomy(
        self,
    ) -> (
        Dict[str, Union[str, int, bool, None, List[Dict[str, Union[str, int]]]]] | None
    ):
        payload = TaxonomyNestedPayload()
        match self.taxonomy_type:
            case "tag":
                payload.taxonomy_name(Taxonomy.TAG).term(self.taxonomy_term)
                return remove_taxonomy(payload)
            case "model":
                payload.taxonomy_name(Taxonomy.MODEL).term(self.taxonomy_term)
                return remove_taxonomy(payload)
        return None

    def manage_taxonomies(self):
        self.parse_arguments()
        if self.remove:
            return self.remove_taxonomy()
        return None


if __name__ == "__main__":
    pprint(TaxonomyUtility().manage_taxonomies())
