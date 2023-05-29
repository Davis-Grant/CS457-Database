# Grant Davis, CS 457, PA4, Fall 21
# Python 3.7+ required.

# Main driver file

import os
import sys

import db
import table
import query
import join

workingDB = None
UserQuery = ""
TableList = [None]
CommandsToExecuteOnCommit = []
BreakFlag = 0
isLocked = 1
userMadeLock = 0

def commandProcessing():
  global workingDB
  global userMadeLock
  global isLocked
  #global CommandsToExecuteOnCommit

  if (';' not in UserQuery and UserQuery.upper() != ".EXIT"): # Invalid command
    print("Commands must end with ';'")
  
  # Creates database
  elif ("CREATE DATABASE" in UserQuery.upper()):
    dbName = db.inputCleaner("CREATE DATABASE ", UserQuery)
    if db.databaseExistenceCheck(dbName) == 0:
      os.system(f'mkdir {dbName}')
      print(f"Created database {dbName}.")
    else:
      print(f"Could not create database {dbName} because it already exists.")
  
  # Deletes database
  elif ("DROP DATABASE" in UserQuery.upper()):
    dbName = db.inputCleaner("DROP DATABASE ", UserQuery)
    if db.databaseExistenceCheck(dbName):
      os.system(f'rm -r {dbName}')
      print(f"Removed database {dbName}.")
    else:
      print(f"Could not remove database {dbName} because it does not exist.")
  
  # Sets currently active database
  elif ("USE" in UserQuery.upper()):
    workingDB = db.inputCleaner("USE ", UserQuery)
    #os.system('cd ' + workingDB)
    if db.databaseExistenceCheck(workingDB):
      print(f"Using database {workingDB}.")
    else:
      print(f"Could not use database {workingDB} because it does not exist.")

  # Creates a table with specified name and attributes
  elif ("CREATE TABLE" in UserQuery.upper()):
    # Splits input into separate strings
    tInput = db.inputCleaner("CREATE TABLE ", UserQuery).replace("create table ", "")
    tName = tInput.split()[0] # Grabs table name
    tRest = tInput.replace(tName, "")
    tAttrs0 = tRest[2:] # Leaves only string with attributes
    tAttrs1 = tAttrs0[:-1] # See above
    tAttrs = tAttrs1.split(",") # Creates list from attributes

    if (workingDB != None):
      if db.tableExistenceCheck(tName, workingDB) == 0:
        os.system(f'touch {workingDB}/{tName}.txt')
        filename = workingDB + '/' + tName + '.txt'
        f = open(filename, 'w')
        f.write(" |".join(tAttrs)) # Writes list to file with pipe delimiter
        f.close()
        print(f"Created table {tName}.")
      else:
        print(f"Could not create table {tName} because it already exists.")
    else:
      print("Please specify which database to use.")

  # Deletes table
  elif ("DROP TABLE" in UserQuery.upper()):
    tName = db.inputCleaner("DROP TABLE ", UserQuery)
    if (workingDB != None):
      if db.tableExistenceCheck(tName, workingDB):
        if isLocked == 0:
          if userMadeLock:
            CommandsToExecuteOnCommit.append(f'rm {workingDB}/{tName}.txt')
          else:
            os.system(f'rm {workingDB}/{tName}.txt')
          print(f"Removed table {tName} from database {workingDB}.")
        else:
          print(f"Table {tName} is locked!")
      else:
        print(f"Could not remove table {tName} because it does not exist.")
    else:
      print("Please specify which database to use.")
  
  # Returns table elements as specified
  elif ("SELECT" in UserQuery.upper()):
    if ("SELECT *" in UserQuery.upper()):
      if ("." in UserQuery.upper()):
        join.joinTableOpener(UserQuery, workingDB)
      else:
        query.queryAll(UserQuery, workingDB)
    else:
      query.querySpecific(UserQuery, workingDB)

  # Modifies table by adding attribute
  elif ("ALTER TABLE" in UserQuery.upper()):
    alter = db.inputCleaner("ALTER TABLE ", UserQuery)
    tName = alter.split()[0] # Grabs table name
    alterCmd = alter.split()[1] # Grabs command (ADD, etc)
    alterRest1 = alter.replace(tName, "")
    alterRest2 = alterRest1.replace(alterCmd, "") # Left with attributes, currently only supports one
    newAttr = alterRest2[2:] # May have issue with leading parentheses

    if workingDB != None:
      if db.tableExistenceCheck(tName, workingDB):
        if isLocked == 0:
          f = open(f'{workingDB}/{tName}.txt', 'a')
          f.write(f" | {newAttr}") # Appends attribute to file with pipe delimiter
          f.close()
          print(f"Modified table {tName}.")
        else:
          print(f"Table {tName} is locked!")
      else:
        print(f"Could not modify table {tName} because it does not exist.")
    else:
      print("Please specify which database to use.")
  
  elif ("INSERT INTO" in UserQuery.upper()):
    table.insertTuple(UserQuery, workingDB, isLocked, userMadeLock, CommandsToExecuteOnCommit)
  
  elif ("UPDATE" in UserQuery.upper()):
    table.updateTuple(UserQuery, workingDB, isLocked, userMadeLock, CommandsToExecuteOnCommit)
  
  elif ("DELETE FROM" in UserQuery.upper()):
    table.deleteTuple(UserQuery, workingDB, isLocked, userMadeLock, CommandsToExecuteOnCommit)
  
  elif ("BEGIN TRANSACTION" in UserQuery.upper()):
    userMadeLock = db.makeLock(workingDB)
    print("Transaction start.")
  
  elif ("COMMIT" in UserQuery.upper()):
    if userMadeLock:
      db.releaseLock(workingDB, CommandsToExecuteOnCommit)
      print("Transaction committed.")
    else:
      print("Transaction aborted.")
    userMadeLock = 0

  # Testing purposes, deletes databases to start fresh
  elif ("DEL" in UserQuery):
    os.system('rm -r CS457_PA4')
  
  elif (".EXIT" != UserQuery.upper()):
    print("I don't know what you want me to do.")

try:
  inputFile = open(sys.argv[1])
  for cmd in inputFile:
    if (BreakFlag == 1):
      inputFile.close()
      quit()
    elif ("--" not in cmd):
      if (".EXIT" not in cmd.upper()):
        if userMadeLock == 0:
          isLocked = db.checkLock(workingDB) if (workingDB != None) else 1
        UserQuery = cmd.rstrip('\n')
        commandProcessing()
      else:
        BreakFlag = 1
except IndexError:
  while (UserQuery.upper() != ".EXIT"):
    if userMadeLock == 0:
      isLocked = db.checkLock(workingDB) if (workingDB != None) else 1
    UserQuery = input("grantQL> ")
    commandProcessing()

quit()
