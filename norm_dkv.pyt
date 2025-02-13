# -*- coding: utf-8 -*-

import arcpy
import math
import sys
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Normalization and categorization of data into three categories"
        self.alias = "NORM_CAT"

        # List of tool classes associated with this toolbox
        # In this case, it includes Tool1 (the tool we're defining)
        self.tools = [Tool1]


class Tool1(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalization & Categorization"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
        
        # Input Layer or Table (either a Feature Layer, Table, or Shapefile)
        # This allows the user to input a Feature Layer, Table, or Shapefile
        param0 = arcpy.Parameter(
            displayName="Input Layer or Table",
            name="input_layer",
            datatype=["GPFeatureLayer"],  # Allowing feature layer, table, or shapefile
            parameterType="Required",
            direction="Input"
        )
        
        # Output Layer or Table (Feature Layer, Table, or Shapefile)
        # This defines where the output data will be stored (Feature Layer, Table, or Shapefile)
        param1 = arcpy.Parameter(
            displayName="Output Layer or Table",
            name="out_features",
            datatype=["GPFeatureLayer"],  # Allowing feature layer, table, or shapefile
            parameterType="Required",
            direction="Output"
        )

        # Name of the column/field with information about the gridcell ID
        # This parameter will allow the user to specify the column to be normalized
        param2 = arcpy.Parameter(
            displayName="Column",
            name="column",
            datatype="Field",  # This specifies the field name, which is required
            parameterType="Required",
            direction="Input"
        )

        # Define dependencies and schemas if necessary
        param1.parameterDependencies = [param0.name]  # Output depends on Input
        param1.schema.clone = True  # Cloning schema to ensure output matches input format



        # Return the parameter list (required by the toolbox)
        params = [param0, param1, param2]

        # Set the filter to accept only fields that are Short or Long type
        params[2].filter.list = ['Short', 'Long', 'Float', 'Double']
        params[2].parameterDependencies = [params[0].name]
                
        return params
    
    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):

        return


    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool.""" 
        
        # get text value of parameters (input/output layer, and the column name)
        INPUT_LAYER = parameters[0].valueAsText  # Get the input layer (path to the layer)
        OUTPUT_LAYER = parameters[1].valueAsText  # Get the output layer (path to save output)
        COLUMN = parameters[2].valueAsText  # Get the column name for normalization
        
        # Define datatype for fields to be added in the output (normalization and categorization fields)
        FIELD_TYPE_NORM = "DOUBLE"  # 'NORMAL' field will be of type DOUBLE
        FIELD_TYPE_CAT = "INTEGER"  # 'CATS' field will be of type INTEGER
        
        # Create a copy of the input layer to preserve original data
        input_layer_copy = arcpy.Copy_management(
            INPUT_LAYER, 
            OUTPUT_LAYER)  # This is where we copy the input layer to the output path
        
        # Add a field called 'NORMAL' in the copied layer for normalization calculation
        arcpy.management.AddField(
            input_layer_copy, 
            "NORMAL", 
            FIELD_TYPE_NORM)  # 'NORMAL' field will store normalized values (float/double)
        
        # Add a field called 'CATS' in the copied layer for categorization calculation
        arcpy.management.AddField(
            input_layer_copy, 
            "CATS", 
            FIELD_TYPE_CAT)  # 'CATS' field will store the categories (integer)
        
        # Initialize variables for min and max values for normalization
        min_value = float('inf')
        max_value = float('-inf')

        # Use a SearchCursor to find the minimum and maximum values of the specified column
        with arcpy.da.SearchCursor(OUTPUT_LAYER, [COLUMN]) as cursor:
            for row in cursor:
                value = row[0]  # Get the value of the current row's specified column
                if value < min_value:
                    min_value = value  # Update the min value
                if value > max_value:
                    max_value = value  # Update the max value
        
        # Define the expression for normalization
        # This formula normalizes the values between 1 and 2 based on the min/max values
        expression = "(!{}! - {}) / ({}) + 1".format(COLUMN, min_value, max_value - min_value)

        # Run CalculateField to populate the 'NORMAL' field with the normalized values
        arcpy.management.CalculateField(
            OUTPUT_LAYER,
            "NORMAL",
            expression,
            expression_type="PYTHON3"  # Use Python 3 syntax for calculation
        )

        # Define the expression for categorizing the normalized values into 3 categories
        # The 'NORMAL' values will be divided into 3 categories based on predefined ranges
        categorization_expression = (
            "1 if (float(!NORMAL!) >= 1 and float(!NORMAL!) <= 1.33) else " +
            "2 if (float(!NORMAL!) > 1.33 and float(!NORMAL!) <= 1.66) else " +
            "3 if (float(!NORMAL!) > 1.66 and float(!NORMAL!) <= 2) else None"
        )

        # Run CalculateField to populate the 'CATS' field with the category numbers
        arcpy.management.CalculateField(
            OUTPUT_LAYER,
            "CATS",
            categorization_expression,
            expression_type="PYTHON3"  # Use Python 3 syntax for calculation
        )

        return