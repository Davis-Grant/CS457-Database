# Grant Davis, CS 457, PA4, Fall 21
# Python 3.7+ required.

# Utility file for table joins

import db
import os

def joinTableOpener(UserQuery, workingDB):
  joinType = 0
  exitFlag=0
  if ('LEFT OUTER JOIN' in UserQuery.upper()):
    joinType = 1
  
  # Removing unnecessary words from command
  selLower = db.inputCleaner("SELECT * FROM ", UserQuery)
  selection = db.inputCleaner("select * from ", selLower)
  selection = selection.replace("inner join", "").replace("left outer join", "")
  commandWords = selection.replace(",","").split()

  # Grabbing values from commands
  table1Name = commandWords[0]
  table2Name = commandWords[2]
  comparisonOperator = db.getOperand(commandWords[6])

  # Importing tables into lists
  Table_1 = []
  Table_2 = []
  Table_Join = []
  TableListNames = [Table_1, Table_2]
  ActualTableNames = [table1Name, table2Name]
  if workingDB != None:
    for x in range(0,2):
      if db.tableExistenceCheck(ActualTableNames[x], workingDB):
        f = open(f'{workingDB}/{ActualTableNames[x]}.txt', 'r')
        for line in f:
          TableListNames[x].append(line) #Turning tables into list of lines
        f.close()
      else:
        print(f"Could not query table {ActualTableNames[x]} because it does not exist.")
        exitFlag=1
  else:
    print("Please specify which database to use.")
  
  if (exitFlag==0):

    # Finding the index of columns to search
    table1Column = Table_1[0].index(commandWords[5].split(".")[1])
    table2Column = Table_2[0].index(commandWords[7].split(".")[1])

    # Performs comparisons on given data
    def joinOperandFunction(t1, t2):
      if (comparisonOperator == 0): #Equality
        if (type(Table_2[t2].split("|")[table2Column]) is str):
          if (Table_2[t2].split("|")[table2Column] == Table_1[t1].split("|")[table1Column]):
            Table_Join.append(f'{Table_1[t1]} | {Table_2[t2]}')
        else:
          if (float(Table_2[t2].split("|")[table2Column]) == float(Table_1[t1].split("|")[table1Column])):
            Table_Join.append(f'{Table_1[t1]} | {Table_2[t2]}')
      elif (comparisonOperator == 1): #Greater than
        if (Table_2[t2].split("|")[table2Column] > Table_1[t1].split("|")[table1Column]):
          Table_Join.append(f'{Table_1[t1]} | {Table_2[t2]}')
      elif (comparisonOperator == -1): #Less than
        if (Table_2[t2].split("|")[table2Column] < Table_1[t1].split("|")[table1Column]):
          Table_Join.append(f'{Table_1[t1]} | {Table_2[t2]}')
      elif (comparisonOperator == -3): #Inequality
        if (Table_2[t2].split("|")[table2Column] != Table_1[t1].split("|")[table1Column]):
          Table_Join.append(f'{Table_1[t1]} | {Table_2[t2]}')

    # Join function. Nested for loops to iterate through tables.
    def join():
      Table_1[0] = Table_1[0].rstrip('\n')
      Table_2[0] = Table_2[0].rstrip('\n')
      Table_Join.append(f"{Table_1[0]} | {Table_2[0]}")
      for t1 in range(1, len(Table_1)):
        Table_1[t1] = Table_1[t1].rstrip("\n")
        for t2 in range(1, len(Table_2)):
          Table_2[t2] = Table_2[t2].rstrip('\n')
          joinOperandFunction(t1, t2)
        # Left outer join. If program cannot find Table 1 value in the joined Table, we add it with null info for Table 2's values.
        if (joinType == 1):
          if (Table_1[t1].split("|")[table1Column] not in Table_Join[-1].split("|")[table1Column]):
            Table_Join.append(f"{Table_1[t1]} | |")
      for myTuple in Table_Join:
        print(myTuple)
    
    join()
