import re
import json
import logging
import azure.functions as func

from typing import Dict
from odooapiclient.client import Client


client = Client(host='andriisem.odoo.com', dbname='andriisem', ssl=True)
client.authenticate(login='', pwd='')

def get_country_id(country_name: str) -> list:
    return client.search('res.country', [('name', '=', country_name)])
    
def get_res_partner_id(**kw: Dict) -> int:
    res_partner_id = client.search('res.partner', [('email', '=', kw.get('email'))])
    if res_partner_id:
        return res_partner_id[0]
    else:
        res_partner_id = client.create('res.partner', {
            'name': '%s %s' % (kw.get('fist_name'), kw.get('last_name')),
            'zip': kw.get('postal'),
            'email': kw.get('email'),
            'street': kw.get('addr_line1'),
            'street2': kw.get('addr_line2'),
            'city': kw.get('city'),
            'country_id': kw.get('country_id') and kw.get('country_id')[0] or False,
        })
        return res_partner_id


def get_invoice_payment_terms_id(payment_terms: str) -> list:
    payment_term_id = client.search('account.payment.term', [('name', '=', payment_terms)])
    if payment_term_id:
        return payment_term_id[0]
    else:
        days = int(re.search(r'\d+', payment_terms).group())
        res_partner_id = client.create('account.payment.term', {
            'name': payment_terms,
            'line_ids': [(0, 0, {
                'value': 'balance',
                'days': days
            })]
        })
        return res_partner_id 


def create_invoice(res_patner_id: int, payment_terms: str) -> int: 
    payment_term_id = get_invoice_payment_terms_id(payment_terms)
    invoice_id = client.create('account.move', {
        'type': 'out_invoice',
        'partner_id': res_patner_id,
        'invoice_payment_term_id': payment_term_id
    })
    return invoice_id


def main(req: func.HttpRequest) -> func.HttpResponse:
    form = req.form.getlist('rawRequest') and json.loads(req.form.getlist('rawRequest')[0])
    if form:
        fist_name, last_name = form['q8_fullName8']['first'], form['q8_fullName8']['last']
        email = form.get('q38_email38')
        addr_line1 = form['q34_invoiceAddress']['addr_line1']
        addr_line2 = form['q34_invoiceAddress']['addr_line2']
        city = form['q34_invoiceAddress']['city']
        postal = form['q34_invoiceAddress']['postal']
        country_id = get_country_id(form['q34_invoiceAddress']['country'])
        payment_terms = form.get('q63_paymentTerms')

        res_patner_id = get_res_partner_id(
            fist_name=fist_name, last_name=last_name,
            email=email, addr_line1=addr_line1,
            addr_line2=addr_line2, city=city,
            postal=postal, country_id=country_id,
        )
        invoice_id = create_invoice(res_patner_id, payment_terms)

    return func.HttpResponse(
        "Invoice created", status_code=200
    )
