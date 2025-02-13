# -*- coding: utf-8 -*-

import arcpy
import math
import sys
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the .pyt file)."""
        # Label and alias for the toolbox, defining the description and the tools included.
        self.label = "Normalization and categorization of data into three categories"
        self.alias = "NORM_CAT"

        # List of tool classes associated with this toolbox.
        # In this case, it includes Tool1 (the tool we're defining), Tool2 (for SHP), and Tool3 (for tables).
        self.tools = [fc, shp, table]


def normalize_and_categorize(self, input_layer, output_layer, column):
        """Shared function for normalizing and categorizing."""
        # Define constants for the new fields' types
        FIELD_TYPE_NORM = "DOUBLE"  # 'NORMAL' field will be of type DOUBLE for normalization
        FIELD_TYPE_CAT = "INTEGER"  # 'CATS' field will be of type INTEGER for categorization
        
        # Create a copy of the input layer to preserve the original data
        input_layer_copy = arcpy.Copy_management(input_layer, output_layer)
        
        # Add a new field 'NORMAL' in the copied layer to store normalized values
        arcpy.management.AddField(input_layer_copy, "NORMAL", FIELD_TYPE_NORM)
        
        # Add a new field 'CATS' to store the categorized values
        arcpy.management.AddField(input_layer_copy, "CATS", FIELD_TYPE_CAT)
        
        # Initialize min and max values for normalization calculations
        min_value = float('inf')
        max_value = float('-inf')

        # Use a SearchCursor to calculate the minimum and maximum values for the specified column
        with arcpy.da.SearchCursor(output_layer, [column]) as cursor:
            for row in cursor:
                value = row[0]  # Extract the value from the current row's specified column
                if value < min_value:
                    min_value = value  # Update the min value
                if value > max_value:
                    max_value = value  # Update the max value
        
        # Create the expression for normalization based on min/max values
        expression = "(!{}! - {}) / ({}) + 1".format(column, min_value, max_value - min_value)

        # Run CalculateField to fill the 'NORMAL' field with normalized values
        arcpy.management.CalculateField(output_layer, "NORMAL", expression, expression_type="PYTHON3")

        # Define the expression for categorizing the normalized values into 3 categories
        categorization_expression = (
            "1 if (float(!NORMAL!) >= 1 and float(!NORMAL!) <= 1.33) else " +
            "2 if (float(!NORMAL!) > 1.33 and float(!NORMAL!) <= 1.66) else " +
            "3 if (float(!NORMAL!) > 1.66 and float(!NORMAL!) <= 2) else None"
        )

        # Run CalculateField to categorize the normalized values into the 'CATS' field
        arcpy.management.CalculateField(output_layer, "CATS", categorization_expression, expression_type="PYTHON3")


def get_parameter_info(input_datatype, output_datatype, column_datatype):
    """Shared function for getting parameter definitions with customizable data types."""
    # Define the first parameter (input layer or table)
    param0 = arcpy.Parameter(
        displayName="Input Layer or Table",  # Label for the input parameter
        name="input_layer",  # Name of the input parameter
        datatype=input_datatype,  # Data type for input (customizable for each class)
        parameterType="Required",  # This parameter is required
        direction="Input"  # Direction of data flow (input)
    )
    
    # Define the second parameter (output layer or table)
    param1 = arcpy.Parameter(
        displayName="Output Layer or Table",  # Label for the output parameter
        name="out_features",  # Name of the output parameter
        datatype=output_datatype,  # Data type for output (customizable for each class)
        parameterType="Required",  # This parameter is required
        direction="Output"  # Direction of data flow (output)
    )

    # Define the third parameter (column to be normalized)
    param2 = arcpy.Parameter(
        displayName="Column",  # Label for the column parameter
        name="column",  # Name of the column parameter
        datatype=column_datatype,  # Data type for the column (customizable for each class)
        parameterType="Required",  # This parameter is required
        direction="Input"  # Direction of data flow (input)
    )

    # Set parameter dependencies (output depends on input)
    param1.parameterDependencies = [param0.name]
    param1.schema.clone = True  # Cloning schema to ensure output matches input format

    # Combine the parameters into a list
    params = [param0, param1, param2]
    
    # Set a filter to accept only valid field types for the 'column' parameter
    params[2].filter.list = ['Short', 'Long', 'Float', 'Double']  # Field data types
    params[2].parameterDependencies = [params[0].name]  # Column depends on input layer

    return params  # Return the list of parameters


class fc(object):
    """Tool class for normalizing and categorizing feature classes (FC to GDB)."""
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalize into Categories (Feature Class to GDB)"  # Tool label
        self.description = "Normalize and categorize Feature Class layers and save them to File GeoDatabase"  # Tool description
        self.canRunInBackground = False  # Tool does not run in the background

    def getParameterInfo(self):
        # Get the parameter definitions with custom data types for this class
        return get_parameter_info(
            input_datatype=["GPFeatureLayer"],  # Input is a Feature Layer
            output_datatype=["GPFeatureLayer"],  # Output is a Feature Layer
            column_datatype="Field"  # Column is a field
        )
            
    def isLicensed(self):
        """Check if the tool is licensed to execute."""
        return True  # Tool is licensed

    def updateParameters(self, parameters):
        """Update parameters if necessary (no implementation in this case)."""
        return

    def updateMessages(self, parameters):
        """Modify messages after internal validation (no implementation in this case)."""
        return

    def execute(self, parameters, messages):
        """Run the normalization and categorization function."""
        # Call the shared function for normalizing and categorizing with the specified parameters
        normalize_and_categorize(self,
            parameters[0].valueAsText,  # Input layer
            parameters[1].valueAsText,  # Output layer
            parameters[2].valueAsText  # Column to normalize
        )
        return
    

class shp(object):
    """Tool class for normalizing and categorizing shapefiles (SHP to SHP)."""
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalize into Categories (SHP to SHP)"  # Tool label
        self.description = "Normalize and categorize ShapeFile files and save them to folder"  # Tool description
        self.canRunInBackground = False  # Tool does not run in the background

    def getParameterInfo(self):
        # Get the parameter definitions with custom data types for this class
        return get_parameter_info(
            input_datatype=["DEShapeFile"],  # Input is a shapefile
            output_datatype=["DEShapeFile"],  # Output is a shapefile
            column_datatype="Field"  # Column is a field
        )
    
    def isLicensed(self):
        """Check if the tool is licensed to execute."""
        return True  # Tool is licensed

    def updateParameters(self, parameters):
        """Update parameters if necessary (no implementation in this case)."""
        return

    def updateMessages(self, parameters):
        """Modify messages after internal validation (no implementation in this case)."""
        return

    def execute(self, parameters, messages):
        """Run the normalization and categorization function."""
        # Call the shared function for normalizing and categorizing with the specified parameters
        normalize_and_categorize(self,
            parameters[0].valueAsText,  # Input shapefile
            parameters[1].valueAsText,  # Output shapefile
            parameters[2].valueAsText  # Column to normalize
        )
        return
    
class table(object):
    """Tool class for normalizing and categorizing tables (Table to GDB)."""
    
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalize into Categories (Table to GDB)"  # Tool label
        self.description = "Normalize and categorize GDB Table layers and save them to GDB"  # Tool description
        self.canRunInBackground = False  # Tool does not run in the background

    def getParameterInfo(self):
        # Get the parameter definitions with custom data types for this class
        return get_parameter_info(
            input_datatype=["GPTableView"],  # Input is a table view
            output_datatype=["GPTableView"],  # Output is a table view
            column_datatype="Field"  # Column is a field
        )
    
    def isLicensed(self):
        """Check if the tool is licensed to execute."""
        return True  # Tool is licensed

    def updateParameters(self, parameters):
        """Update parameters if necessary (no implementation in this case)."""
        return

    def updateMessages(self, parameters):
        """Modify messages after internal validation (no implementation in this case)."""
        return

    def execute(self, parameters, messages):
        """Run the normalization and categorization function."""
        # Call the shared function for normalizing and categorizing with the specified parameters
        normalize_and_categorize(self,
            parameters[0].valueAsText,  # Input table
            parameters[1].valueAsText,  # Output table
            parameters[2].valueAsText  # Column to normalize
        )
        return
