import os
import datetime
import logging
import logging.handlers

logger = logging.getLogger()

logger.setLevel(logging.INFO)

filepath = os.path.join(os.path.dirname(
    os.path.abspath(__file__)), '..', '_log', 'stream', 'stream')
fileHandler = logging.handlers.TimedRotatingFileHandler(
    filename=filepath, when='midnight', interval=1, encoding='utf-8', utc=True, atTime=datetime.time(hour=0))

# fomatter = logging.Formatter('[%(levelname)s|%(filename)s:%(lineno)s] %(asctime)s > %(message)s')
fomatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')

fileHandler.setFormatter(fomatter)

logger.addHandler(fileHandler)

# logger.debug("===========================")
# logger.info("TEST START")
# logger.warning("스트림으로 로그가 남아요~")
# logger.error("파일로도 남으니 안심이죠~!")
# logger.critical("치명적인 버그는 꼭 파일로 남기기도 하고 메일로 발송하세요!")
# logger.debug("===========================")
# logger.info("TEST END!")
