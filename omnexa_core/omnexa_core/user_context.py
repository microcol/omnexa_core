# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

from __future__ import annotations

import frappe

from omnexa_core.omnexa_core.branch_access import (
	get_allowed_branches,
	get_default_branch,
	get_default_company,
	user_can_access_all_branches,
)


def apply_company_branch_defaults(doc, method=None):
	"""Populate company/branch from logged-in user context when missing."""
	has_company = bool(getattr(doc.meta, "has_field", lambda f: False)("company"))
	has_branch = bool(getattr(doc.meta, "has_field", lambda f: False)("branch"))

	if has_company and not getattr(doc, "company", None):
		doc.company = get_default_company()

	if has_branch and not getattr(doc, "branch", None):
		company = getattr(doc, "company", None)
		if company:
			doc.branch = get_default_branch(company=company)


def get_allowed_branches_for_current_doc(doc) -> list[str] | None:
	company = getattr(doc, "company", None)
	if user_can_access_all_branches():
		return None
	return get_allowed_branches(company=company)
