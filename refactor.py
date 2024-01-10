from time import time as time_now
from time import sleep, strftime
from selenium import webdriver
from selenium.webdriver.chrome.service import Service

service = Service()
options = webdriver.ChromeOptions()
driver = webdriver.Chrome(service=service, options=options)
from os import makedirs, path
from bs4 import BeautifulSoup
import argparse
from sys import argv
import threading
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from pytz import timezone    
from random import randint
import discord
from discord import Webhook, RequestsWebhookAdapter, File
import schedule
from config import config
import array as arr

import os

global GW_DAY
global GW_NUM
global GW_URL
global RIVAL_URL
global JP_TZ
global PING_THRESHOLD
global RESET_THRESHOLD
global HAS_PINGED
global ENABLE_ALERT_PING
global ENABLE_DISCORD
global SPREADSHEET_NAME


START_HOUR = 9
END_HOUR = 2

webhook_id = os.getenv('WEBHOOK_ID')
webhook_url = os.getenv('WEBHOOK_URL')