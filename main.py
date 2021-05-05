##################################
# GITHUB.COM/2e4
##################################
# GITHUB.COM/2e4/python-exchange_code-generator
##################################
# IF YOU DONT MIND LEAVE A STAR ⭐
##################################
# PYTHON EXCHANGE CODE GENERATOR
##################################

import requests, json, asyncio, time

class exchangeCode:

    def __init__(self) -> None:
        self.config = json.loads(open("config.json", "r").read())
        self.loop = asyncio.get_event_loop()
        self.session = requests.session()
        self.start()

    def log(self, type, content):
        print(f"[{type}] {content}")

    async def generateAccessToken(self, session):
        accessToken = session.post(
            "https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token", 
            headers=
            {
                'Authorization': f"basic {self.config['clientToken']}"
            },
            data=
            {
                'grant_type':'client_credentials', 
                'token_type':'eg1'
            }
        )
        self.log("+", "Generated access token.")
        return accessToken.json()

    async def generateDeviceCode(self, session, accessToken):
        deviceCode = session.post(
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/deviceAuthorization", 
            headers=
            {
                "Authorization": f"bearer {accessToken['access_token']}",
                "Content-Type": "application/x-www-form-urlencoded"
            }
        )
        self.log("+", "Created device Code.")
        return deviceCode.json()

    async def awaitAuthorization(self, session, deviceCode):
        while True:
            request = session.post(
                url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/token",
                headers=
                {
                    "Authorization": f"basic {self.config['switchToken']}",
                    "Content-Type": "application/x-www-form-urlencoded"
                },
                data=
                    {
                        "grant_type": "device_code","device_code": deviceCode['device_code']
                    }
                )
            requestJson = request.json()
            if request.status_code == 200:
                self.log("+", "Authorized.")
                break
            else:
                if requestJson["errorCode"] == "errors.com.epicgames.account.oauth.authorization_pending":
                    await asyncio.sleep(3)
                    pass
                elif requestJson["errorCode"] == "errors.com.epicgames.not_found":
                    self.log("-", "Device Code not found, time probably ran out or you did not authorize.")
                    time.sleep(5)
                    return requestJson
                else:
                    await asyncio.sleep(3)
        return requestJson

    async def generateExchangeCode(self, session, accessToken):
        request = session.get(
            url="https://account-public-service-prod03.ol.epicgames.com/account/api/oauth/exchange",
            headers=
            {
                "Authorization": f"bearer {accessToken}"
            }
        )
        return request.json()

    def start(self):
        accessToken = self.loop.run_until_complete(self.generateAccessToken(session=self.session))
        deviceCode = self.loop.run_until_complete(self.generateDeviceCode(session=self.session, accessToken=accessToken))
        self.log("+", "Awaiting Authorization.")
        self.log("+", f"Please log on the account using this link: {deviceCode['verification_uri_complete']}")
        awaitAuthorization = self.loop.run_until_complete(self.awaitAuthorization(session=self.session, deviceCode=deviceCode))
        try:
            if awaitAuthorization["access_token"]:
                self.log("+", "Generated access token & refresh token.")
                self.log("+", f"Access Token: {awaitAuthorization['access_token']}")
                self.log("+", f"Refresh Token: {awaitAuthorization['refresh_token']}")
                time.sleep(5)
                exchangeCode = self.loop.run_until_complete(self.generateExchangeCode(session=self.session, accessToken=awaitAuthorization["access_token"]))
        except:
            self.log("-", "Exiting.")
            return
        if exchangeCode["code"]:
            self.log("+", "Generated exchange code.")
            self.log("+", f"Exchange Code: {exchangeCode['code']}")
            time.sleep(30)
        else:
            self.log("-", "Something went wrong while generating exchange code.")
            print(exchangeCode)
            time.sleep(5)

exchangeCode()
