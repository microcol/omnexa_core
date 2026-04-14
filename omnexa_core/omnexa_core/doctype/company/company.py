# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe import _
from frappe.model.document import Document


class Company(Document):
	def validate(self):
		if self.eta_einvoice_enabled and not (self.rin or "").strip():
			frappe.throw(_("RIN is required when ETA e-Invoice is enabled."), title=_("Validation"))
		self._validate_einvoice_profiles()

	def before_insert(self):
		self._prevent_circular_parent()

	def before_save(self):
		self._prevent_circular_parent()

	def _prevent_circular_parent(self):
		if not self.parent_company:
			return
		if self.parent_company == self.name:
			frappe.throw(_("Parent Company cannot be the same as the company."), title=_("Validation"))
		walk = self.parent_company
		depth = 0
		while walk and depth < 32:
			if walk == self.name:
				frappe.throw(_("Circular parent company chain is not allowed."), title=_("Validation"))
			walk = frappe.db.get_value("Company", walk, "parent_company")
			depth += 1

	def _validate_einvoice_profiles(self):
		if not self.eta_einvoice_enabled:
			return
		if not self.company_tax_authority_profile or not self.company_signing_profile:
			frappe.throw(
				_("Tax Authority Profile and Signing Profile are required when ETA e-Invoice is enabled."),
				title=_("Validation"),
			)

		tax_company = frappe.db.get_value(
			"Tax Authority Profile", self.company_tax_authority_profile, "company"
		)
		sign_company = frappe.db.get_value("Signing Profile", self.company_signing_profile, "company")
		if tax_company and tax_company != self.name:
			frappe.throw(_("Tax Authority Profile must belong to the same company."), title=_("Validation"))
		if sign_company and sign_company != self.name:
			frappe.throw(_("Signing Profile must belong to the same company."), title=_("Validation"))
