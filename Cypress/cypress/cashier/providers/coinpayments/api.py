import base64
import datetime
import hashlib
import hmac
import json
from io import BytesIO

import requests
from PIL import Image
from django.core.files import File
from django.utils.timezone import now

from cashier.models import CryptoCurrencyProviderCode, CryptoCurrencies
from parameters.models import VHostParameterRegistry


class CoinPaymentsAPI(object):
    client_id = False
    client_secret = False
    vhost = False
    urls = {
        "_prefix":"https://a-api.coinpayments.net/api/",
        "create_invoice":"v2/merchant/invoices",
        "currencies":"v2/currencies",
        "rates":"v2/rates",
        "create_client_webhook":"v1/merchant/clients/"

    }

    def __init__(self, vhost, **kwargs):
        # print("CoinPaymentsAPI.__init__")
        self.vhost = vhost
        self.client_id = VHostParameterRegistry.objects.get_or_create(vhost=self.vhost,application="cashier.providers.coinpayments",name="client_id")[0].value_text
        self.client_secret = VHostParameterRegistry.objects.get_or_create(vhost=self.vhost,application="cashier.providers.coinpayments",name="client_secret")[0].value_text
        self.webhook_ep = VHostParameterRegistry.objects.get_or_create(vhost=self.vhost,application="cashier.providers.coinpayments",name="client_webhook")[0].value_text



    def calculate_signature(self, method, url, payload, date):
        sig_string = ''.join(['\ufeff', method, url, self.client_id, date, payload])
        # print(sig_string)
        sig_bytes = hmac.new(
            self.client_secret.encode(),
            sig_string.encode(),
            hashlib.sha256
        ).digest()
        return base64.b64encode(sig_bytes).decode()

    def build_headers(self, method, url, payload):
        date = now().strftime('%Y-%m-%dT%H:%M:%S')
        # print("d")
        signature = self.calculate_signature(method, url, payload, date)
        # print("s")
        return {
            'Content-Type': 'application/json',

            'X-CoinPayments-Client': self.client_id,
            'X-CoinPayments-Timestamp': date,
            'X-CoinPayments-Signature': signature,
        }

    def validate_request(self, method, request):
        cp_client = request.META['HTTP_X_COINPAYMENTS_CLIENT']
        cp_ts = request.META['HTTP_X_COINPAYMENTS_TIMESTAMP']
        cp_sig = request.META['HTTP_X_COINPAYMENTS_SIGNATURE']
        signature = self.calculate_signature(method, f"{request.META["HTTP_X_FORWARDED_PROTO"]}://{request.META["HTTP_HOST"]}{request.path}", payload=request.body.decode("utf-8"), date=cp_ts)
        return cp_sig == signature

    def create_client_webhook(self,client_id):
        url = self.urls["_prefix"]+self.urls["create_client_webhook"]+client_id+"/webhook"
        payload = {
            "notificationsUrl":self.webhook_ep,
            "notifications":["invoiceCreated","invoicePending","invoicePaid","invoiceCompleted","invoiceCancelled","invoiceTimedOut"]
        }
        return self.post_to_url(url, payload,False)

    def get_currency_api_code(self,cuuid):
        try:
            ccpc = CryptoCurrencyProviderCode.objects.get(currency__uuid=cuuid,provider="cashier.providers.coinpayments")
            currencyObj = CryptoCurrencies.objects.get(uuid=cuuid)
        except CryptoCurrencyProviderCode.DoesNotExist:
            currencyObj = CryptoCurrencies.objects.get(uuid=cuuid)
            acurrency = self.get_from_url("currencies",f"?q={currencyObj.symbol}&types&capabilities")
            if len(acurrency) > 0:
                acurrency = acurrency[0]
                # print(acurrency)
                if "id" in acurrency:
                    currObj = CryptoCurrencies.objects.get(uuid=cuuid,vhost=self.vhost)
                    ccpc = CryptoCurrencyProviderCode(currency=currObj,provider="cashier.providers.coinpayments",code=acurrency["id"])
                    if 'logo' in acurrency:
                        try:
                            imgreg = requests.request("GET", acurrency["logo"]["imageUrl"])
                            itype = imgreg.headers["Content-Type"]
                            img_io = BytesIO(imgreg.content)
                            img_name = str(currObj.uuid)
                            if itype == "image/svg+xml":
                                img_name += ".svg"
                            elif itype == "image/png":
                                img_name += ".png"
                            elif itype == "image/jpeg":
                                img_name += ".jpg"
                            elif itype == "image/webp":
                                img_name += ".webp"
                            elif itype == "image/gif":
                                img_name += ".gif"
                            elif itype == "image/avif":
                                img_name += ".avif"
                            django_file = File(img_io, name=img_name)
                            currObj.logo.save(img_name,django_file,save=True)
                            currObj.save()
                        except Exception as e:
                            print(f"Unable to load logo: {e} for Crypto currency {currencyObj.uuid}")
                        # print("Image saved.")
                    ccpc.save()
                    return ccpc.code,currencyObj
            return False
        return ccpc.code,currencyObj

    def get_rate(self,curr1,curr2):
            return self.get_from_url("rates",f"?from={curr1}&to={curr2}")['items'][0]['rate']

    def get_from_url(self,url,data):
        if url not in self.urls:
            print(f"Url key {url} not in self.urls.")
            raise ValueError(f"Url key {url} not in self.urls.")
        url = self.urls["_prefix"] + self.urls[url]+data
        # print(url)
        try:
            response = requests.request(
                method="GET",
                url=url,

            )
            # print(response)
            try:
                rjson =  response.json()
                # print(rjson)
                return rjson
            except ValueError:
                return {'result': 200 <= response.status_code < 300}
        except requests.RequestException as e:
            return {'error': str(e)}

    def create_invoice(self,invoice_data):
        invoice_data = self.post_to_url("create_invoice",invoice_data)['invoices'][0]
        return invoice_data

    def post_to_url(self,url,payload,safe=True):

        if url not in self.urls and safe:
            print(f"Url key {url} not in self.urls.")
            raise ValueError(f"Url key {url} not in self.urls.")
        url = self.urls["_prefix"] + self.urls[url]
        jpayload = json.dumps(payload)
        print(jpayload)
        print(url)
        headers = self.build_headers("POST", url, jpayload)
        print(headers)
        try:
            response = requests.request(
                method="POST",
                url=url,
                headers=headers,
                data=jpayload
            )
            try:
                rjson =  response.json()
                # print(rjson)
                return rjson
            except ValueError:
                print("VALUE ERRORRRR")
                print(response.text)
                print(response.status_code)
                return {'result': 200 <= response.status_code < 300}

        except requests.RequestException as e:
            print("TYPE ERROR")
            return {'error': str(e)}


