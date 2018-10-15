from PySide2 import QtWidgets, QtCore
import NameManagerUI as name_UI
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import maya.cmds as cmds


def maya_main_window():
    main_window_ptr = omui.MQtUtil.mainWindow()
    return wrapInstance(long(main_window_ptr), QtWidgets.QMainWindow)


class NameManagerDialog(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        #creating the main window
        super(NameManagerDialog, self).__init__(parent)
        self.setWindowFlags(QtCore.Qt.Tool)
        self.ui = name_UI.Ui_MainWindow()
        self.ui.setupUi(self)
        self.type = ""
        self.side = ""
        self.kinematic = ""
        self.mesh_name = ""

        #connecting the buttons
        buttons = self.ui.centralwidget.findChildren(QtWidgets.QPushButton)
        for button in buttons:
            if "mirror" not in button.objectName() and "hierarchy" not in button.objectName():
                button.clicked.connect(lambda name=button.objectName(): self.rename_object(name))

        self.ui.btn_create_hierarchy.clicked.connect(self.create_hierarchy)
        self.ui.btn_mirror.clicked.connect(self.mirror_and_rename)

        #connecting the radio buttons
        radio_btns = self.ui.centralwidget.findChildren(QtWidgets.QRadioButton)
        for radio_btn in radio_btns:
            radio_btn.toggled.connect(lambda status, name=radio_btn.objectName(): self.set_object_type(name))

        # connecting the combo boxes
        self.ui.com_box_side.currentIndexChanged.connect(self.set_side)

        self.ui.com_box_kinematic.currentIndexChanged.connect(self.set_kinematic)

    def mirror_and_rename(self):
        """
        Gets the list of all the selected objects of type 'joint' and their hierarchy.
        Mirrors each joint (and child) on the YX axes and renames each joint substituting
        '_L_' with '_R_".
        """

        objects_selected = cmds.ls(sl=True, l=True) or []

        if objects_selected:
            if cmds.objectType(objects_selected[0]) == 'joint':
                cmds.mirrorJoint(objects_selected, myz=True, mb=True, sr=('_L_', '_R_'))
        else:
            cmds.warning("You must select an object")


    def create_hierarchy(self):
        """
        Creates the group structure to store the rig
        """

        mesh_name = self.ui.edit_object_name.text()
        if cmds.objExists(mesh_name + "_main"):
            cmds.warning("Group already exists")
        elif mesh_name:
            cmds.group(n=mesh_name + "_main", em = True)
            cmds.group(n=mesh_name + "_global_control", em = True, p = mesh_name + "_main")
            cmds.group(n=mesh_name + "_extra_nodes", em=True, p=mesh_name + "_main")
            cmds.group(n=mesh_name + "_global_blendshapes", em=True, p=mesh_name + "_main")
            cmds.group(n=mesh_name + "_global_geo", em=True, p=mesh_name + "_main")
            cmds.group(n=mesh_name + "_global_scale", em=True, p=mesh_name + "_global_control")
            cmds.group(n=mesh_name + "_joints", em=True, p=mesh_name + "_global_scale")
            cmds.group(n=mesh_name + "_IK", em=True, p=mesh_name + "_global_scale")
            cmds.group(n=mesh_name + "_controls", em=True, p=mesh_name + "_global_scale")
        else:
            cmds.warning("Please select a mesh name")

    def set_kinematic(self):
        """
        Gets the value of the kinematic combo box and stores it in the attribute 'kinematic'
        """
        k = self.ui.com_box_kinematic.currentText()
        if k == "None": self.kinematic = ""
        elif k == "Inverse":  self.kinematic = "_IK"
        else: self.kinematic = "_FK"

    def set_side(self):
        """
        Gets the value of the side (left or right) combo box and stores it in the attribute 'side'
        """
        side = self.ui.com_box_side.currentText()
        if side == "None": self.side = ""
        else: self.side = "_"+side[0]

    def set_object_type(self, name):
        """
        Gets the value of the new object type from the active radio button and stores it in the
        attribute 'type'
        """

        object_name = name.replace("radio_btn", "")
        if object_name == "_null": object_name = ""

        self.type = object_name

    def rename_object(self, name):
        """
        Renames the selected object, or chain of objects, according to the mesh name, type or custom name type,
        side, kinematic and and body part selected. The objects are indexed with increasing numbers to avoid
        duplicates
        """

        #verify if the user input a name for the mesh.
        mesh_name = self.ui.edit_object_name.text()
        if mesh_name:
            # If the input exists...get the list of all the objects selected and all names in the outiner
            objects_selected = cmds.ls(sl=True, l=True) or []
            objects_selected.sort(reverse=True)

            #if the user selected at least an object to rename create the new name
            if objects_selected:
                if "apply" in name: object_name = "_"+self.ui.edit_pers_name.text()
                else: object_name = name.replace("btn", "")

                composite_name = mesh_name + self.side + object_name + self.type + self.kinematic
                #count duplicates of the same base name
                existing_indices = [0]
                for o in cmds.ls():
                    o_parts = o.split("_")
                    if composite_name == o.strip(o_parts[-1]):
                        o = o.split("_")
                        existing_indices.append(int(o[-1]))

                max_index = max(existing_indices)
                print "max" + str(max_index)
                new_indices = list(reversed(range(max_index+1, max_index+len(objects_selected)+1)))

                for index, object in zip(new_indices, objects_selected):
                    cmds.rename(object, composite_name + "_" + str(index))
            else:
                cmds.warning("You must select an object to rename")
        else:
            cmds.warning("You must select a mesh name")


myWin = NameManagerDialog(parent=maya_main_window())
myWin.show()

















