# -*- coding: utf-8 -*-
"""
/***************************************************************************
 WorChecker
                                 A QGIS plugin
 Dette plugin viser, hvilke filer et MapInfo workspace  refererer til.
                              -------------------
        begin                : 2018-08-06
        git sha              : $Format:%H$
        copyright            : (C) 2018 by Daníel Örn Árnason
        email                : daniel.arnason@egekom.dk
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QgsVectorLayer, QGis
from qgis.utils import iface
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from wor_checker_dialog import WorCheckerDialog
import os.path
import re


class WorChecker:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgisInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'WorChecker_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)


        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&MapInfo WOR Checker')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'WorChecker')
        self.toolbar.setObjectName(u'WorChecker')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('WorChecker', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        # Create the dialog (after translation) and keep reference
        self.dlg = WorCheckerDialog()

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        # Mine knapper
        self.dlg.pushButton.clicked.connect(self.path_to_wor)

        # Listwidgets og den slags
        self.dlg.listWidget.currentItemChanged.connect(self.file_info)

        # TODO: Slet denne knap til sidts
        self.dlg.pushButton_3.clicked.connect(self.open_file)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/WorChecker/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Check WOR fil'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&MapInfo WOR Checker'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def path_to_wor(self):
        """
        Finder path til wor fil og skriver ind i textbox.
        """

        wor_path = QFileDialog.getOpenFileName(self.dlg, 'V�lg MapInfo arbejdsomr�de')
        self.dlg.lineEdit.setText(wor_path)

        self.wor_data = self.read_wor_file(wor_path)

        self.dlg.listWidget.clear()
        self.dlg.listWidget.addItems([name for name in self.wor_data])
        

    def read_wor_file(self, filepath):
        """
        L�ser wor fil og finder filer.

        :returns: Dictionary med filnavne som key og path som values.
        """

        with open(filepath, 'r') as f:
            data = {}
            for line in f:
                if line.startswith('Open Table'):
                    path = re.findall(r'"(.*)"\s', line)[0]
                    data[os.path.basename(path)] = path + '.TAB'
        return data

    def file_info(self):
        """
        Læser info om valgt tab fil og skriver i info box.
        """
        self.dlg.textEdit.clear()

        filename = self.dlg.listWidget.currentItem().text()
        for f, path in self.wor_data.iteritems():
            if filename == f:
                lyr = QgsVectorLayer(path, f, 'ogr')
                lyr_geom_type = self.geom_type(lyr)
                self.dlg.textEdit.insertPlainText('Geometry type: {}'.format(lyr_geom_type))
                self.dlg.textEdit.insertPlainText('\nPath til fil: {}'.format(path))
    
    def geom_type(self, layer):
        """
        Tjekker om et layer er en valid datasource og returnerer typen.
        """

        if layer.isValid():
            if layer.wkbType() == QGis.WKBPoint:
                return 'Punkter'
            if layer.wkbType() == QGis.WKBLineString:
                return 'Linjer'
            if layer.wkbType() == QGis.WKBPolygon:
                return 'Polygoner'
            if layer.wkbType() == QGis.WKBMultiPolygon:
                return 'Multipolygoner'
        else:
            return '{} er ikke valid datakilde'.format(layer.name())

    def open_file(self):
        """
        Åbner en fil i lagvinduet
        """
        for f, path in self.wor_data.iteritems():
            if f == self.dlg.listWidget.currentItem().text():
                lyr = iface.addVectorLayer(path, os.path.basename(path), 'ogr')
                if not lyr.isValid():
                    print '{} er ikke en valid datakilde'.format(lyr.name())

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
