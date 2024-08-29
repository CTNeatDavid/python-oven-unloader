#~ from neopixel import *
import sys
import time
import paho.mqtt.client as mqttClient
import RPi.GPIO as gpio
import os
from datetime import datetime
import MySQLdb
import socket
import threading

Connected 					= False
broker_address 				= '192.168.1.100'
port 						= 1883
mqttPass					= 'FGGaLHjaPygGLVBmNt4qcN4aRqyYkz'
mqttUser					= 'CTPROD'

mysqlHost 					= '192.168.1.100'
mysqlDB						= 'CTForn'
mysqlDBAlarm				= 'ProcessControl'
mysqlUser					= 'root'
mysqlPass					= 'ZpZCn*uFoZ.oMbk_xmY3'
mysqlPort					= 3307

machineName					= ""
machineIP					= ""

enableMotorPin 				= 16#
dirMotorPin 				= 21#
pulsePinDerecho 			= 18#
pulsePinIzquierdo 			= 6#
lowerDerMicroPin 			= 23#
lowerIzqMicroPin 			= 14#
upperDerMicroPin			= 15#
sensorINPin1				= 22#
sensorINPin2				= 20#
rackINPin					= 19#
motorInPin					= 13#
SMEMAPin					= 2#
ventiladorPin				= 7
pinSemVerde					= 17#
pinSemRojo					= 12#
pinSemNaran					= 7#
pionSemPito					= 27#

valorBaix 					= False
valorAlt 					= True

pulsosPerRev 				= 400
velocitatOFF				= 700
velocitatON					= 900

Adalt 						= 2
Abaix 						= 1
direccioIndeterminada		= 0
autoDirection 				= direccioIndeterminada
currentDirection 			= direccioIndeterminada

estatElevadorIndeterminat 	= 1
estatElevadorAbaix 			= 2
estatElevadorAdalt			= 3
estatElevadorEnError		= 4
estatElevador 				= estatElevadorIndeterminat

estatCarregadorIndeterminat	= 0
estatCarregadorPle			= 1
estatCarregador				= estatCarregadorIndeterminat

estatPlacaEntrant		 	= 1
estatPlacaDins	 			= 2
estatPlacaIndeterminat		= 3
estatPlaca 					= estatPlacaIndeterminat

estatSemaforON				= 1
estatSemaforOFF				= 0
estatSemaforVerd			= estatSemaforON
estatSemaforTronja			= estatSemaforOFF
estatSemaforVermell			= estatSemaforOFF

estatPitoSemaforOFF			= 0
estatPitoSemaforON			= 1
estatDesitjatPitoSemafor	= estatPitoSemaforOFF
estatPitoSemafor			= estatPitoSemaforOFF

valorAtualIntermitencia		= valorAlt
tiempoIntermitenciaSemaforo = 2

numeroDePosicion			= 0
currentPosition 			= 0
pasPerVolta					= 3
distEntrePisos				= 0
pulsosPerPis				= 0
firstPosition				= 0
pulsosFirstPos 				= 0
lastPosition 				= 0
pulsosLastPosition			= 0
currentConf					= 0
plaquesMarge				= 0
programaSel					= ""
tempsMotorEngegatDespres	= 5
tempMax						= 63
tempMin 					= 45
updateTime					= 5
tempsMinimVentilador		= 60

upperReference				= 1
lowerReference				= 2
indetReference				= 0
referencePos				= indetReference

needToMoveOnePosition		= False
horaPlacaForaDeSensor 		= datetime.now()

resetRequested 				= False
upperResetRequested			= False
lowerResetRequested			= False
autoMode					= True
stopMovement				= False

estatRackIN					= 1
estatRackOUT				= 0
estatRack 					= estatRackOUT
rackDetectatIN				= False
horaRackDetectat			= datetime.now()
tempsMinimRackDetectat		= 5

estatSMEMA_ON				= 1
estatSMEMA_OFF				= 0
estatSMEMA					= estatSMEMA_ON

estatMotorINON				= 1
estatMotorINOFF				= 0
estatMotorIN				= estatMotorINOFF

SMEMAParatPerRack			= False
SMEMAParatPerPosicions		= False

estatVentiladorON			= 1
estatVentiladorOFF			= 0
estatVentilador 			=estatVentiladorOFF

def check_lowerAndUpperMicro_event():
	global estatElevador 
	if estatElevador == estatElevadorIndeterminat:
		return
	if not gpio.input(lowerDerMicroPin) or not gpio.input(lowerIzqMicroPin): 
		if estatElevador != estatElevadorAbaix:
			print ("Lower micro PRESS")
			estatElevador = estatElevadorAbaix
			client.publish('CTForn/estatElevador',estatElevador)
	elif not gpio.input(upperDerMicroPin):
		if estatElevador != estatElevadorAdalt:
			print ("Upper micro PRESS")
			estatElevador = estatElevadorAdalt
			client.publish('CTForn/estatElevador',estatElevador)
	elif estatElevador != estatElevadorIndeterminat:
		if estatElevador == estatElevadorAbaix:
			print ("Lower micro RELEASED")
		else:
			print ("Upper micro RELEASED")
		estatElevador = estatElevadorIndeterminat	
		client.publish('CTForn/estatElevador',estatElevador)

def monitor_events():
    while True:
        check_lowerAndUpperMicro_event()
        time.sleep(0.2)  # Wait for 0.3 seconds

#def sensorIN_event(channel):
#	global estatPlaca 
#	global horaPlacaForaDeSensor
#	global needToMoveOnePosition
#	# ~ print ("Event, gpio state: " + str(gpio.input(sensorINPin)) + " estat placa: " + str(estatPlaca))
#	if gpio.input(sensorINPin) and estatPlaca == estatPlacaEntrant and needToMoveOnePosition == False:
#		time.sleep(0.1)
#		if not gpio.input(sensorINPin):
#			return
#		estatPlaca = estatPlacaDins   		
#		print ("Placa dins del sistema")
#		client.publish('CTForn/estatPlate',estatPlaca)
#		needToMoveOnePosition = True
#		horaPlacaForaDeSensor = datetime.now()
#	elif not gpio.input(sensorINPin) and estatPlaca != estatPlacaEntrant and needToMoveOnePosition == False:
#		time.sleep(0.1)
#		if gpio.input(sensorINPin):
#			return
#		estatPlaca = estatPlacaEntrant
#		print ("Placa entrant al sistema")
#		client.publish('CTForn/estatPlate',estatPlaca)
#	gpio.remove_event_detect(sensorINPin)
#	time.sleep(0.1)
#	gpio.add_event_detect(sensorINPin, gpio.BOTH, callback=sensorIN_event,bouncetime=10)

def gestionIntermitenciaSem():

	if estatPitoSemafor == estatPitoSemaforON:
		gpio.output(pionSemPito, valorAtualIntermitencia)
		gpio.output(pinSemRojo, valorAtualIntermitencia)
		if valorAtualIntermitencia == valorAlt:
			valorAtualIntermitencia = valorBaix
		else:
			valorAtualIntermitencia = valorAlt

def intermitencia_sem():
    while True:
        gestionIntermitenciaSem()
        time.sleep(tiempoIntermitenciaSemaforo) 


def enableDriver(Direcction):

	usleep = lambda x: time.sleep(x/1000000.0)
	gpio.output(enableMotorPin, valorAlt)
	usleep(200)
	if Direcction == 1:		
		gpio.output(dirMotorPin, valorBaix)
	elif Direcction == 2:
		gpio.output(dirMotorPin, valorAlt)
	usleep(200)
	return
	
def disableDriver():

	usleep = lambda x: time.sleep(x/1000000.0)
	gpio.output(enableMotorPin, valorBaix)
	usleep(200)
	gpio.output(dirMotorPin, valorAlt)
	usleep(200)
	return

def sendPulse(pulses, timeBaix, timeAlt):

	global estatSemaforTronja
	global estatElevador
	
	gpio.output(pinSemNaran, False) #se mueve el rack 
	estatSemaforTronja = estatSemaforON

	if estatElevador == estatElevadorAbaix and currentDirection == Abaix:
		return
	elif estatElevador == estatElevadorAdalt and currentDirection == Adalt:
		return
	elif estatElevador == estatElevadorEnError:
		return
	sent = 0
	usleep = lambda x: time.sleep(x/1000000.0)
	client.publish('CTForn/movingElevator',currentDirection)
	while sent<pulses and stopMovement == False and ((estatElevador == estatElevadorAdalt and currentDirection == Abaix) or (estatElevador == estatElevadorAbaix and currentDirection == Adalt) or (estatElevador == estatElevadorIndeterminat)):
		sent=sent+1
		gpio.output(pulsePinDerecho, valorBaix)
		gpio.output(pulsePinIzquierdo, valorBaix)
		usleep(timeBaix)
		gpio.output(pulsePinDerecho, valorAlt)
		gpio.output(pulsePinIzquierdo, valorAlt)
		usleep(timeAlt)
	if stopMovement == True:
		estatElevador = estatElevadorEnError

	gpio.output(pinSemNaran, True) #rack parado
	estatSemaforTronja = estatSemaforOFF
	return

def movementStopped():
	global stopMovement
	stopMovement = False
	client.publish('CTForn/movingElevator',direccioIndeterminada)
	
def changeDirection(newDir):

		global currentDirection
		
		if currentDirection == newDir:
			return
		
		currentDirection = newDir

		if estatElevador == estatElevadorAbaix and currentDirection == Abaix:
			return
		elif estatElevador == estatElevadorAdalt and currentDirection == Adalt:
			return
		elif estatElevador == estatElevadorEnError:
			return
		
		disableDriver()
		enableDriver(newDir)
		
def goToYourPosition():
	if ( estatElevador == estatElevadorEnError):
		return
	print('Going to the current position...')
	if referencePos == upperReference:
		changeDirection(Abaix)
		pulsosToSend = round(pulsosLastPosition + (numeroDePosicion-currentPosition)*pulsosPerPis)
		sendPulse(pulsosToSend,velocitatOFF,velocitatON)
		movementStopped()
	elif referencePos == lowerReference:
		changeDirection(Adalt)
		pulsosToSend = round(pulsosFirstPos + currentPosition*pulsosPerPis)
		sendPulse(pulsosToSend,velocitatOFF,velocitatON)
		movementStopped()
	print('Current position reached!')
		
def goToYourNearestHomeYouAreDrunk():
	global referencePos
	print('Going home...')
	if currentPosition >= (numeroDePosicion/2):
		moveToUpperHome()
		referencePos = upperReference
		print('Upper home reached!')
	else:
		moveToLowerHome()
		referencePos = lowerReference
		print('Lower home reached!')

def moveToUpperHome():
	print('Going up')
	changeDirection(Adalt)
	while estatElevador != estatElevadorAdalt and stopMovement == False and estatElevador != estatElevadorEnError:		
		sendPulse(pulsosPerRev,velocitatOFF,velocitatON)
	movementStopped()

def moveToLowerHome():
	print('Going down')
	changeDirection(Abaix)
	while estatElevador != estatElevadorAbaix and stopMovement == False and estatElevador != estatElevadorEnError:		
		sendPulse(pulsosPerRev,velocitatOFF,velocitatON)
	movementStopped()

def moveOnePosition():
	global currentPosition
	
	print('Moving one position from ' + str(currentPosition))
	
	if autoDirection == Adalt:
		if (currentPosition + 1) <= (numeroDePosicion-1):
			currentPosition = currentPosition +1
		else:
			return
	elif autoDirection == Abaix:
		if (currentPosition - 1) >= (0):
			currentPosition = currentPosition -1
		else:
			return
			
	db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPass, db=mysqlDB, port=mysqlPort)
	cur = db.cursor()
	qry = """UPDATE Configuration SET currentPosition = """  + str(currentPosition) + """ WHERE ID = 1"""
	cur.execute(qry)
	db.commit()
	cur.close()
	db.close ()
	
	print('Current position: ' + str(currentPosition))
	changeDirection(autoDirection)
	sendPulse(round(pulsosPerPis),velocitatOFF,velocitatON)
	movementStopped()

def readConfParam():

	global numeroDePosicion		
	global currentPosition 		
	global pasPerVolta				
	global distEntrePisos			
	global pulsosPerPis			
	global firstPosition			
	global pulsosFirstPos 			
	global lastPosition 			
	global pulsosLastPosition		
	global currentConf				
	global plaquesMarge				
	global programaSel
	global autoDirection
	global tempsMotorEngegatDespres
	global velocitatON
	global velocitatOFF
	global updateTime
	global tempMax
	global tempMin
	global tempsMinimVentilador

	db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPass, db=mysqlDB, port=mysqlPort)
	print('Connected to MySQL')
	cur = db.cursor()
	cur.execute("SELECT * FROM Configuration WHERE ID = 1")
	configurationRecord = cur.fetchone()
	velocitatON = float(configurationRecord[1])
	velocitatOFF = float(configurationRecord[2])
	pulsosPerRev = int(configurationRecord[3])
	numeroDePosicion = int(configurationRecord[4])
	currentPosition = int(configurationRecord[5])
	pasPerVolta = float(configurationRecord[6])
	distEntrePisos = float(configurationRecord[7])
	pulsosPerPis = (distEntrePisos/pasPerVolta)*pulsosPerRev
	firstPosition = float(configurationRecord[8])
	pulsosFirstPos = round((firstPosition/pasPerVolta)*pulsosPerRev)
	lastPosition = float(configurationRecord[9])
	pulsosLastPosition = round((lastPosition/pasPerVolta)*pulsosPerRev)
	autoDirection = int(configurationRecord[10])
	currentConf = configurationRecord[11]
	tempsMotorEngegatDespres = int(configurationRecord[12])
	updateTime = int(configurationRecord[13])
	tempMax = int(configurationRecord[14])
	tempMin = int(configurationRecord[15])
	tempsMinimVentilador = int(configurationRecord[16])
	plaquesMarge = int(configurationRecord[28])

	cur.close()
	# close the connection
	db.close ()
	print("MySQL connection is closed")

	print('Configuration readed:')
	print('VelocitatOFF: ' +  str(velocitatOFF))
	print('VelocitatON: ' + str(velocitatOFF))
	print('PulsosPerRev: ' + str(pulsosPerRev))
	print('NumeroDePosicion: ' + str(numeroDePosicion))
	print('CurrentPosition: ' + str(currentPosition))
	print('PasPerVolta: ' + str(pasPerVolta))
	print('DistEntrePisos: ' + str(distEntrePisos))
	print('PulsosPerPis: ' + str(pulsosPerPis))
	print('FirstPosition: ' + str(firstPosition))
	print('PulsosFirstPos: ' + str(pulsosFirstPos))
	print('LastPosition: ' + str(lastPosition))
	print('PulsosLastPos: ' + str(pulsosLastPosition))
	print('AutoDirection: ' + str(autoDirection))
	print('Temps segons motor engegat: ' + str(tempsMotorEngegatDespres))
	print('Temps update: ' + str(updateTime))
	print('Temp. maxima: ' + str(tempMax))
	print('Temp. minima: ' + str(tempMin))
	print('Temps minim ventilador: ' + str(tempsMinimVentilador))
	print('Plaques de marge: ' + str(plaquesMarge))

def generateAlarm():
	if estatCarregador == estatCarregadorPle:
		client.publish('CTForn/IM_FULL','IM FULL')
	else:
		client.publish('CTForn/IM_ALMOST_FULL','IM ALMOST FULL')
	print('Warning created')

def deleteAlarm():
	
	print('Possible warning deleted')

def addPlateDone():
	
	db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPass, db=mysqlDB, port=mysqlPort)
	cur = db.cursor()
	qry = """UPDATE Configuration SET plaquesTotalsFetes = plaquesTotalsFetes + 1 WHERE ID = 1"""
	cur.execute(qry)
	db.commit()
	cur.close()
	db.close ()
	print('1 plate added to MySQL')
		
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print('Connected to broker')
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print('Connection failed')

def on_message(client, userdata, message):
	global resetRequested
	global autoMode
	global currentPosition
	global upperResetRequested
	global lowerResetRequested
	global stopMovement
	try:
		message.payload = message.payload.decode("utf-8")
		print( 'Message received: ' + message.payload + ' of the topic ' + message.topic)
		if message.payload.find('$') == -1:
			print('client name not found in command')
			return
		randomUIdClient = message.payload[message.payload.find('$')+1:]
		message.payload = message.payload[:message.payload.find('$')]
		print( 'Message from ' + randomUIdClient + ': ' + message.payload)
		if message.topic == 'CTForn/ARE_YOU_HERE':
			print('IM HERE!')
			client.publish('CTForn/IM_HERE/' + randomUIdClient,'IM HERE')
		elif message.topic == 'CTForn/SendPulses': #pulses%direction@speedON|speedOFF
			numberOfPulses = 0
			speedON = 900
			speedOFF = 900
			direction = -1
			if message.payload.find('%') == -1 or message.payload.find('@') == -1 or message.payload.find('|') == -1:
				print('Parameters missing in message')
				client.publish('CTForn/SendPulses/' + randomUIdClient,'ERR') 
			else:
				numberOfPulses = message.payload[:message.payload.find('%')]
				direction = message.payload[message.payload.find('%')+1:message.payload.find('@')]
				speedON = message.payload[message.payload.find('@')+1:message.payload.find('|')]
				speedOFF = message.payload[message.payload.find('|')+1:]
				print('Parameters to send to motor:')
				print('Nof pulses: ' + str(numberOfPulses))
				print('Direction: ' + str(direction) + ' (1-Up, 2-Down)')
				print('SpeedON: ' + str(speedON))
				print('SpeedOFF: ' + str(speedOFF))
				changeDirection(int(direction))
				sendPulse(int(numberOfPulses),float(speedOFF),float(speedON))
				movementStopped()
				client.publish('CTForn/SendPulses/' + randomUIdClient,'DONE')
		elif message.topic == 'CTForn/TurnMotor': #Turns%direction@speedON|speedOFF
			turns = 0
			speedON = 900
			speedOFF = 900
			direction = -1
			if message.payload.find('%') == -1 or message.payload.find('@') == -1 or message.payload.find('|') == -1:
				print('Parameters missing in message')
				client.publish('CTForn/TurnMotor/' + randomUIdClient,'ERR') 
			else:
				#turns = float(message.payload[:message.payload.find('%')])
				#turns = 
				if autoMode == True: #Ha d'estar activat el mode manual
					client.publish('CTForn/TurnMotor/' + randomUIdClient,'ERR')
					return
				direction = int(message.payload[message.payload.find('%')+1:message.payload.find('@')])
				speedON = message.payload[message.payload.find('@')+1:message.payload.find('|')]
				speedOFF = message.payload[message.payload.find('|')+1:]
				print('Parameters to send to motor:')
				print('Nof turns: ' + str(turns))
				print('Direction: ' + str(direction) + ' (1-Up, 2-Down)')
				print('SpeedON: ' + str(speedON))
				print('SpeedOFF: ' + str(speedOFF))
				if direction == Abaix and currentPosition == 0:
					client.publish('CTForn/TurnMotor/' + randomUIdClient,'DONE')
					return
				elif direction == Adalt and currentPosition == numeroDePosicion-1:
					client.publish('CTForn/TurnMotor/' + randomUIdClient,'DONE')
					return
				elif direction == Abaix:
					currentPosition = currentPosition-1
				elif direction == Adalt:
					currentPosition = currentPosition+1

				db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPass, db=mysqlDB, port=mysqlPort)
				cur = db.cursor()
				qry = """UPDATE Configuration SET currentPosition = """  + str(currentPosition) + """ WHERE ID = 1"""
				cur.execute(qry)
				db.commit()
				cur.close()
				db.close ()
				client.publish('CTForn/updateMySQL',estatPlaca)
				print('Current position: ' + str(currentPosition))
				changeDirection(direction)				
				sendPulse(round(pulsosPerPis),float(speedOFF),float(speedON))
				movementStopped()
				# ~ time.sleep(0.01)
				client.publish('CTForn/TurnMotor/' + randomUIdClient,'DONE')
		elif message.topic == 'CTForn/currentElevatorState':
			print('The elevator is in: ' + str(estatElevador))
			client.publish('CTForn/estatElevador/' + randomUIdClient,estatElevador)
		elif message.topic == 'CTForn/currentPlateState':
			print('The plate is in: ' + str(estatPlaca))
			client.publish('CTForn/estatPlate/' + randomUIdClient,estatPlaca)		
		elif message.topic == 'CTForn/currentRackState':
			print('The rack is in: ' + str(estatRack))
			client.publish('CTForn/estatRack/' + randomUIdClient,estatRack)
		elif message.topic == 'CTForn/currentMotorState':
			print('The motor is : ' + str(estatMotorIN))
			client.publish('CTForn/estatMotorIN/' + randomUIdClient,estatMotorIN)
		elif message.topic == 'CTForn/currentSMEMAState':
			print('SMEMA is : ' + str(estatSMEMA))
			client.publish('CTForn/estatSMEMA/' + randomUIdClient,estatSMEMA)
		elif message.topic == 'CTForn/currentFanState':
			print('The fan is : ' + str(estatVentilador))
			client.publish('CTForn/estatVentilador/' + randomUIdClient,estatVentilador)
		elif message.topic == 'CTForn/currentMode':
			if autoMode == True:
				print('The elevator is in auto')
				client.publish('CTForn/estatMode/' + randomUIdClient,"1")
			else:
				print('The elevator is in manual')
				client.publish('CTForn/estatMode/' + randomUIdClient,"0")			
		elif message.topic == 'CTForn/ResetAndGo':
			print('Auto reset requested')
			resetRequested = True
		elif message.topic == 'CTForn/UpperReset':
			print('Upper reset requested')
			upperResetRequested = True
		elif message.topic == 'CTForn/LowerReset':
			print('Lower reset requested')
			lowerResetRequested = True
		elif message.topic == 'CTForn/AutoMode':
			print('Switched to auto mode')
			autoMode = True
		elif message.topic == 'CTForn/ManualMode':
			print('Switched to manual mode')
			autoMode = False
		elif message.topic == 'CTForn/UpdateFromMySQL':
			print('Updating from mySQL')
			readConfParam()
			goToYourNearestHomeYouAreDrunk()
			goToYourPosition()
		elif message.topic == 'CTForn/stopMovement':
			print('Request to stop the movement')
			stopMovement = True
		return
	except Exception as e:
	    print('Exception message: ' + str(e))       

client = mqttClient.Client('Python')               	#create new instance
client.username_pw_set(mqttUser, mqttPass)
client.on_connect = on_connect                      #attach function to callback
client.on_message = on_message



if __name__ == '__main__':


	machineName = socket.gethostname()
	machineIP = ([l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)),s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0])

	print('RASPBERRY_ID: ' + machineName)
	print('RASPBERRY_IP: ' + machineIP)

	gpio.setwarnings(False)
	gpio.setmode(gpio.BCM)
	gpio.setup(enableMotorPin, gpio.OUT)
	gpio.output(enableMotorPin, valorBaix)
	gpio.setup(dirMotorPin, gpio.OUT)
	gpio.output(dirMotorPin, valorAlt)
	gpio.setup(pulsePinDerecho, gpio.OUT)
	gpio.output(pulsePinDerecho, valorAlt)
	gpio.setup(pulsePinIzquierdo, gpio.OUT)
	gpio.output(pulsePinIzquierdo, valorAlt)

	gpio.setup(lowerDerMicroPin, gpio.IN)
	gpio.setup(lowerIzqMicroPin, gpio.IN)
	gpio.setup(upperDerMicroPin, gpio.IN)

	gpio.setup(sensorINPin1, gpio.IN, pull_up_down=gpio.PUD_UP)
	gpio.setup(sensorINPin2, gpio.IN, pull_up_down=gpio.PUD_UP)

	gpio.setup(rackINPin, gpio.IN, pull_up_down=gpio.PUD_UP)

	gpio.setup(motorInPin, gpio.OUT)
	gpio.output(motorInPin, False)

	gpio.setup(SMEMAPin, gpio.OUT)
	gpio.output(SMEMAPin, True)

	gpio.setup(ventiladorPin, gpio.OUT)
	gpio.output(ventiladorPin, False)

	gpio.setup(pinSemVerde, gpio.OUT)
	gpio.output(pinSemVerde, True)
	gpio.setup(pinSemRojo, gpio.OUT)
	gpio.output(pinSemRojo, True)
	gpio.setup(pinSemNaran, gpio.OUT)
	gpio.output(pinSemNaran, True)
	gpio.setup(pionSemPito, gpio.OUT)
	gpio.output(pionSemPito, True)
	
	if gpio.input(lowerDerMicroPin) == 0: 
		estatElevador = estatElevadorAbaix
		print('Elevador abaix!')
	elif gpio.input(upperDerMicroPin) == 0:
		print('Elevador adalt!')
		estatElevador = estatElevadorAdalt

	if not gpio.input(rackINPin):
		estatRack = estatRackIN
		print('Detectat rack IN!')
	else:
		estatRack = estatRackOUT
		print('Detectat rack OUT!')

	client.connect(broker_address, port = port)         #connect to broker
	client.loop_start()        							#start the loop
	while Connected != True:    						#Wait for connection
		time.sleep(0.1)
        

		
	client.subscribe('CTForn/SendPulses')
	client.subscribe('CTForn/TurnMotor')
	client.subscribe('CTForn/ARE_YOU_HERE')
	client.subscribe('CTForn/currentElevatorState')
	client.subscribe('CTForn/currentPlateState')
	client.subscribe('CTForn/currentFanState')
	client.subscribe('CTForn/currentRackState')
	client.subscribe('CTForn/currentMotorState')
	client.subscribe('CTForn/currentSMEMAState')
	client.subscribe('CTForn/ResetAndGo')
	client.subscribe('CTForn/ManualMode')
	client.subscribe('CTForn/AutoMode')
	client.subscribe('CTForn/UpperReset')
	client.subscribe('CTForn/LowerReset')
	client.subscribe('CTForn/UpdateFromMySQL')
	client.subscribe('CTForn/currentMode')
	client.subscribe('CTForn/stopMovement')

	timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

	db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPass, db=mysqlDB, port=mysqlPort)
	cur = db.cursor()
	cur.execute("UPDATE Configuration SET iniciPrograma = '" + timestamp + "' WHERE ID = 1")
	db.commit()
	cur.execute("UPDATE Configuration SET IniciSistema = '" + timestamp + "' WHERE ID = 1")
	db.commit()
	cur.close()
	db.close ()
	
	# Start the monitoring thread
	event_thread = threading.Thread(target=monitor_events)
	event_thread.start()

	# Start the monitoring thread
	event_thread2 = threading.Thread(target=intermitencia_sem)
	event_thread2.start()

	readConfParam()
	goToYourNearestHomeYouAreDrunk()
	goToYourPosition()


	lastUpdated = datetime.now()
	horaOnVentilador = datetime.now()
	while (1):
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- LOOP EVERY updateTime s
		if (datetime.now() - lastUpdated).seconds >= updateTime:
			lastUpdated = datetime.now()
			tFile = open('/sys/class/thermal/thermal_zone0/temp')
			temp = float(tFile.read())
			tempC = int(temp/1000)
			client.publish('CTForn/CPUTemperature',str(tempC))
			print(datetime.now().strftime('%Y-%m-%d %H:%M:%S') + ' T: ' + str(tempC))
			if tempC >= tempMax and estatVentilador == estatVentiladorOFF:
				gpio.output(ventiladorPin, True)
				horaOnVentilador = datetime.now()
				estatVentilador = estatVentiladorON
				client.publish('CTForn/estatVentilador',estatVentilador)
			elif tempC < tempMin and (datetime.now() - horaOnVentilador).seconds >= tempsMinimVentilador and estatVentilador == estatVentiladorON:
				gpio.output(ventiladorPin, False)
				estatVentilador = estatVentiladorOFF
				client.publish('CTForn/estatVentilador',estatVentilador)

			if ((((numeroDePosicion-1)-currentPosition)<=plaquesMarge and autoDirection == Adalt) or (currentPosition<=(plaquesMarge-1) and autoDirection == Abaix)) and autoMode == True:
				print('Current position is near or is in the end!')
				generateAlarm()
				SMEMAParatPerPosicions = True
		#//-------------------------------------------------------------------------------------------------------------------------------------------------------------FI LOOP EVERY 5s

		#//-------------------------------------------------------------------------------------------------------------------------------------------------------------GESTIO SENSOR PLACA
		if gpio.input(sensorINPin1) and estatPlaca == estatPlacaEntrant and autoMode == True:
			time.sleep(0.5)
			if gpio.input(sensorINPin1):
				estatPlaca = estatPlacaDins   		
				print ("Placa dins del sistema")
				client.publish('CTForn/estatPlate',estatPlaca)
				needToMoveOnePosition = True
				horaPlacaForaDeSensor = datetime.now()
		elif not gpio.input(sensorINPin1) and estatPlaca != estatPlacaEntrant and autoMode == True:
			time.sleep(0.5)
			if not gpio.input(sensorINPin1):
				estatPlaca = estatPlacaEntrant
				print ("Placa entrant al sistema")
				client.publish('CTForn/estatPlate',estatPlaca)
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- FI GESTIO SENSOR PLACA	
		
		#//-------------------------------------------------------------------------------------------------------------------------------------------------------------GESTIO SENSOR RACK
		if not gpio.input(rackINPin) and estatRack!= estatRackIN and rackDetectatIN == False:
			print('Detectat rack IN!')	
			client.publish('CTForn/estatRack',estatRackIN)		
			rackDetectatIN = True
			horaRackDetectat = datetime.now()
			SMEMAParatPerRack = False
		elif gpio.input(rackINPin) and estatRack != estatRackOUT:
			print('Detectat rack OUT!')
			client.publish('CTForn/estatRack',estatRackOUT)
			rackDetectatIN = False
			estatRack = estatRackOUT
			SMEMAParatPerRack = True

		if rackDetectatIN and (datetime.now() - horaRackDetectat).seconds >= tempsMinimRackDetectat:		
			estatRack = estatRackIN
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- FI GESTIO SENSOR RACK	

		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- GESTIO MOVE ONE POSITION AUTO	
		if needToMoveOnePosition and (datetime.now() - horaPlacaForaDeSensor).seconds >= tempsMotorEngegatDespres and autoMode == True and estatRack == estatRackIN:
			gpio.output(motorInPin, False)
			estatMotorIN = estatMotorINOFF
			client.publish('CTForn/estatMotorIN',estatMotorIN)
			needToMoveOnePosition = False
			moveOnePosition()
			estatPlaca = estatPlacaIndeterminat
			client.publish('CTForn/estatPlate',estatPlaca)
			addPlateDone()
			client.publish('CTForn/updateMySQL',estatPlaca)
			if (currentPosition == (numeroDePosicion-1) and autoDirection == Adalt) or (currentPosition == 0 and autoDirection == Abaix):
				SMEMAParatPerPosicions = True
				print('Carregador ple!')
				estatCarregador = estatCarregadorPle
				generateAlarm()		
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- FI GESTIO MOVE ONE POSITION AUTO
		
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- GESTIO MOTOR ENTRADA
		if estatPlaca == estatPlacaEntrant and estatCarregador != estatCarregadorPle and autoMode== True and estatRack == estatRackIN and estatMotorIN != estatMotorINON:
			print('Starting motor')
			gpio.output(motorInPin, True)
			estatMotorIN = estatMotorINON
			client.publish('CTForn/estatMotorIN',estatMotorIN)			
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- FI GESTIO MOVE ONE POSITION AUTO
		
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- GESTIO SMEMA	
		if (SMEMAParatPerPosicions or SMEMAParatPerRack) and estatSMEMA == estatSMEMA_ON:
			estatSMEMA = estatSMEMA_OFF
			gpio.output(SMEMAPin, False)
			client.publish('CTForn/estatSMEMA',estatSMEMA)
			print('SMEMA OFF!')
		elif estatSMEMA == estatSMEMA_OFF and not (SMEMAParatPerPosicions or SMEMAParatPerRack):
			estatSMEMA = estatSMEMA_ON
			gpio.output(SMEMAPin, True)
			client.publish('CTForn/estatSMEMA',estatSMEMA)
			print('SMEMA ON!')
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- FI GESTIO SMEMA
		
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- GESTIO DE RESETS
		if (resetRequested or upperResetRequested or lowerResetRequested) and estatPlaca != estatPlacaEntrant:

			estatElevador = estatElevadorIndeterminat
			if gpio.input(lowerDerMicroPin) == 0: 
				estatElevador = estatElevadorAbaix
				print('Elevador abaix!')
			elif gpio.input(upperDerMicroPin) == 0:
				print('Elevador adalt!')
				estatElevador = estatElevadorAdalt

			deleteAlarm()

			if resetRequested:
				goToYourNearestHomeYouAreDrunk()
				if currentPosition >= (numeroDePosicion/2):
					currentPosition = numeroDePosicion-1
					autoDirection = Abaix
				else: 
					currentPosition = 0
					autoDirection = Adalt
			elif upperResetRequested:
				moveToUpperHome()
				referencePos = upperReference
				print('Upper home reached!')
				currentPosition = numeroDePosicion-1
				autoDirection = Abaix
			elif lowerResetRequested:
				moveToLowerHome()
				referencePos = lowerReference
				print('Lower home reached!')
				currentPosition = 0
				autoDirection = Adalt

			resetRequested = False
			upperResetRequested = False
			lowerResetRequested = False	
			SMEMAParatPerPosicions = False		

			goToYourPosition()

			db = MySQLdb.connect(host=mysqlHost, user=mysqlUser, passwd=mysqlPass, db=mysqlDB, port=mysqlPort)
			cur = db.cursor()
			qry = "UPDATE Configuration SET autoDirection = "  + str(autoDirection) + " WHERE ID = 1"
			cur.execute(qry)
			db.commit()
			qry = "UPDATE Configuration SET currentPosition = "  + str(currentPosition) + " WHERE ID = 1"
			cur.execute(qry)
			db.commit()
			cur.close()
			db.close ()
			client.publish('CTForn/updateMySQL',estatPlaca)
			print('Reset done!')
		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- FI GESTIO RESETS		

		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- GESTIO SEMAFOR

		if (estatPlaca == estatPlacaEntrant):#//situaciones de semaforo en narnaja 
			estatSemaforTronja = estatSemaforON
		else:
			if estatSemaforTronja == estatSemaforON:#lo apagamos
				gpio.output(pinSemNaran, True)
				estatSemaforTronja = estatSemaforOFF

		if (estatSMEMA == estatSMEMA_OFF or estatElevador == estatElevadorEnError):#//situaciones de semaforo en rojo
			estatSemaforVermell = estatSemaforON 
		else:
			if estatSemaforVermell == estatSemaforON:#lo apagamos
				gpio.output(pinSemRojo, True)
				estatSemaforVermell = estatSemaforOFF

		if (estatSemaforVermell == estatSemaforON):#// El pito se enciende con el semaforo rojo
			estatPitoSemafor = estatPitoSemaforON
		else:
			if estatPitoSemafor == estatPitoSemaforON:#lo apagamos
				gpio.output(pionSemPito, True)
				estatPitoSemafor = estatPitoSemaforOFF

		if (estatSemaforTronja == estatSemaforON or estatSemaforVermell == estatSemaforON): #// si no hay ningun semaforo se enciende el verde
			#apagamos el led verde
			if estatSemaforVerd == estatPitoSemaforON:
				gpio.output(pinSemVerde, True)
				estatSemaforVerd = estatSemaforOFF
		else:
			if estatSemaforVerd == estatSemaforOFF:
				gpio.output(pinSemVerde, False)
				estatSemaforVerd = estatSemaforON
			

		#//------------------------------------------------------------------------------------------------------------------------------------------------------------- FI GESTIO SEMAFOR	
		time.sleep(0.4)

