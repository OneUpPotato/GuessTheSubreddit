import sentry_sdk

initiated = False
def init_sentry(url):
    global initiated
    sentry_sdk.init(url)
    initiated = True

def capture_exception(exception):
    if initiated:
        sentry_sdk.capture_exception(exception)
