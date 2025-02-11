# -*- coding: utf-8 -*-

import arcpy
import math
import sys
import os


class Toolbox(object):
    def __init__(self):
        """Define the toolbox (the name of the toolbox is the name of the
        .pyt file)."""
        self.label = "Normalization and categoryzation of data into three categories"
        self.alias = "NORM_CAT"

        # List of tool classes associated with this toolbox
        self.tools = [Tool1]


class Tool1(object):
    def __init__(self):
        """Define the tool (tool name is the name of the class)."""
        self.label = "Normalization&Caterorization"
        self.description = ""
        self.canRunInBackground = False

    def getParameterInfo(self):
        """Define parameter definitions"""
       
       
        # Input SHP layer with intersected grid and land patches
        param0 = arcpy.Parameter(
            displayName="Input Layer or Table",
            name="input_layer",
            datatype=["GPFeatureLayer", "DETable"],
            parameterType="Required",
            direction="Input"
            )
        
     
        # Output SHP Layer
        param1 = arcpy.Parameter(
            displayName="Output Layer or Table",
            name="out_features",
            datatype=["GPFeatureLayer", "DETable", "DEShapeFile"],
            parameterType="Required",
            direction="Output")
        
    
        # Name of field with information about gridcell ID
        param2 = arcpy.Parameter(
            displayName="Column",
            name="column",
            datatype="Field",
            parameterType="Required",
            direction="Input")

        param1.parameterDependencies = [param0.name]
        param1.schema.clone = True
        
        params = [param0, param1, param2]
        
        return params

    def isLicensed(self):
        """Set whether tool is licensed to execute."""
        return True

    def updateParameters(self, parameters):
        """Modify the values and properties of parameters before internal
        validation is performed.  This method is called whenever a parameter
        has been changed."""
        return

    def updateMessages(self, parameters):
        """Modify the messages created by internal validation for each tool
        parameter.  This method is called after internal validation."""
        return

    def execute(self, parameters, messages):
        """The source code of the tool."""
        
        # get text value of parameters
        INPUT_LAYER = parameters[0].valueAsText
        OUTPUT_LAYER = parameters[1].valueAsText
    
        COLUMN = parameters[2].valueAsText
        
        # Define datype for fields
        FIELD_TYPE_NORM = "DOUBLE"
        FIELD_TYPE_CAT = "INTEGER"
      
        # Create copy of input layer to preserve original data
        input_layer_copy = arcpy.Copy_management(
            INPUT_LAYER, 
            OUTPUT_LAYER)
        
        # add field for calculation for perimeter of the land patch    
        arcpy.management.AddField(
            input_layer_copy, 
            "NORMAL", 
            FIELD_TYPE_NORM)
        
        # add field for calculation for gridcell area
        arcpy.management.AddField(
            input_layer_copy, 
            "CATS", 
            FIELD_TYPE_CAT)
        
        min_value = float('inf')
        max_value = float('-inf')

        # Normalize the values
        with arcpy.da.SearchCursor(OUTPUT_LAYER, [COLUMN]) as cursor:
            for row in cursor:
                value = row[0]
                if value < min_value:
                    min_value = value
                if value > max_value:
                    max_value = value
        expression = "(!{}! - {}) / ({}) + 1".format(COLUMN, min_value, max_value - min_value)

        # Run CalculateField to create the new 'NORMAL' field
        arcpy.management.CalculateField(
            OUTPUT_LAYER,
            "NORMAL",
            expression,
            expression_type="PYTHON3"
        )

        # Define the expression for categorizing the 'NORMAL' values
        categorization_expression = (
            "1 if (float(!NORMAL!) >= 1 and float(!NORMAL!) <= 1.33) else " +
            "2 if (float(!NORMAL!) > 1.33 and float(!NORMAL!) <= 1.66) else " +
            "3 if (float(!NORMAL!) > 1.66 and float(!NORMAL!) <= 2) else None"
        )

        arcpy.management.CalculateField(
        OUTPUT_LAYER,
        "CATS",
        categorization_expression,
        expression_type="PYTHON3"
        )

        return
    

