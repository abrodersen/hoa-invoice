import datetime
import sys

from .email import GmailClient
from .pdf import get_pdf
from .wave import WaveClient

def main():
    """Entry point for the application script"""
    if sys.argv[1] == "generate":
        gen_invoices()

    if sys.argv[1] == "authorize":
        authorize()

    if sys.argv[1] == "approve_drafts":
        approve_drafts()

    if sys.argv[1] == "send_invoices":
        send_invoices()

    if sys.argv[1] == "send_single":
        send_invoices(invoice_number=sys.argv[2])
    

def gen_invoices():
    year = datetime.date.today().year
    print(f"generating invoices for {year}")

    client = WaveClient()
    bus_id = client.get_default_business()['id']
    customers = client.get_customers()
    invoices = client.get_invoices(year=year)
    products = client.get_products()
    skip_customer_ids = set([invoice['customer']['id'] for invoice in invoices])

    product_id = next((product['id'] for product in products if product['name'] == "2024 Membership Dues"), None)

    if not product_id:
        print ("no valid product found for invoice generation, exiting")
        return

    for customer in customers:
        cust_id = customer['id']
        if cust_id in skip_customer_ids:
            print(f"skipping invoice for customer {cust_id}")
            continue

        print(f"gen invoice for {cust_id}")
        result = client.gen_invoice(business_id=bus_id, customer_id=cust_id, year=year, product_id=product_id)
        print(f"new invoice: {result}")

def approve_drafts():
    year = datetime.date.today().year
    print(f"approving invoices for {year}")
    
    client = WaveClient()
    invoices = client.get_invoices(year=year)

    for invoice in invoices:
        inv_id = invoice["id"]
        status = invoice['status']
        inv_num = invoice["invoiceNumber"]
        print(f"inv = {inv_num}, status = {status}")
        if status != "DRAFT":
            print(f"skipping non-draft invoice {inv_num}")
            continue

        result = client.approve_invoice(id=inv_id)
        print(f"approve invoice: {result}")

def authorize():
    client = GmailClient()
    client.get_creds()

def send_invoices(*, invoice_number=None):
    year = datetime.date.today().year
    print(f"sending invoices for {year}")
    
    client = WaveClient()
    invoices = client.get_invoices(year=year)
    email = GmailClient()

    for invoice in invoices:
        print(invoice)
        inv_id = invoice["id"]
        status = invoice['status']
        inv_num = invoice["invoiceNumber"]
        customer = invoice["customer"]
        cust_name = f"{customer['firstName']} {customer['lastName']}"
        cust_email = customer["email"]

        if invoice_number and inv_num != invoice_number:
            print(f"skipping invoice {inv_num}")
            continue

        if status == "DRAFT":
            print(f"skipping draft invoice {inv_num}")
            continue

        if not invoice_number and status == "SENT":
            print(f"skipping sent invoice {inv_num}")
            continue

        if not cust_email:
            print(f"skipping customer without email invoice {inv_num}")
            continue

        inv_pdf = invoice["pdfUrl"]
        print(f"fetching invoice {inv_num} pdf from {inv_pdf}")
        pdf_data = get_pdf(url=inv_pdf)
        send_addr = f"{cust_name} <{cust_email}>"
        print(f"sending invoice to {send_addr}")
        result = email.send_message(to=send_addr, year=year, pdf=pdf_data)
        print(f"send result: {result}")
        result = client.mark_invoice_sent(id=inv_id)
        print(f"update result: {result}")
        

