# Grant Davis, CS 6457, PA4, Fall 21
# Python 3.7+ required.

# Utility file for input sanitizing, existence checks

import os
import shlex
import subprocess

def inputCleaner(wordToRemove, UserQuery): # Removes ; and command
  query = UserQuery.replace(";", "")
  return query.replace(wordToRemove, "")

def databaseExistenceCheck(db): # Checks if database exists
  if db in subprocess.run(['ls', '|', 'grep', db], capture_output=True, text=True).stdout:
    return 1
  else:
    return 0

def tableExistenceCheck(t, workingDB): # Checks if table exists
  if t in subprocess.run(['ls', workingDB,  '|', 'grep', t], capture_output=True, text=True).stdout:
    return 1
  else:
    return 0

# Determines operand and assigns value
def getOperand(o):
  operand = None
  if (o == '='):
    operand = 0
  elif (o == '<'):
    operand = -1
  elif (o == '>'):
    operand = 1
  elif (o == '!='):
    operand = -3
  return operand

# Creates a lock if one does not exist already
def makeLock(workingDB):
  if checkLock(workingDB):
    return 0
  else:
    tablesToLock = subprocess.run(['ls', workingDB, '|', 'grep ".txt"'], capture_output=True, text=True).stdout.split()
    tablesToLock.pop(0)
    for name in tablesToLock:
      os.system(f"touch {workingDB}/{name}.lock")
    return 1

def checkLock(workingDB):
  if ".lock" in subprocess.run(['ls', workingDB, '|', 'grep ".lock"'], capture_output=True, text=True).stdout:
    #print("Locks found!")
    return 1
  else:
    return 0

def releaseLock(workingDB, c):
  for cmd in c:
    os.system(cmd)
  os.system(f"rm {workingDB}/*.lock")
  #print("Locks removed!")
