import time
import json
from xvfbwrapper import Xvfb
from selenium import webdriver
import pandas as pd
import logging
import sys
import psycopg2


# Set up logging configuration in scrappy.log
def create_logger(name: str, file_name: str) -> logging.Logger:
    try:
        log = logging.getLogger(name)
    except ValueError or TypeError:
        print("Error with logger name")
        sys.exit(1)
    log.setLevel(logging.DEBUG)
    try:
        fh = logging.FileHandler(file_name)
    except TypeError or ValueError:
        print("Error with logger filepath")
        sys.exit(1)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(levelname)s - %(asctime)s - %(process)s - %(name)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    log.addHandler(fh)
    log.addHandler(ch)
    return log


# Load json file with configuration (website, scraping targets, db info)
def load_config(file: str) -> dict:
    try:
        with open(file) as f:
            conf = json.load(f)
    except Exception as ie:
        logger.error("Error Loading Config File", ie)
        sys.exit(1)
    return conf


# TODO Set up DB Connection
class DatabaseConnection:
    def __init__(self, data):
        self.url = data['url']
        self.port = data['port']
        self.dbuser = data['dbuser']
        self.dbpw = data['dbpw']

    def create_connection(self):
        pass




class DynScraper:
    def __init__(self, data):
        self.WEBSITE = data['website']
        self.targets = data['scrape']
        self.df = pd.DataFrame()
        self.driver = None
        self.v_display = None

    def create_v_display(self):
        self.v_display = Xvfb()
        self.v_display.start()

    def terminate_v_display(self):
        self.v_display.stop()

    def connect_website(self):
        # Creating the web driver
        try:
            self.driver = webdriver.Firefox()
        except Exception as ie:
            logger.error("Error creating WebDriver", ie)
            sys.exit(1)
        # Connecting to the website to start scraping
        try:
            self.driver.get(self.WEBSITE)
        except Exception as ie:
            logger.error("Error connecting to website", ie)
            sys.exit(1)

        logger.info(msg="Scraping: {}".format(self.driver.title))
        logger.debug(msg="URL: {}".format(self.WEBSITE))
        # Sleep to allow JS scripts to run and create dynamic data
        time.sleep(3)
        
    def scrape(self):
        res = {}
        for elem in self.targets:
            web_data = self.driver.find_element_by_xpath(self.targets[elem])
            res[elem] = web_data.text
            if web_data.text is None:
                logger.warning("Element: {}, had no information (empty)".format(elem))
        final_results = pd.DataFrame(data=res, index=[0])
        self.df = self.df.append(final_results, ignore_index=True)
        return self.df
# TODO Set up function to process dataframe and insert to DB


if __name__ == '__main__':
    # Create logger and load config file
    logger = create_logger("Scrappy_App", "scrappy.log")
    config = load_config("config.json")

    # Starting Script and Instantiating Class
    logger.info(msg="Script Started")
    try:
        scrape = DynScraper(config)
    except Exception as e:
        logger.error("Error Instantiating class with this config file", e)
        sys.exit(1)

    # Creating the virtual display for Selenium
    try:
        logger.debug("Creating Virtual Display")
        scrape.create_v_display()
    except Exception as e:
        logger.error("Error Creating Virtual Display", e)
        sys.exit(1)

    # Creating WebDriver and connecting to website
    logger.debug(msg="Creating WebDriver and connecting to website")
    scrape.connect_website()

    logger.info(msg="Start Scraping")
    for i in range(10):
        try:
            results = scrape.scrape()
        except Exception as e:
            logger.error("Error Scraping", e)
            sys.exit(1)
        # TODO Change logic here for database insert
        print(results)
        time.sleep(1)
    logger.debug(msg="Closing Virtual Display")
    try:
        scrape.terminate_v_display()
    except Exception as e:
        logger.error("Error closing the Virtual Terminal", e)
    logger.info(msg="Script Ended")
    print(scrape.df)
    sys.exit(0)
