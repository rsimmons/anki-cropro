from aqt import mw
from aqt.qt import *
from aqt.utils import showInfo
from anki import Collection

def getColDeckNames(col):
    return sorted(col.decks.allNames())

def getOtherProfileNames():
    profiles = mw.pm.profiles()
    profiles.remove(mw.pm.name)
    return profiles

def openProfileCollection(name):
    # NOTE: this code is based on aqt/profiles.py; we can't really re-use what's there
    collectionFilename = os.path.join(mw.pm.base, name, 'collection.anki2')
    return Collection(collectionFilename)

class MainDialog(QDialog):
    def __init__(self):
        super(MainDialog, self).__init__()

        self.otherProfileName = None
        self.otherProfileCollection = None

        self.initUI()

    def initUI(self):
        self.noteListView = QListView()
        self.noteListModel = QStandardItemModel(self.noteListView)
        self.noteListView.setModel(self.noteListModel)
        self.noteListView.setSelectionMode(self.noteListView.ExtendedSelection)

        self.otherProfileDeckCombo = QComboBox()
        self.otherProfileDeckCombo.currentIndexChanged.connect(self.otherProfileDeckComboChange)

        self.otherProfileCombo = QComboBox()
        otherProfileNames = getOtherProfileNames()
        if otherProfileNames:
            self.otherProfileCombo.addItems(otherProfileNames)
            self.otherProfileCombo.currentIndexChanged.connect(self.otherProfileComboChange)
            self.handleSelectOtherProfile(otherProfileNames[0])
        else:
            # TODO: handle this case
            pass

        otherProfileDeckRow = QHBoxLayout()
        otherProfileDeckRow.addWidget(QLabel('Import From Profile:'))
        otherProfileDeckRow.addWidget(self.otherProfileCombo)
        otherProfileDeckRow.addWidget(QLabel('Deck:'))
        otherProfileDeckRow.addWidget(self.otherProfileDeckCombo)
        otherProfileDeckRow.addStretch(1)

        searchEdit = QLineEdit()
        searchEdit.setPlaceholderText('<search text>')

        searchRow = QHBoxLayout()
        searchRow.addWidget(searchEdit)
        searchRow.addWidget(QPushButton('Search'))

        currentProfileNameLabel = QLabel(mw.pm.name)
        currentProfileNameLabelFont = QFont()
        currentProfileNameLabelFont.setBold(True)
        currentProfileNameLabel.setFont(currentProfileNameLabelFont)

        currentProfileDeckCombo = QComboBox()
        currentProfileDeckCombo.addItems(getColDeckNames(mw.col))
        currentProfileDeckCombo.currentIndexChanged.connect(self.currentProfileDeckComboChange)

        importRow = QHBoxLayout()
        importRow.addWidget(QLabel('Into Profile:'))
        importRow.addWidget(currentProfileNameLabel)
        importRow.addWidget(QLabel('Deck:'))
        importRow.addWidget(currentProfileDeckCombo)

        importButton = QPushButton('Import')
        importButton.clicked.connect(self.importButtonClick)

        importRow.addWidget(importButton)
        importRow.addStretch(1)

        mainVbox = QVBoxLayout()
        mainVbox.addLayout(otherProfileDeckRow)
        mainVbox.addLayout(searchRow)
        mainVbox.addWidget(self.noteListView)
        mainVbox.addLayout(importRow)

        self.setLayout(mainVbox)

        self.setWindowTitle('Cross Profile Import')
        self.exec_()

    def otherProfileComboChange(self):
        newProfileName = self.otherProfileCombo.currentText()
        self.handleSelectOtherProfile(newProfileName)

    def otherProfileDeckComboChange(self):
        newDeckName = self.otherProfileDeckCombo.currentText()
        self.noteListModel.clear()
        if newDeckName:
            # deck was selected, fill list
            # TODO: need to quote the deck query in case deck name has spaces?
            noteIds = self.otherProfileCollection.findNotes('deck:' + newDeckName)
            # TODO: we could try to do this in a single sqlite query, but would be brittle
            for noteId in noteIds:
                note = self.otherProfileCollection.getNote(noteId)
                item = QStandardItem()
                item.setText(note.fields[0])
                item.setData(noteId)
                self.noteListModel.appendRow(item)
        else:
            # deck was unselected, leave list cleared
            pass

    def currentProfileDeckComboChange(self):
        showInfo('current profile deck change')

    def handleSelectOtherProfile(self, name):
        # Close current collection object, if any
        if self.otherProfileCollection:
            self.otherProfileCollection.close()
            self.otherProfileCollection = None

        self.otherProfileName = name
        self.otherProfileCollection = openProfileCollection(name)

        self.otherProfileDeckCombo.clear()
        self.otherProfileDeckCombo.addItems(getColDeckNames(self.otherProfileCollection))

    def importButtonClick(self):
        # Get the note ids of all selected notes
        noteIds = [self.noteListModel.itemFromIndex(idx).data() for idx in self.noteListView.selectedIndexes()]
        notesStr = ';'.join(repr(self.otherProfileCollection.getNote(nid).items()) for nid in noteIds)
        showInfo('import: ' + notesStr)
        for nid in noteIds:
            note = self.otherProfileCollection.getNote(nid)

    def closeEvent(self, event):
        if self.otherProfileCollection:
            self.otherProfileCollection.close()
        super(MainDialog, self).closeEvent(event)

def addMenuItem():
    a = QAction(mw)
    a.setText('Cross Profile Import')
    mw.form.menuTools.addAction(a)
    a.triggered.connect(MainDialog)


addMenuItem()
