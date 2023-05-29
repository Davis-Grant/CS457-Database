# Grant Davis, CS 457, PA3, Fall 21
# Python 3.7+ required.

# Utility file for table queries

import os
import db

# Select *
def queryAll(UserQuery, workingDB):
  selLower = db.inputCleaner("SELECT * FROM ", UserQuery)
  selection = db.inputCleaner("select * from ", selLower)
  if workingDB != None:
    if db.tableExistenceCheck(selection, workingDB):
      f = open(f'{workingDB}/{selection}.txt', 'r')
      print(f.read())
      f.close()
    else:
      print(f"Could not query table {selection} because it does not exist.")
  else:
    print("Please specify which database to use.")

# Select (with variables)
def querySpecific(UserQuery, workingDB):
  selLower = db.inputCleaner("SELECT ", UserQuery)
  selection = db.inputCleaner("select ", selLower)

  # Gathering list of variables
  selectColumns = selection.replace(",", "").split()
  selectColumns = selectColumns[:selectColumns.index("from")]

  # Table name
  tName = selection.split()[len(selectColumns)+1]

  # Gathering what to filter by
  whereColumn = selection.split()[len(selectColumns)+3]
  whereRecord = selection.split()[len(selectColumns)+5]
  operand = db.getOperand(selection.split()[len(selectColumns)+4])

  if workingDB != None:
    if db.tableExistenceCheck(tName, workingDB):
      f = open(f'{workingDB}/{tName}.txt', 'r')
      tempFile = f.readlines()
      f.close()

      selectColumnNums = []
      columnNameString = ""
      listToReturn = []
      count = 0
      for line in tempFile:
        if (count == 0): # Headers
          # Finding the indexes of select and where columns
          columnList = line.split()
          columnListWithTypes = columnList.copy()
          del columnListWithTypes[2::3]

          del columnList[1::3]
          columnCount = 0

          # If variable is found in table, record its index
          for word in columnList:
            if word in selectColumns:
              selectColumnNums.append(columnCount)
            if (word == whereColumn):
              whereColumnNum = columnCount
            columnCount += 1

          # Creating a custom table header for the selected columns
          for index in selectColumnNums:
            columnNameString += f"{columnListWithTypes[index]} {columnListWithTypes[index+1]} | "
          queryHeader = columnNameString[:-3]
          listToReturn.append(queryHeader)

        if (count > 0): # Values
          tupleDetails = line.split()

          # Determines what to do with each row
          def querySpecificHelper():

            # Creates the row output
            def queryStringMaker():
              queryString = ""
              for index in selectColumnNums:
                queryString += f"{tupleDetails[index]} | "
              queryResult = queryString[:-3]
              listToReturn.append(queryResult)

            if (operand == 0): # Equality
              # The type checking here handles strings and numbers separately
              # Ex. 150 or 150.00 would not find 150.00 or 150, respectively
              if (type(tupleDetails[whereColumnNum]) is str):
                if (tupleDetails[whereColumnNum] == whereRecord):
                  queryStringMaker()
              elif (type(tupleDetails[whereColumnNum]) is not str):
                if (float(tupleDetails[whereColumnNum]) == float(whereRecord)):
                  queryStringMaker()

            elif (operand == 1): # Greater than
              if (float(tupleDetails[whereColumnNum]) > float(whereRecord)):
                queryStringMaker()

            elif (operand == -1): # Less than
              if (float(tupleDetails[whereColumnNum]) < float(whereRecord)):
                queryStringMaker()

            elif (operand == -3): # Inequality
              if (type(tupleDetails[whereColumnNum]) is str):
                if (tupleDetails[whereColumnNum] != whereRecord):
                  queryStringMaker()
              elif (type(tupleDetails[whereColumnNum]) is not str):
                if (float(tupleDetails[whereColumnNum]) != float(whereRecord)):
                  queryStringMaker()

          querySpecificHelper()

        count += 1
      for line in listToReturn: # Prints table
        print(line)

    else:
      print(f"Could not query table {tName} because it does not exist.")
  else:
    print("Please specify which database to use.")
