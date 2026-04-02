import json
from decimal import Decimal

import uuid

from cashier.models import DummyProviderTXStub, CashierVDomainParameters, ProviderTX, CryptoCurrencies
from cashier.providers.coinpayments.api import CoinPaymentsAPI


class DepositProvider(object):
    def create_deposit(self,domain,account,amount,fees,**kwargs):
        if amount <= 0:
            raise ValueError("amount must be > 0")
        if amount > 10000:
            raise ValueError("amount must be <= 10000")
        cpApi = CoinPaymentsAPI(account.vhost)
        cryptoParams = CashierVDomainParameters.objects.get_or_create(vhost=account.vhost)[0]
        if "currency" in kwargs:
            currency,cObj1 = cpApi.get_currency_api_code(kwargs["currency"])
            cuuid = kwargs.get("currency")
        else:
            currency,cObj1 = cpApi.get_currency_api_code(cryptoParams.base_crypto.uuid)
            cuuid = cryptoParams.uuid
        # print(cryptoParams.base_crypto.uuid)
        # print(cuuid)
        # cObj1 = CryptoCurrencies.objects.get(uuid=cuuid)

        if "paymentCurrency" in kwargs:
            pcurrency,cObj2 = cpApi.get_currency_api_code(kwargs["paymentCurrency"])
            puuid = kwargs.get("paymentCurrency")
        else:
            pcurrency = currency
            puuid = cuuid
            cObj2 = cObj1

        if currency != pcurrency:
            rate = cpApi.get_rate(pcurrency,currency)
        else:
            rate = 1

        invoice_data =  {
            "client_id": str(account.uuid),
            "vhost_id": str(account.vhost.uuid),
            "amount": str(amount),
            "invoice_currency": str(cuuid),
            "payment_currency": str(puuid),
            "xchng_rate": str(rate),
        },
        cbody = {
            "client_id":str(account.uuid),
            "currency":currency,
            "items": [
                {
                 "name":"AI Processing Token",

                 "quantity":{
                     "value":str(amount),
                     "type":2
                 },
                "amount":str(amount),
                 }
            ],
            "amount":{
                "breakdown": {
                    "subtotal": str(amount),
                },
                "total": str(amount),
            },
            "isEmailDelivery":True,
            "emailDelivery":{
                "to":account.email1,
                "cc":account.email2,
            },
            "buyer": {
                "name": {
                    "firstName": "",
                    "lastName": "",

                },
                # "address": {
                #     "address1":"",
                #     "address2": "",
                #     "address3": "",
                #     "provinceOrState":"",
                #     "city":"",
                #     "suburbOrDistrict":"",
                #     "countryCode":"",
                #     "postalCode":"",
                # }

            },
            # "shipping": {
            #     "hasData":False,
            #      "method": "",
            #      "companyName": "",
            #      "name": {
            #         "firstName": "",
            #         "lastName": ""
            #      },
            #     "emailAddress": "",
            #     "phoneNumber": "",
            #     "address": {
            #         "address1": "",
            #         "address2": "",
            #         "address3": "",
            #         "provinceOrState": "",
            #         "city": "",
            #         "suburbOrDistrict": "",
            #         "countryCode": "",
            #         "postalCode": ""
            #     }
            #     },
                "payment": {
                    "refundEmail":account.email1
                },
                "customData": {
                    "client_id": str(account.uuid),
                    "vhost_id": str(account.vhost.uuid),
                    "amount": str(amount),
                    "invoice_currency": str(cuuid),
                    "payment_currency": str(puuid),
                    "xchng_rate": str(rate),
                },
                "requireBuyerNameAndEmail":False,
                "merchantOptions": {
                    "showAddress": False,
                    "showEmail": False,
                    "showPhone": False,
                    "showRegistrationNumber": False,
                    "additionalInfo": ""
                },
                "useCoinReservation":False,
                "hideShoppingCart":True

        }
        if pcurrency:
            cbody["payment"]["paymentCurrency"] = pcurrency


        print(cbody)
        print("--------")
        print(json.dumps(cbody))
        print("--------")
        pinvoice_data = cpApi.create_invoice(cbody)
        # print(pinvoice_data["hotWallet"])
        # print(pinvoice_data["payment"])
        # NOTE: Crypto objects are backwards to represent the payment currency being the primary currency in the invoice.
        ptxObj = ProviderTX(vhost=account.vhost,provider_tx=uuid.UUID(pinvoice_data["id"]),domain=account.domain,provider="cashier.providers.coinpayments",
                            cryp1=cObj2,cryp2=cObj1,url=pinvoice_data["link"],type="DEPOSIT",pending=pinvoice_data["hotWallet"]["amount"],
                            account=account,amount=pinvoice_data["hotWallet"]["amount"],hot_wallet=pinvoice_data["hotWallet"]["addresses"]["address"],
                            provider_data=pinvoice_data,invoice_data=invoice_data,provider_fees=Decimal(pinvoice_data["payment"]["paymentCurrencies"][0]["approximateNetworkAmount"]))
        ptxObj.save()
        api_return = {
            "uuid": str(ptxObj.uuid),
            "prov_id": str(ptxObj.provider_tx),
            "provider": str(ptxObj.provider),
            "currency":str(cObj2.uuid),
            "currency_id":str(pcurrency),
            "currency_prefix":cObj2.uri_prefix,
            "currency_name":cObj2.name,
            "currency_symbol":cObj2.symbol,
            "paymentCurrency":str(cObj2.uuid),
            "original_currency":cObj1.symbol,
            "rate":str(rate),
            "hot_wallet":ptxObj.hot_wallet,
            "tx_expires":pinvoice_data["hotWallet"]["expires"],
            "subtotal":str(pinvoice_data["payment"]["paymentCurrencies"][0]["amount"]),
            "network": str(pinvoice_data["payment"]["paymentCurrencies"][0]["approximateNetworkAmount"]),
            "refundEmail":str(pinvoice_data["payment"]["refundEmail"]),
            "amount":ptxObj.amount,
            "url":ptxObj.url
        }
        if cObj2.logo:
            api_return["currency_logo"] = cObj2.logo.url
        print(api_return)

        # Create the webhook ~
        #wh_create = cpApi.create_client_webhook(str(account.uuid))
        #print(wh_create)
        # # NOTE: Returns -2 (for PENDING INTERNAL Deposit); api_return data (for payment flow), and  TX Object.
        # # in the API design of the cashier, receiving a -2 means the Transaction is pending an internal deposit.
        # # That means, Athena/Cashier renders the Payment page for the user to follow in the flow using the selected provider.
        # # We return -2, the provider TX id, and a Data Object which contains all the information relevant to the provider in
        # # rendering the next step of the flow downstream.
        # # When we pass a -2; the UI will actually generate a UI for payment processing for the customer.
        # # We return -2, the api_return which contains all the data needed to generate the QR code, and the transaction object.
        return -2, api_return, ptxObj

