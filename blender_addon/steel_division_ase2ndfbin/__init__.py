# SPDX-License-Identifier: GPL-3.0-or-later
"""File > Export > Steel Division Tank (.Ase2NdfBin)."""

import bpy
from bpy.props import BoolProperty, FloatProperty, StringProperty
from bpy_extras.io_utils import ExportHelper

from . import exporter


class EXPORT_OT_steel_division(bpy.types.Operator, ExportHelper):
    """Export the scene as a Steel Division: Normandy 44 tank mesh"""

    bl_idname = "export_scene.steel_division"
    bl_label = "Export Ase2NdfBin"
    bl_options = {"PRESET"}

    filename_ext = ".Ase2NdfBin"
    filter_glob: StringProperty(default="*.Ase2NdfBin", options={"HIDDEN"})

    scale: FloatProperty(
        name="Units per Metre",
        description="Game units per Blender metre. The game's tanks use about 203",
        default=exporter.DEFAULT_SCALE,
        min=1.0,
        max=10000.0,
    )
    copy_textures: BoolProperty(
        name="Copy Textures",
        description="Copy the textures named by the materials next to the exported file",
        default=True,
    )

    def execute(self, context):
        try:
            result = exporter.export_scene(context.scene, self.filepath, self.scale, self.copy_textures)
        except exporter.ExportProblem as problem:
            for message in problem.errors:
                self.report({"ERROR"}, message)
            return {"CANCELLED"}
        for message in result["warnings"]:
            self.report({"WARNING"}, message)
        self.report({"INFO"}, "Exported %d triangles, %d nodes" % (result["triangles"], result["nodes"]))
        return {"FINISHED"}


def menu_func_export(self, _context):
    self.layout.operator(EXPORT_OT_steel_division.bl_idname, text="Steel Division Tank (.Ase2NdfBin)")


def register():
    bpy.utils.register_class(EXPORT_OT_steel_division)
    bpy.types.TOPBAR_MT_file_export.append(menu_func_export)


def unregister():
    bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
    bpy.utils.unregister_class(EXPORT_OT_steel_division)
