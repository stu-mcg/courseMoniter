checkInterval = 60

import json
import time
import os
import random

import requests
from bs4 import BeautifulSoup

from twilio.rest import Client
from dotenv import load_dotenv
load_dotenv()
account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
twilio_phone_number = os.environ['TWILIO_PHONE_NUMBER']
alert_phone_number = os.environ['ALERT_PHONE_NUMBER']
client = Client(account_sid, auth_token)

import psycopg2
dbConnection = psycopg2.connect(
	host = "localhost",
	database = "course_moniter",
	user = "postgres",
	port = 5432
)
database = dbConnection.cursor()

def main():
	while(True):
		database.execute("SELECT * FROM courses")
		targets = database.fetchall()
		changes = check(targets) #this take some time
		for change in changes:
			database.execute("UPDATE courses SET status = %s WHERE id = %s", [change['status'], change['id']])
			dbConnection.commit()
		database.execute("UPDATE stats SET value = %s WHERE stat = 'last_check'", [time.time()])
		dbConnection.commit()
		time.sleep(checkInterval + random.randint(0,9))

def sendAlert(message):
	message = client.messages.create(
    	body = message,
        from_ = twilio_phone_number,
        to = alert_phone_number
    )

def check(targets):
	changes = []
	for target in targets:
		id = target[0]
		dept = target[1]
		course = target[2]
		section = target[3]
		campus = target[4]
		oldStatus = target[5]
		newStatus = 'Invalid'
		targetName = dept + " " + course + " " + section
		try:
			url = "https://courses.students.ubc.ca/cs/courseschedule?tname=subj-course&course=" + course + "&campuscd=" + campus + "&dept=" + dept + "&pname=subjarea"
			page = requests.get(url)
		except:
			if(oldStatus != 'Invalid'):
				sendAlert(target['section'] + ' has an invalid url')
			continue
		soup = BeautifulSoup(page.content, 'html.parser')
		table = soup.find('table', {'class': 'table table-striped section-summary'})
		if(not table):
			newStatus = 'Invalid'
			if(oldStatus != 'Invalid'):
				sendAlert(target['section'] + ' has an invalid url')
		else:
			table = table.findAll('tr')[1:]
			names = []
			for row in table:
				name = row.findAll('td')[1].text
				if(name == targetName):
					status = row.findAll('td')[0].text
					if(status.strip() == ''):
						status = 'Available'
						if(oldStatus != 'Available'):
							sendAlert(targetName + ' is available')
					newStatus = status
			if(newStatus == 'Invalid' and oldStatus != 'Invalid'):
				sendAlert(targetName + ' is an invalid section	')
		if(newStatus != oldStatus):
			changes.append({"id" : id, "status" : newStatus})
	return changes

if __name__ == "__main__":
    main()
