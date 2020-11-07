import dateutil.parser
import datetime
import pytz

from requests_toolbelt import sessions

import api_config


def init_http_api(session):
    s = sessions.BaseUrlSession(base_url=api_config.API_BASE)

    s.headers.update({
        "X-Client-ID": api_config.CLIENT_ID,
        "X-Client-Secret": api_config.CLIENT_SECRET
    })

    if "accessToken" in session:
        expiry = dateutil.parser.parse(session["sessionExpires"])

        if expiry < pytz.UTC.localize(datetime.datetime.utcnow()):
            del session["accessToken"]
        else:
            s.headers.update({
                "Authorization": "Bearer " + session["accessToken"],
            })

    return s
