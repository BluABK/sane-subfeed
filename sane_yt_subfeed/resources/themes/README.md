HOWTO Create A Theme
====================

### 1. Create a QSS file

#### Standard QSS

QSS is merely Qt flavoured CSS.

Examples: https://doc.qt.io/qt-5/stylesheet-examples.html

Reference sheet: https://doc.qt.io/qt-5/stylesheet-reference.html

#### Sane Flavoured QSS

These additional custom objects are also stylable:

Main window (inherits **QMainWindow**)
* MainWindow

Dialogs (inherits **QDialog**)
* SaneDialog
* SaneConfirmationDialog
* SaneInputDialog
* SaneTextViewDialog
* SaneOAuth2BuilderDialog

Scroll areas (inherits **QScrollArea**)
* GridScrollArea
* DownloadScrollArea
* ConfigWindow
* ConfigScrollArea

Tab widgets (inherits **QTabWidget**)
* ConfigViewTabs

[//]: # (Abandoned for now due to override unsetting all the defaults into an unusable status)
[//]: # (Progress bars (inherits **QProgressBar**)
[//]: # (* DownloadProgressBar)

Toolbars (inherits **QToolBar**)
* Toolbar

Views (inherits **QWidget**)
  * GridView
    * SubfeedGridView
    * PlaybackGridView
  * SubfeedTiledListView
    * ExtendedQLabel
  * DownloadView
  * SubfeedDetailedListView
  * SubscriptionsDetailedListView
  * InputSuper
    * ConfigViewWidget
    * HotkeysViewWidget
  * AboutView
    * ExtendedQLabel

Tiles (inherits **QWidget**)
  * VideoTile
    * SubfeedGridViewTile
    * PlaybackGridViewTile
  * DownloadTile

Labels (inherits **QLabel**):
  * ElidedLabel
    * TitleLabel
    * ChannelLabel
    * DateLabel
  * SmallLabel
  * DbStateIcon

Buttons (inherits **QWidget**)
* ButtonsTile

Buttons (inherits **QPushButton**)
* ClearFinishedDownloads
* GenericConfigPushButton
* FontPickerButton

Checkboxes (inherits **QCheckBox**)
* GenericConfigCheckBox

Combo boxes (inherits **QComboBox**)
* GenericConfigComboBox

Line editors (inherits **QLineEdit**)
* GenericLineEdit

### 2. Define any required resources in a QRC file

Format:

```xml
<RCC>
  <qresource>
    <file>img/menubar.png</file>
    <file>img/toolbar.png</file>
  </qresource>
</RCC>
```

### 3. Compile the QRC file into a PyQt5 compatible script


In order for PyQt5 to recognise your resources (if you have any) you need to compile the QRC file into a resources.py
script:
 
 `pyrcc5 resources.qrc -o resources.py`


### 4. Create a metadata JSON (optional, but recommended)

Format:
```json
{
  "name": "<name>",
  "version": "<version>",
  "author": "<author>",
  "description": "<description>",
  "compiled_qrc": "resources.py",
  "variants":
  [
    {
      "name": "<variant 1>",
      "path": "<variant 1 filename>.qss",
      "platform_whitelist": null
    },
    {
      "name": "<variant 2>",
      "path": "<variant 2 filename>.qss",
      "platform_whitelist": ["win32", "darwin"]
    }
  ]
}
```

  * `platform whitelist` can be `null` or a list of platforms (win32/linux/cygwin/darwin).
  * `complied_qrc` is only relevant if you have compiled a QRC file, if else leave it as `null`.