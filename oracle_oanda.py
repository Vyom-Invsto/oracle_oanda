import oandapyV20
import oandapyV20.endpoints.accounts as accounts
import oandapyV20.endpoints.instruments as instruments
import pytz
import asyncio
import websockets
import json
from datetime import datetime

# Specify the time zone for India
india_timezone = pytz.timezone("Asia/Kolkata")


class OANDA:
    def __init__(self) -> None:
        self.account_id = None
        self.access_token = None
        self.api = None

    def login(self, account_id, access_token):
        """
        To login on OANDA API

        Args:
            account_id (str): your OANDA account id
            access_token (str): access token to OANDA API
        """
        self.account_id = account_id
        self.access_token = access_token
        self.api = oandapyV20.API(access_token=self.access_token)

    def get_accountdetails(self):
        try:
            r = accounts.AccountDetails(self.account_id)
            ret = self.api.request(r)
        except Exception as e:
            print(f"Error with OANDA: {e}")
            ret = None
        return ret

    def get_historicaldata(self, instrument, granularity, from_date, to_date=None):
        params = {
            "granularity": granularity,
            "from": from_date,
            "to": to_date,
        }
        r = instruments.InstrumentsCandles(instrument=instrument, params=params)
        data = self.api.request(r)
        return data


    async def on_message(self, message):
        OANDA.onmessage(message)

    def main(self, stopTime):
        print("Starting WebSocket stream")

        async def run():
            async with websockets.connect(
                f"wss://stream-fxpractice.oanda.com/v3/accounts/{self.account_id}/pricing/stream?instruments={','.join(OANDA.instruments)}",
                extra_headers={"Authorization": f"Bearer {self.access_token}"}
            ) as websocket:
                await self.on_connect(websocket)
                async for message in websocket:
                    await self.on_message(json.loads(message))
                    if datetime.now(india_timezone).strftime("%H:%M") >= stopTime:
                        await websocket.close()
                        break

        asyncio.get_event_loop().run_until_complete(run())

    def get_livedata(self, instruments: list, onmessage: callable, onerror: callable, onclose: callable, stopTime: str = "15:30"):
        OANDA.instruments = instruments
        OANDA.onmessage = onmessage
        OANDA.onerror = onerror
        OANDA.onclose = onclose
        self.main(stopTime=stopTime)