import logging
# from config import CrawlerConfig

# create logger
logger = logging.getLogger('crawler')
logger.setLevel(logging.DEBUG)

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

#file handler
# fileName=CrawlerConfig().app_log
# fh = logging.FileHandler("{0}".format(fileName))

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# add formatter to ch
ch.setFormatter(formatter)
#fh.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
#logger.addHandler(fh)

if __name__=="__main__":
	# 'application' code
	logger.debug('debug message')
	logger.info('info message')
	logger.warn('warn message')
	logger.error('error message')
	logger.critical('critical message')
