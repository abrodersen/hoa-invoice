import datetime
import os

from gql import gql, Client
from gql.transport.aiohttp import AIOHTTPTransport

class WaveClient:
    def __init__(self):
        self.token = os.environ.get("WAVE_TOKEN", "")
        self.transport = AIOHTTPTransport(
            url="https://gql.waveapps.com/graphql/public",
            headers={"Authorization": f"Bearer {self.token}"})
        self.client = Client(transport=self.transport, fetch_schema_from_transport=True)

    def get_default_business(self):
        query = gql(
            """
            query {
                business {
                    id
                }
            }
            """
        )

        result = self.client.execute(query)
        return result['business']

    def get_customers(self):
        query = gql(
            """
            query {
                business {
                    id
                    customers(sort: [NAME_ASC]) {
                        edges {
                            node {
                                id
                                name
                                firstName
                                lastName
                                email
                            }
                        }
                    }  
                }
            }
            """
        )

        result = self.client.execute(query)
        return [edge['node'] for edge in result['business']['customers']['edges']]

    def get_invoices(self, *, year):
        query = gql(
            """
            query($invStart: Date!, $invEnd: Date!) {
                business {
                    invoices(invoiceDateStart: $invStart, invoiceDateEnd: $invEnd, sort: [INVOICE_NUMBER_ASC] ) {

                        edges {
                            node {
                                id
                                status
                                invoiceNumber
                                pdfUrl
                                customer {
                                    id
                                    name
                                    firstName
                                    lastName
                                    email
                                }
                            }
                        }
                    }  
                }
            }
            """
        )

        result = self.client.execute(query, variable_values={"invStart": f"{year}-01-01", "invEnd": f"{year}-12-31"})
        return [edge['node'] for edge in result['business']['invoices']['edges']]

    def get_products(self):
        query = gql(
            """
            query {
                business {
                    products(sort: [NAME_DESC], isArchived: false) {
                        edges {
                            node {
                                id
                                name
                                description
                            }
                        }
                    }  
                }
            }
            """
        )

        result = self.client.execute(query)
        return [edge['node'] for edge in result['business']['products']['edges']]

    def approve_invoice(self, *, id):
        data = {
            "id": id,
            "status": "SAVED",
        }
        query = gql(
            """
            mutation($input: InvoicePatchInput!) {
                invoicePatch(input: $input) {
                    didSucceed
                    inputErrors {
                        code
                        message
                        path
                    }
                    invoice {
                        id
                    }
                }
            }
            """
        )
        result = self.client.execute(query, variable_values={"input": data})
        return result

    def mark_invoice_sent(self, *, id):
        data = {
            "invoiceId": id,
            "sendMethod": "GMAIL"
        }
        query = gql(
            """
            mutation($input: InvoiceMarkSentInput!) {
                invoiceMarkSent(input: $input) {
                    didSucceed
                    inputErrors {
                        code
                        message
                        path
                    }
                    invoice {
                        id
                    }
                }
            }
            """
        )
        result = self.client.execute(query, variable_values={"input": data})
        return result

    def gen_invoice(self, *, business_id, customer_id, year, product_id):
        data = {
            "status": "DRAFT",
            "businessId": business_id,
            "customerId": customer_id,
            "dueDate": f"{year}-05-01",
            "items": [
                {"productId": product_id}
            ]
        }
        query = gql(
            """
            mutation($input: InvoiceCreateInput!) {
                invoiceCreate(input: $input) {
                    didSucceed
                    inputErrors {
                        code
                        message
                        path
                    }
                    invoice {
                        id
                    }
                }
            }
            """
        )
        result = self.client.execute(query, variable_values={"input": data})
        return result
