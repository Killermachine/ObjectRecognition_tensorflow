import smtplib
from email.MIMEMultipart import MIMEMultipart
from email.MIMEText import MIMEText
from email.MIMEBase import MIMEBase
from email import encoders


#sender and receiver email ids
def sendResults(results):
	fromaddr = 'ashok05@somaiya.edu'
	toaddr = 'tanay.v@somaiya.edu'

	#MIMEMultipart helps add subject to the mail along with plain body
	msg = MIMEMultipart()
	msg['From'] = fromaddr
	msg['To'] = toaddr
	msg['Subject'] = str(results)

	#fetching a quote from Goodreads


	body = str(results)

	msg.attach(MIMEText(body.encode('utf-8'),'plain'))

	server = smtplib.SMTP('smtp.gmail.com', 587)
	server.starttls()
	server.login(fromaddr,"Drakeash133@somaiya")

	text = msg.as_string()
	server.sendmail(fromaddr,toaddr,text)
	server.quit()