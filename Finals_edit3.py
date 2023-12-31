### User defined config variables
### Edit the variables below to suit your needs
CREW_URL = 'http://game.granbluefantasy.jp/#guild/detail/1522224'

# Worksheets in the spreadsheet must follow the following naming 
# convention: GW ### - Day # (e.g. GW 041 - Day 2)

######################################################
# Note from Hybri: CTRL+F and search for the [edit_this] placeholder.
# Replace everything between and including the brackets.
######################################################


# Spreadsheet must obey certain naming and formatting conventions.
# otherwise, it'll fail to work.
SPREADSHEET_NAME = 'Zenosyne GW'

ENABLE_ALERT_PING = False
PING_THRESHOLD = 100000000
RESET_THRESHOLD = 200000000

# To get the role ID of a certain role, mention that role, 
# right click on the mention itself, and select 'Copy ID'. 
# You must enable Developer Mode in Settings>Appearance for 
# that option to show up.
PING_ROLE_ID = '804666854131630101'

ENABLE_DISCORD = True
# Create a Discord webhook and copy the URL, the URL should 
# have the following format: 
# https://discordapp.com/api/webhooks/<DISCORD_WEBHOOK_ID>/<DISCORD_WEBHOOK_TOKEN>
DISCORD_WEBHOOK_ID = '868298212786700338'

DISCORD_WEBHOOK_TOKEN = 'PZGtFlmglG14Oxo2e2kTtY71PkHH-xJYCvqW1GlP9XOJ8QY8A2fSsMss_bsZiVCTbtxo'

# Substitute placeholders with instructions below:
# The hours that your match starts at. This uses YOUR PC clock.
# Adjust this accordingly in 24 hour time with values between
# 1 and 24 inclusive.
START_HOUR = 9
END_HOUR = 2

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

GW_DAY = '4'
GW_NUM = '062'
GW_URL = 'http://game.granbluefantasy.jp/#event/teamraid{}'.format(GW_NUM)
JP_TZ = timezone('Asia/Tokyo')
RIVAL_URL = None
HAS_PINGED = False

CHROME_ARGUMENTS = '--disable-infobars'

LOG_FILE = '[{}]granblue-scraper.log'.format(strftime('%m-%d_%H%M'))

def log(message):
  '''Prints to console and outputs to log file'''

  try:
    with open('.\\logs\\' + LOG_FILE, 'a',
        encoding='utf-8', newline='') as fout:
      message = '[%s] %s' % (strftime('%a %H:%M:%S'), message)
      print(message)
      print(message, file=fout)
  except FileNotFoundError:
    makedirs('.\\logs')
    log('Created log folder')
    log(message)

def parse_score():
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

# Substitute the placeholder with the JSON file for the Google Sheet.
# example: gc = gspread.service_account(filename = r'D:\Users\Hyde\Scrape\client_secret.json')
  
  #edit 09/01/2024: use ./ following by the file name is less pain in the ass to 
  #manage the file path yourself, but it could be more uh.. kind of secure to do it the way that
  #the old maintainer suggested. in case of this code will be publicly visible tho.
  # also this 4 long line of comment can be remove later if you understand what i'm doing here :)
  gc = gspread.service_account(filename = r'./client_secret.json')

  spreadsheet = gc.open("Zenosyne GW")
  try:
    worksheet = spreadsheet.worksheet('GW {} - Day {}'.format(GW_NUM, GW_DAY))
  except Exception:
    log('Sheet not found')
    return
  
  log('Scraping score')
  GBF.get(GW_URL)
  GBF.refresh()
  sleep(5)
  currTime = datetime.now(JP_TZ)
  data = BeautifulSoup(GBF.page_source, 'html.parser')
  guild = 0
  rival = 0

  if RIVAL_URL is None:
    rivalElem = data.find('div', attrs={'class': 'btn-rival-airship'})
    if rivalElem is not None:
      RIVAL_URL = 'http://game.granbluefantasy.jp/#' + rivalElem.get('data-href')

  scores = data.find('div', attrs={'class': 'prt-battle-point'})
  if scores is None:
    log('Score not found')
    return

  guild = int(scores.find('div', attrs={'class': 'txt-guild-point'}).text.strip().replace(',', ''))
  rival = int(scores.find('div', attrs={'class': 'txt-rival-point'}).text.strip().replace(',', ''))
  if worksheet.row_count == 1:
    guildplus = guild
    rivalplus = rival
  else:
    guildplus = guild - int(worksheet.cell(worksheet.row_count, 2).value.strip().replace(',', ''))
    rivalplus = rival - int(worksheet.cell(worksheet.row_count, 5).value.strip().replace(',', ''))
  difference = guild - rival
  worksheet.insert_row([''], index=worksheet.row_count, value_input_option='USER_ENTERED')
  prevRow = worksheet.range(worksheet.row_count, 1, worksheet.row_count, 9)
  newRow = worksheet.range(worksheet.row_count + 1, 1, worksheet.row_count + 1, 9)
  
  rivalATElem = data.find('img', attrs={'class': 'img-rival-assault'})
  rivalAT = False
  rivalATString = 'No'
  if rivalATElem is not None:
    rivalAT = True
    rivalATString = 'Yes'

  GBF.get(RIVAL_URL)
  GBF.refresh()
  sleep(5)
  currTime = datetime.now(JP_TZ)
  data = BeautifulSoup(GBF.page_source, 'html.parser')

  rivalMembersElem = data.find_all('div', attrs={'class': 'prt-status-value'})
  try:
    rivalMembers = int(rivalMembersElem[2].text.strip())
  except:
    rivalMembers = 'N/A'

  GBF.get(CREW_URL)
  GBF.refresh()
  sleep(5)
  currTime = datetime.now(JP_TZ)
  data = BeautifulSoup(GBF.page_source, 'html.parser')

  crewMembersElem = data.find_all('div', attrs={'class': 'prt-status-value'})
  try:
    crewMembers = int(crewMembersElem[2].text.strip())
  except:
    crewMembers = 'N/A'
    
  newValues = [currTime.strftime('%I:%M:00 %p'), guild, guildplus, crewMembers, rival, rivalplus, rivalMembers, difference, rivalATString]
  for i in range (0, 9):
    prevRow[i].value = newRow[i].value.strip().strip(',')
    newRow[i].value = newValues[i]
  worksheet.update_cells(prevRow, value_input_option='USER_ENTERED')
  worksheet.update_cells(newRow, value_input_option='USER_ENTERED')

  if ENABLE_DISCORD:
    embed = discord.Embed(description='```Difference: {:>14}                                                               ```'.format('{:,d}'.format(difference)))
    if rivalAT:
      oppTitle = 'Opponent - STRIKE TIME'
    else:
      oppTitle = 'Opponent'
      
    embed.add_field(name="<:over_dabbing2:814090097628020746>Crew<:over_dabbing:804753374599184404>", value="🎖️`Honors: {:>14}`\n♿`Change: {:>14}`\n<:mutie:814460169810346044>`Active: {:>14}`".format('{:,d}'.format(guild), '{:,d}'.format(guildplus), crewMembers), inline=True)
    embed.add_field(name="💩" + (oppTitle) + "💩", value="🎖️`Honors: {:>14}`\n♿`Change: {:>14}`\n<:mutie:814460169810346044>`Active: {:>14}`".format('{:,d}'.format(rival), '{:,d}'.format(rivalplus), rivalMembers), inline=True)
    embed.set_footer(text=currTime.strftime('%a, %b %d, %Y at %I:%M:00 %p JST') + "\nOpponent:\n" + RIVAL_URL)

    ping = False
    if difference <= PING_THRESHOLD:
      ping = True
    elif difference >= RESET_THRESHOLD:
      HAS_PINGED = False 

    webhook = Webhook.partial(DISCORD_WEBHOOK_ID, DISCORD_WEBHOOK_TOKEN,\
      adapter=RequestsWebhookAdapter())
    if ENABLE_ALERT_PING is True and ping is True and HAS_PINGED is False:
      webhook.send(content='<@&{}> Score difference is less than {:,d}, smash their legs boys <:hyperfaa:804940939427971104>'.format(PING_ROLE_ID, PING_THRESHOLD), embed=embed)
      HAS_PINGED = True
      log('Enable Alert ping is True, Ping is True, has pinged is false')
    else:
      webhook.send(embed=embed)
      log('ping not triggered')

  return

def parse_new_opponent():
  global RIVAL_URL
  global GW_DAY
  global HAS_PINGED
  
  RIVAL_URL = None
  GW_DAY = str(int(GW_DAY) + 1)
  HAS_PINGED = True

def main():
  global GBF
  global GW_NUM
  global GW_DAY
  global GW_URL
  global START_HOUR
  global END_HOUR

  timestart = time_now()
  profile = path.abspath(".\\" + CFG.profile)

  parser = argparse.ArgumentParser(prog='matchup-scraper.py',
    description='A simple script for scraping various parts of Granblue Fantasy',
    usage='matchup-scraper.py [profile] [gw] [finals day] [options]\nexample: python matchup-scraper.py profile2 035 5 -l',
    formatter_class=argparse.MetavarTypeHelpFormatter)

  parser.add_argument('profile', nargs='?',
    help='overwrites the default profile path', type=str)
  parser.add_argument('gw', nargs=2,
    help='scrapes matchup scores based on gw and finals day', type=str)
  parser.add_argument('--login', '-l',
    help='pauses the script upon starting up to allow logging in', action='store_true')
  args = parser.parse_args()

  if len(argv) == 1:
    parser.print_help()
    quit()

#  if args.profile is not None:
#    log('Changing profile path to {}'.format(args.profile))
#    profile = path.abspath('.\\' + args.profile)

  if args.gw is not None and len(args.gw) == 2:
    log('Parsing scores for GW {} day {}'.format(args.gw[0], args.gw[1]))
    GW_NUM = args.gw[0]
    GW_DAY = args.gw[1]
    GW_URL = 'http://game.granbluefantasy.jp/#event/teamraid{}'.format(GW_NUM)
  else:
    parser.print_help()
    quit()

# Substitute the placeholder with a path to whatever Chromium browser you want to use.
# example: browserBIN = r'C:\Program Files\Vivaldi\Application\vivaldi.exe'

  # Configure the thing to point at the right places
  browserBIN = r'C:\Program Files\Google\Chrome\Application\chrome.exe'
  options = webdriver.ChromeOptions()
  options.binary_location = browserBIN
  
  
# Substitute placeholder with the location of a browser profile. I duplicated it so I wouldn't affect the original.
# profiles live in a directory similar to C:\Users\YourName\AppData\Local\Vivaldi\User Data
# example: options.add_argument(r"--user-data-dir=C:\Python\hybri")
# (this was the trickiest edit to get right. you may need to fiddle with this.)

  options.add_argument(r"--user-data-dir=C:\Users\Ben\AppData\Local\Google\Chrome\User Data\Profile 3") # Duplicate Profile
  
  for cargs in CHROME_ARGUMENTS.split():
    options.add_argument(cargs)
  GBF = webdriver.Chrome(options=options)
  GBF.get('http://game.granbluefantasy.jp/#mypage')

  if args.login:
    log('Pausing to login')
    input('Press enter to continue...')

  log('Scheduling tasks')
  listtime=[00,5,10,15,20,25,30,35,40,45,50,55]
  if START_HOUR < END_HOUR:
    for i in range (START_HOUR, END_HOUR):
      for k in listtime:
        schedule.every().day.at("{}:{}".format("{0:02d}".format(i), "{0:02d}".format(k))).do(parse_score)
  elif START_HOUR > END_HOUR:
    for i in range (START_HOUR, 24):
      for k in listtime:
        schedule.every().day.at("{}:{}".format("{0:02d}".format(i), "{0:02d}".format(k))).do(parse_score)
    for i in range (0, END_HOUR):
      for k in listtime:
        schedule.every().day.at("{}:{}".format("{0:02d}".format(i), "{0:02d}".format(k))).do(parse_score)
  else:
    log('Invalid starting and ending hours set')

  if END_HOUR >= 23:
    schedHour = 25 - END_HOUR
    schedule.every().day.at("0{}:30".format(schedHour)).do(parse_new_opponent)
  else:
    schedHour = END_HOUR + 1
    schedule.every().day.at("{}:30".format("{0:02d}".format(schedHour))).do(parse_new_opponent)
  log('Begin scraping')

  while True:
    schedule.run_pending()
    sleep(1)

if __name__ == '__main__':
  CFG = config()

  try:
    main()
  except Exception:
    GBF.close()
    raise
