# Copyright (c) 2026, Omnexa and contributors
# License: MIT. See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase


class TestOmnexaCompany(FrappeTestCase):
	def setUp(self):
		super().setUp()
		if not frappe.db.exists("Currency", "EGP"):
			frappe.get_doc(
				{"doctype": "Currency", "currency_name": "EGP", "symbol": "E£", "enabled": 1}
			).insert(ignore_permissions=True)
		if not frappe.db.exists("Country", "Egypt"):
			frappe.get_doc(
				{"doctype": "Country", "country_name": "Egypt", "code": "EG"}
			).insert(ignore_permissions=True)

	def test_rin_required_when_eta_enabled(self):
		doc = frappe.new_doc("Company")
		doc.company_name = "Test Pilot Co"
		doc.abbr = "TPCO"
		doc.default_currency = "EGP"
		doc.country = "Egypt"
		doc.status = "Draft"
		doc.eta_einvoice_enabled = 1
		doc.rin = ""
		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_company_inserts_when_eta_is_disabled(self):
		doc = frappe.new_doc("Company")
		doc.company_name = "Test Pilot Co 2"
		doc.abbr = "TPC2"
		doc.default_currency = "EGP"
		doc.country = "Egypt"
		doc.status = "Draft"
		doc.eta_einvoice_enabled = 0
		doc.insert(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Company", doc.name))

	def test_company_eta_requires_profiles(self):
		doc = frappe.new_doc("Company")
		doc.company_name = "Test Pilot Co 4"
		doc.abbr = "TPC4"
		doc.default_currency = "EGP"
		doc.country = "Egypt"
		doc.status = "Draft"
		doc.eta_einvoice_enabled = 1
		doc.rin = "123456789"
		with self.assertRaises(frappe.ValidationError):
			doc.insert(ignore_permissions=True)

	def test_company_eta_accepts_company_profiles(self):
		doc = frappe.new_doc("Company")
		doc.company_name = "Test Pilot Co 3"
		doc.abbr = "TPC3"
		doc.default_currency = "EGP"
		doc.country = "Egypt"
		doc.status = "Draft"
		doc.rin = "987654321"
		doc.insert(ignore_permissions=True)

		tax = frappe.get_doc(
			{
				"doctype": "Tax Authority Profile",
				"company": doc.name,
				"country_code": "EG",
				"adapter_id": "EGY_ETA",
				"api_base_url": "https://eta.example/tpc3",
			}
		).insert(ignore_permissions=True)
		sign = frappe.get_doc(
			{
				"doctype": "Signing Profile",
				"company": doc.name,
				"profile_name": "TPC3 Sign",
				"certificate_vault_ref": "vault://tpc3/sign",
			}
		).insert(ignore_permissions=True)

		doc.eta_einvoice_enabled = 1
		doc.company_tax_authority_profile = tax.name
		doc.company_signing_profile = sign.name
		doc.save(ignore_permissions=True)
		self.assertTrue(frappe.db.exists("Company", doc.name))
