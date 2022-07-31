import json
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import pandas as pd
import time
from datetime import datetime
from celery import shared_task
from .models import Prediction
from scipy.stats import poisson
import numpy as np
import os

time.sleep(5)






@shared_task
def ScrapeResult():
    
    options = Options()
    
    options.add_argument("--no-sandbox") 
    options.add_argument("--remote-debugging-port=9222")  # this
    options.add_argument("--headless") 
    options.add_argument("--disable-dev-shm-using")  
    
    driver = webdriver.Remote('http://chromed:4444/wd/hub',options=options)
    driver.get('wwww.google.com')
    driver.save_screenshot('image.png')
    driver.Quit();
