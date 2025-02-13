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
        self.tools = [fc, shp, table]


def normalize_and_categorize(self, input_layer, output_layer, column):
        """Shared function for normalizing and categorizing."""
        # Add common logic here
        FIELD_TYPE_NORM = "DOUBLE"  # 'NORMAL' field will be of type DOUBLE
        FIELD_TYPE_CAT = "INTEGER"  # 'CATS' field will be of type INTEGER
        
        # Create a copy of the input layer to preserve original data
        input_layer_copy = arcpy.Copy_management(input_layer, output_layer)
        
        # Add a field called 'NORMAL' in the copied layer for normalization calculation
        arcpy.management.AddField(input_layer_copy, "NORMAL", FIELD_TYPE_NORM)
        
        # Add a field called 'CATS' in the copied layer for categorization calculation
        arcpy.management.AddField(input_layer_copy, "CATS", FIELD_TYPE_CAT)
        
        # Initialize variables for min and max values for normalization
        min_value = float('inf')
        max_value = float('-inf')

        # Use a SearchCursor to find the minimum and maximum values of the specified column
        with arcpy.da.SearchCursor(output_layer, [column]) as cursor:
            for row in cursor:
                value = row[0]  # Get the value of the current row's specified column
                if value < min_value:
                    min_value = value  # Update the min value
                if value > max_value:
                    max_value = value  # Update the max value
        
        # Define the expression for normalization
        expression = "(!{}! - {}) / ({}) + 1".format(column, min_value, max_value - min_value)

        # Run CalculateField to populate the 'NORMAL' field with the normalized values
        arcpy.management.CalculateField(output_layer, "NORMAL", expression, expression_type="PYTHON3")

        # Define the expression for categorizing the normalized values into 3 categories
        categorization_expression = (
            "1 if (float(!NORMAL!) >= 1 and float(!NORMAL!) <= 1.33) else " +
            "2 if (float(!NORMAL!) > 1.33 and float(!NORMAL!) <= 1.66) else " +
            "3 if (float(!NORMAL!) > 1.66 and float(!NORMAL!) <= 2) else None"
        )

        # Run CalculateField to populate the 'CATS' field with the category numbers
        arcpy.management.CalculateField(output_layer, "CATS", categorization_expression, expression_type="PYTHON3")


def get_parameter_info(input_datatype, output_datatype, column_datatype):
    """Shared function for getting parameter definitions with customizable data types."""
    param0 = arcpy.Parameter(
        displayName="Input Layer or Table",
        name="input_layer",
        datatype=input_datatype,  # This will allow different input data types
        parameterType="Required",
        direction="Input"
    )
    
    param1 = arcpy.Parameter(
        displayName="Output Layer or Table",
        name="out_features",
        datatype=output_datatype,  # This will allow different output data types
        parameterType="Required",
        direction="Output"
    )

    param2 = arcpy.Parameter(
        displayName="Column",
        name="column",
        datatype=column_datatype,  # This will allow different column data types
        parameterType="Required",
        direction="Input"
    )

    param1.parameterDependencies = [param0.name]
    param1.schema.clone = True

    params = [param0, param1, param2]
     # Set the filter to accept only fields that are Short or Long type
    params[2].filter.list = ['Short', 'Long', 'Float', 'Double']
    params[2].parameterDependencies = [params[0].name]
    
    return params

class fc(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalize into Categories (Feature Class to GDB)"
        self.description = "Normalize and categorize Feature Class layers and save them to File GeoDatabase"
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Pass custom data types for this class
        return get_parameter_info(
            input_datatype=["GPFeatureLayer"],  # Feature Layer for input
            output_datatype=["GPFeatureLayer"],  # Feature Layer for output
            column_datatype="Field"  # Field for column
        )
            
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
        normalize_and_categorize(self,
            parameters[0].valueAsText, 
            parameters[1].valueAsText, 
            parameters[2].valueAsText
        )

        return
    

class shp(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalize into Categories (SHP to SHP)"
        self.description = "Normalize and categorize ShapeFile files and save them to folder"
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Pass custom data types for this class
        return get_parameter_info(
            input_datatype=["DEShapeFile"],  # Feature Layer for input
            output_datatype=["DEShapeFile"],  # Feature Layer for output
            column_datatype="Field"  # Field for column
        )
    
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
        normalize_and_categorize(self,
            parameters[0].valueAsText, 
            parameters[1].valueAsText, 
            parameters[2].valueAsText
        )
        return
    
class table(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalize into Categories (Table to GDB)"
        self.description = "Normalize and categorize GDB Table layers and save them to GDB"
        self.canRunInBackground = False

    def getParameterInfo(self):
        # Pass custom data types for this class
        return get_parameter_info(
            input_datatype=["GPTableView"],  # Feature Layer for input
            output_datatype=["GPTableView"],  # Feature Layer for output
            column_datatype="Field"  # Field for column
        )
    
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
        normalize_and_categorize(self,
            parameters[0].valueAsText, 
            parameters[1].valueAsText, 
            parameters[2].valueAsText
        )
        return