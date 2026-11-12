from erpnext.slim import remove_modules


def execute():
	remove_modules("Telephony", "Communication")
