#!/usr/bin/env python3
import sys
from PyQt5.QtWidgets import (
    QApplication, QDialog, QTabWidget, QWidget, QVBoxLayout, QHBoxLayout,
    QGridLayout, QFormLayout, QLabel, QComboBox, QRadioButton, QButtonGroup,
    QCheckBox, QSpinBox, QPushButton, QListWidget, QSizePolicy,
    QDialogButtonBox, QGroupBox, QSpacerItem, QStyle, QToolButton, QFrame
)
from PyQt5.QtGui import QPixmap, QIcon, QPainter, QFont
from PyQt5.QtCore import Qt, QSize, QRect

def get_icon(primary_name, secondary_name=None, fallback_style_pixmap_enum=None):
    """
    Helper function untuk memuat ikon dengan fallback.
    1. Coba primary_name dari tema.
    2. Jika gagal & secondary_name ada, coba secondary_name dari tema.
    3. Jika masih gagal & fallback_style_pixmap_enum ada, gunakan ikon standar QStyle.
    Mengembalikan QIcon object (bisa jadi QIcon kosong jika semua gagal).
    """
    icon = QIcon.fromTheme(primary_name)
    if icon.isNull() and secondary_name:
        icon = QIcon.fromTheme(secondary_name)
    if icon.isNull() and fallback_style_pixmap_enum is not None:
        app_instance = QApplication.instance()
        if app_instance:
            try:
                standard_icon = app_instance.style().standardIcon(fallback_style_pixmap_enum)
                if not standard_icon.isNull():
                    icon = standard_icon
            except Exception as e:
                print(f"Error saat memuat ikon QStyle fallback: {e}")
    if icon.isNull():
        return QIcon()
    return icon

def create_placeholder_icon_with_text(text_lines, icon_size=QSize(48, 48), background_color=Qt.lightGray, border_color=Qt.darkGray):
    """Membuat QIcon placeholder dengan teks di dalamnya."""
    pixmap = QPixmap(icon_size)
    pixmap.fill(background_color)
    painter = QPainter(pixmap)
    
    pen = painter.pen()
    pen.setColor(border_color)
    pen.setWidth(1)
    painter.setPen(pen)
    painter.drawRect(0, 0, icon_size.width() -1, icon_size.height() -1)

    font_size = 9
    if isinstance(text_lines, str): 
        text_lines = [text_lines]

    if len(text_lines) == 1:
        font_size = 10
    elif len(text_lines) > 2:
        font_size = 7
        
    font = painter.font()
    font.setPointSize(font_size)
    painter.setFont(font)
    pen.setColor(Qt.black)
    painter.setPen(pen)

    num_lines = len(text_lines)
    padding = 2 
    total_text_height = (font_size + padding) * num_lines - padding
    start_y = (icon_size.height() - total_text_height) // 2
    
    for i, line in enumerate(text_lines):
        line_y = start_y + i * (font_size + padding)
        rect_line = QRect(0, line_y, icon_size.width(), font_size + padding)
        painter.drawText(rect_line, Qt.AlignCenter | Qt.TextDontClip, line)
        
    painter.end()
    return QIcon(pixmap)

class LinuxPrinterPreferencesDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Printing Preferences (Linux Style with Fallback Icons)")
        self.setMinimumSize(750, 600) 

        main_dialog_layout = QVBoxLayout(self)
        self.tab_widget = QTabWidget()
        self.tab_main = QWidget()
        self.tab_more_options = QWidget()
        self.tab_maintenance = QWidget()

        self.tab_widget.addTab(self.tab_main, "Main")
        self.tab_widget.addTab(self.tab_more_options, "More Options")
        self.tab_widget.addTab(self.tab_maintenance, "Maintenance")

        self.setup_main_tab()
        self.setup_more_options_tab()
        self.setup_maintenance_tab()

        main_dialog_layout.addWidget(self.tab_widget)

        bottom_button_layout = QHBoxLayout()
        help_icon = get_icon("help-contents", "help-faq", QStyle.SP_DialogHelpButton)
        self.help_button = QPushButton(help_icon, "Help")

        self.dialog_button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.dialog_button_box.accepted.connect(self.accept)
        self.dialog_button_box.rejected.connect(self.reject)

        bottom_button_layout.addStretch(1)
        bottom_button_layout.addWidget(self.help_button)
        bottom_button_layout.addWidget(self.dialog_button_box)
        main_dialog_layout.addLayout(bottom_button_layout)

    def _create_left_panel_content(self, parent_layout, include_ink_levels=True):
        left_column_layout = QVBoxLayout()
        presets_groupbox = QGroupBox("Printing Presets")
        presets_layout = QVBoxLayout()
        presets_list = QListWidget()
        presets_list.addItems([
            "Document - Fast", "Document - Standard Quality", "Document - High Quality",
            "Document - 2-Up", "Document - Fast Grayscale", "Document - Grayscale"
        ])
        add_remove_icon = get_icon("list-add", "document-new", QStyle.SP_FileDialogNewFolder)
        add_remove_presets_button = QPushButton(add_remove_icon, "Add/Remove Presets...")
        presets_layout.addWidget(presets_list)
        presets_layout.addWidget(add_remove_presets_button)
        presets_groupbox.setLayout(presets_layout)
        left_column_layout.addWidget(presets_groupbox)

        preview_layout = QHBoxLayout()
        doc_preview_label = QLabel()
        doc_icon = get_icon("text-x-generic", "document-new", QStyle.SP_FileIcon)
        if not doc_icon.isNull():
            doc_pixmap = doc_icon.pixmap(QSize(80, 80))
            if not doc_pixmap.isNull():
                doc_preview_label.setPixmap(doc_pixmap)
            else:
                doc_preview_label.setText("📄\n(Gagal Pixmap Dok)")
        else:
            doc_preview_label.setText("📄\n(Gagal Ikon Dok)")
        doc_preview_label.setFixedSize(100, 100)
        doc_preview_label.setAlignment(Qt.AlignCenter)
        doc_preview_label.setStyleSheet("border: 1px solid gray;")

        printer_preview_label = QLabel()
        printer_icon = get_icon("printer", "printer-printing", QStyle.SP_DriveHDIcon)
        if not printer_icon.isNull():
            printer_pixmap = printer_icon.pixmap(QSize(80, 80))
            if not printer_pixmap.isNull():
                printer_preview_label.setPixmap(printer_pixmap)
            else:
                printer_preview_label.setText("🖨️\n(Gagal Pixmap Printer)")
        else:
            printer_preview_label.setText("🖨️\n(Gagal Ikon Printer)")
        printer_preview_label.setFixedSize(100, 100)
        printer_preview_label.setAlignment(Qt.AlignCenter)
        printer_preview_label.setStyleSheet("border: 1px solid gray;")

        preview_layout.addWidget(doc_preview_label)
        preview_layout.addWidget(printer_preview_label)
        left_column_layout.addLayout(preview_layout)
        left_column_layout.addStretch(1)

        reset_defaults_icon = get_icon("edit-undo", "document-revert", QStyle.SP_ArrowLeft)
        reset_defaults_button = QPushButton(reset_defaults_icon,"Reset Defaults")
        left_column_layout.addWidget(reset_defaults_button)

        if include_ink_levels:
            ink_icon = get_icon("media-color-management", "preferences-color", QStyle.SP_CustomBase)
            ink_levels_button = QPushButton(ink_icon, "Ink Levels")
            left_column_layout.addWidget(ink_levels_button)
        parent_layout.addLayout(left_column_layout, 1)
        
    def setup_main_tab(self):
        main_tab_layout = QHBoxLayout(self.tab_main)
        self._create_left_panel_content(main_tab_layout, include_ink_levels=True)
        right_column_wrapper = QVBoxLayout()
        right_column_grid = QGridLayout()
        right_column_grid.setSpacing(10)
        settings_icon = get_icon("preferences-configure", "configure", QStyle.SP_DesktopIcon)

        right_column_grid.addWidget(QLabel("Document Size:"), 0, 0, Qt.AlignRight)
        doc_size_combo = QComboBox()
        paper_sizes = ["Letter (8 1/2 x 11 in)", "A4 (210 x 297 mm)", "Legal (8 1/2 x 14 in)"]
        doc_size_combo.addItems(paper_sizes)
        a4_text = "A4 (210 x 297 mm)"
        if a4_text in paper_sizes:
            doc_size_combo.setCurrentText(a4_text)
        doc_size_settings_button = QPushButton(settings_icon, "Settings...")
        doc_size_layout = QHBoxLayout()
        doc_size_layout.addWidget(doc_size_combo)
        doc_size_layout.addWidget(doc_size_settings_button)
        right_column_grid.addLayout(doc_size_layout, 0, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Orientation:"), 1, 0, Qt.AlignRight)
        orientation_portrait_radio = QRadioButton("Portrait")
        orientation_landscape_radio = QRadioButton("Landscape")
        orientation_portrait_radio.setChecked(True)
        orientation_group = QButtonGroup(self.tab_main)
        orientation_group.addButton(orientation_portrait_radio)
        orientation_group.addButton(orientation_landscape_radio)
        orientation_layout = QHBoxLayout()
        orientation_layout.addWidget(orientation_portrait_radio)
        orientation_layout.addWidget(orientation_landscape_radio)
        orientation_layout.addStretch()
        right_column_grid.addLayout(orientation_layout, 1, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Paper Type:"), 2, 0, Qt.AlignRight)
        paper_type_combo = QComboBox()
        paper_type_combo.addItems(["Plain Paper / Bright White Paper", "Photo Paper Glossy", "Matte Paper"])
        right_column_grid.addWidget(paper_type_combo, 2, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Quality:"), 3, 0, Qt.AlignRight)
        quality_combo = QComboBox()
        quality_combo.addItems(["Standard", "Draft", "High", "Best"])
        right_column_grid.addWidget(quality_combo, 3, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Color:"), 4, 0, Qt.AlignRight)
        color_color_radio = QRadioButton("Color")
        color_grayscale_radio = QRadioButton("Black/Grayscale")
        color_color_radio.setChecked(True)
        color_group = QButtonGroup(self.tab_main)
        color_group.addButton(color_color_radio)
        color_group.addButton(color_grayscale_radio)
        color_layout = QHBoxLayout()
        color_layout.addWidget(color_color_radio)
        color_layout.addWidget(color_grayscale_radio)
        color_layout.addStretch()
        right_column_grid.addLayout(color_layout, 4, 1, 1, 2)

        sided_printing_checkbox = QCheckBox("2-Sided Printing")
        sided_printing_settings_button = QPushButton(settings_icon, "Settings...")
        sided_printing_settings_button.setEnabled(False)
        sided_printing_checkbox.toggled.connect(sided_printing_settings_button.setEnabled)
        sided_layout = QHBoxLayout()
        sided_layout.addWidget(sided_printing_checkbox)
        sided_layout.addWidget(sided_printing_settings_button)
        sided_layout.addStretch()
        right_column_grid.addLayout(sided_layout, 5, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Multi-Page:"), 6, 0, Qt.AlignRight)
        multipage_combo = QComboBox()
        multipage_combo.addItems(["Off", "2 Up", "4 Up", "Custom..."])
        page_order_icon = get_icon("view-page-continuous-symbolic", "format-justify-fill", QStyle.SP_ToolBarVerticalExtensionButton)
        multipage_pageorder_button = QPushButton(page_order_icon,"Page Order...")
        multipage_pageorder_button.setEnabled(False)
        multipage_combo.currentIndexChanged.connect(
            lambda: multipage_pageorder_button.setEnabled(multipage_combo.currentText() != "Off")
        )
        multipage_layout = QHBoxLayout()
        multipage_layout.addWidget(multipage_combo)
        multipage_layout.addWidget(multipage_pageorder_button)
        right_column_grid.addLayout(multipage_layout, 6, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Copies:"), 7, 0, Qt.AlignRight)
        copies_spinbox = QSpinBox()
        copies_spinbox.setMinimum(1)
        copies_spinbox.setValue(1)
        collate_checkbox = QCheckBox("Collate")
        collate_checkbox.setChecked(True)
        reverse_order_checkbox = QCheckBox("Reverse Order")
        copies_layout = QHBoxLayout()
        copies_layout.addWidget(copies_spinbox)
        copies_layout.addWidget(collate_checkbox)
        copies_layout.addWidget(reverse_order_checkbox)
        copies_layout.addStretch()
        right_column_grid.addLayout(copies_layout, 7, 1, 1, 2)

        print_preview_checkbox = QCheckBox("Print Preview")
        job_arranger_checkbox = QCheckBox("Job Arranger Lite")
        quiet_mode_checkbox = QCheckBox("Quiet Mode")
        checkboxes_layout = QVBoxLayout()
        checkboxes_layout.addWidget(print_preview_checkbox)
        checkboxes_layout.addWidget(job_arranger_checkbox)
        checkboxes_layout.addWidget(quiet_mode_checkbox)
        right_column_grid.addLayout(checkboxes_layout, 8, 1, Qt.AlignTop)
        right_column_grid.setRowStretch(9, 1)
        right_column_wrapper.addLayout(right_column_grid)
        right_column_wrapper.addStretch(1)

        show_settings_icon = get_icon("document-properties", "preferences-system", QStyle.SP_DialogApplyButton)
        show_settings_button_main = QPushButton(show_settings_icon, "Show Settings")
        show_settings_layout_main = QHBoxLayout()
        show_settings_layout_main.addStretch(1)
        show_settings_layout_main.addWidget(show_settings_button_main)
        right_column_wrapper.addLayout(show_settings_layout_main)
        main_tab_layout.addLayout(right_column_wrapper, 2)

    def setup_more_options_tab(self):
        more_options_tab_layout = QHBoxLayout(self.tab_more_options)
        self._create_left_panel_content(more_options_tab_layout, include_ink_levels=False)
        right_column_wrapper = QVBoxLayout()
        right_column_grid = QGridLayout()
        right_column_grid.setSpacing(10)
        right_column_grid.setColumnStretch(2,1)
        settings_icon = get_icon("preferences-configure", "configure", QStyle.SP_DesktopIcon)

        right_column_grid.addWidget(QLabel("Document Size:"), 0, 0, Qt.AlignRight)
        self.mo_doc_size_combo = QComboBox()
        paper_sizes = ["Letter (8 1/2 x 11 in)", "A4 (210 x 297 mm)", "Legal (8 1/2 x 14 in)"]
        self.mo_doc_size_combo.addItems(paper_sizes)
        a4_text = "A4 (210 x 297 mm)"
        if a4_text in paper_sizes:
            self.mo_doc_size_combo.setCurrentText(a4_text)
        right_column_grid.addWidget(self.mo_doc_size_combo, 0, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Output Paper:"), 1, 0, Qt.AlignRight)
        self.output_paper_combo = QComboBox()
        self.output_paper_combo.addItems(["Same as Document Size", "Letter (8 1/2 x 11 in)", "A4 (210 x 297 mm)"])
        right_column_grid.addWidget(self.output_paper_combo, 1, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Reduce/Enlarge Document:"), 2, 0, Qt.AlignTop | Qt.AlignRight)
        reduce_enlarge_layout = QVBoxLayout()
        self.fit_to_page_checkbox = QCheckBox("Fit to Page")
        zoom_layout = QHBoxLayout()
        self.zoom_to_checkbox = QCheckBox("Zoom to")
        self.zoom_spinbox = QSpinBox()
        self.zoom_spinbox.setSuffix(" %")
        self.zoom_spinbox.setRange(10, 400)
        self.zoom_spinbox.setValue(100)
        self.zoom_spinbox.setEnabled(False)
        self.zoom_to_checkbox.toggled.connect(self.zoom_spinbox.setEnabled)
        def fit_page_toggled(checked):
            if checked:
                self.zoom_to_checkbox.setChecked(False)
                self.zoom_to_checkbox.setEnabled(False)
            else:
                self.zoom_to_checkbox.setEnabled(True)
        self.fit_to_page_checkbox.toggled.connect(fit_page_toggled)
        zoom_layout.addWidget(self.zoom_to_checkbox)
        zoom_layout.addWidget(self.zoom_spinbox)
        zoom_layout.addStretch()
        reduce_enlarge_layout.addWidget(self.fit_to_page_checkbox)
        reduce_enlarge_layout.addLayout(zoom_layout)
        right_column_grid.addLayout(reduce_enlarge_layout, 2, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Color Correction:"), 3, 0, Qt.AlignTop | Qt.AlignRight)
        color_correction_layout = QVBoxLayout()
        self.cc_auto_radio = QRadioButton("Automatic")
        self.cc_auto_radio.setChecked(True)
        self.cc_custom_radio = QRadioButton("Custom")
        advanced_cc_icon = get_icon("color-management", "preferences-color", QStyle.SP_CustomBase)
        self.cc_advanced_button = QPushButton(advanced_cc_icon,"Advanced...")
        self.cc_advanced_button.setEnabled(False)
        image_options_icon = get_icon("image-sharpen", "transform-crop-and-resize", QStyle.SP_CustomBase)
        self.cc_image_options_button = QPushButton(image_options_icon, "Image Options...")
        def update_advanced_button_status_cc():
            self.cc_advanced_button.setEnabled(self.cc_custom_radio.isChecked())
        self.cc_auto_radio.toggled.connect(update_advanced_button_status_cc)
        self.cc_custom_radio.toggled.connect(update_advanced_button_status_cc)
        custom_cc_layout = QHBoxLayout()
        custom_cc_layout.addWidget(self.cc_custom_radio)
        custom_cc_layout.addWidget(self.cc_advanced_button)
        custom_cc_layout.addStretch()
        color_correction_layout.addWidget(self.cc_auto_radio)
        color_correction_layout.addLayout(custom_cc_layout)
        color_correction_layout.addWidget(self.cc_image_options_button, 0, Qt.AlignLeft)
        right_column_grid.addLayout(color_correction_layout, 3, 1, 1, 2)

        right_column_grid.addWidget(QLabel("Watermark:"), 4, 0, Qt.AlignRight)
        self.watermark_combo = QComboBox()
        self.watermark_combo.addItems(["None", "CONFIDENTIAL", "DRAFT", "Add/Delete..."])
        watermark_add_icon = get_icon("document-edit", "draw-text", QStyle.SP_FileLinkIcon)
        self.watermark_add_delete_button = QPushButton(watermark_add_icon,"Add/Delete...")
        self.watermark_settings_button = QPushButton(settings_icon, "Settings...")
        self.watermark_settings_button.setEnabled(False)
        def watermark_changed(text):
            is_none = (text == "None")
            self.watermark_settings_button.setEnabled(not is_none)
            if text == "Add/Delete...":
                print("Add/Delete Watermark action from combobox (placeholder)")
        self.watermark_combo.currentTextChanged.connect(watermark_changed)
        watermark_controls_layout = QHBoxLayout()
        watermark_controls_layout.addWidget(self.watermark_combo,1)
        watermark_controls_layout.addWidget(self.watermark_add_delete_button)
        watermark_controls_layout.addWidget(self.watermark_settings_button)
        right_column_grid.addLayout(watermark_controls_layout, 4, 1, 1, 2)

        self.header_footer_checkbox = QCheckBox("Header/Footer")
        header_footer_icon = get_icon("insert-header-footer", "format-header-symbolic", QStyle.SP_FileDialogDetailedView)
        self.header_footer_settings_button = QPushButton(header_footer_icon, "Settings...")
        self.header_footer_settings_button.setEnabled(False)
        self.header_footer_checkbox.toggled.connect(self.header_footer_settings_button.setEnabled)
        header_footer_layout = QHBoxLayout()
        header_footer_layout.addWidget(self.header_footer_checkbox)
        header_footer_layout.addWidget(self.header_footer_settings_button)
        header_footer_layout.addStretch()
        right_column_grid.addLayout(header_footer_layout, 5, 1, 1, 2)

        additional_settings_group = QGroupBox("Additional Settings")
        additional_settings_layout = QVBoxLayout()
        self.rotate_checkbox = QCheckBox("Rotate 180°")
        self.high_speed_checkbox = QCheckBox("High Speed")
        self.mirror_image_checkbox = QCheckBox("Mirror Image")
        additional_settings_layout.addWidget(self.rotate_checkbox)
        additional_settings_layout.addWidget(self.high_speed_checkbox)
        additional_settings_layout.addWidget(self.mirror_image_checkbox)
        additional_settings_group.setLayout(additional_settings_layout)
        right_column_grid.addWidget(additional_settings_group, 6, 1, 1, 2)
        right_column_grid.setRowStretch(7, 1)
        right_column_wrapper.addLayout(right_column_grid)
        right_column_wrapper.addStretch(1)

        show_settings_icon_more = get_icon("document-properties", "preferences-system", QStyle.SP_DialogApplyButton)
        show_settings_button_more = QPushButton(show_settings_icon_more, "Show Settings")
        show_settings_layout_more = QHBoxLayout()
        show_settings_layout_more.addStretch(1)
        show_settings_layout_more.addWidget(show_settings_button_more)
        right_column_wrapper.addLayout(show_settings_layout_more)
        more_options_tab_layout.addLayout(right_column_wrapper, 2)
        
    def _create_maintenance_item(self, icon_placeholder_texts_or_qicon, title_text, description_text, icon_size=QSize(32,32)):
        item_frame = QFrame()
        item_frame.setFrameShape(QFrame.StyledPanel)
        item_frame.setObjectName("MaintenanceItemFrame")

        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(10, 8, 10, 8) 
        item_layout.setSpacing(10)

        icon_label = QLabel()
        if isinstance(icon_placeholder_texts_or_qicon, QIcon): 
            item_icon = icon_placeholder_texts_or_qicon
        else: 
             item_icon = create_placeholder_icon_with_text(icon_placeholder_texts_or_qicon, icon_size=icon_size)

        if not item_icon.isNull():
            icon_pixmap = item_icon.pixmap(icon_size)
            if not icon_pixmap.isNull():
                icon_label.setPixmap(icon_pixmap)
            else:
                icon_label.setText("[PXM Gagal]")
        else:
            icon_label.setText("[IKON Gagal]")
        
        icon_label.setFixedSize(icon_size.width() + 4, icon_size.height() + 4) 
        icon_label.setAlignment(Qt.AlignCenter)
        item_layout.addWidget(icon_label, 0, Qt.AlignTop)

        text_content_label = QLabel()
        html_text = f"<b>{title_text}</b>&nbsp;&nbsp;{description_text}"
        text_content_label.setText(html_text)
        text_content_label.setTextFormat(Qt.RichText) 
        text_content_label.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        
        item_layout.addWidget(text_content_label, 1) 
                                                     
        return item_frame

    def setup_maintenance_tab(self):
        main_layout = QVBoxLayout(self.tab_maintenance)
        main_layout.setContentsMargins(10, 10, 10, 10) 
        main_layout.setSpacing(5) 
        main_layout.setAlignment(Qt.AlignTop)

        maintenance_items_data = [
            {"icon_text": ["CLN", "💧"], "title": "Cleaning", 
             "desc": "Removes unwanted marks and lines from your printed output."},
            {"icon_text": ["DEEP", "CLN", "💧💧"], "title": "Deep Cleaning", 
             "desc": "Resolves stubborn nozzle blockages that standard cleaning cannot fix."},
            {"icon_text": ["A|A", "↔️"], "title": "Print Head Alignment", 
             "desc": "Corrects color and line misalignments by performing print head alignment."},
            {"icon_text": ["|||", "---", "|||"], "title": "Nozzle Check", 
             "desc": "Prints a test pattern to determine if any print head nozzles are clogged."},
        ]

        ink_cart_icon_theme = get_icon("color-palette", "preferences-desktop-color", QStyle.SP_CustomBase)
        if ink_cart_icon_theme.isNull():
            ink_cart_icon_repr = create_placeholder_icon_with_text(["INK"], icon_size=QSize(32,32))
        else:
            ink_cart_icon_repr = ink_cart_icon_theme
        
        maintenance_items_data.append(
            {"icon_text": ink_cart_icon_repr, "title": "Ink Cartridge Settings", 
             "desc": "Allows you to configure settings related to your ink cartridges for printing."}
        )

        for item_data in maintenance_items_data:
            item_widget = self._create_maintenance_item( 
                item_data["icon_text"], 
                item_data["title"], 
                item_data["desc"],
                icon_size=QSize(32,32) 
            )
            main_layout.addWidget(item_widget)

        main_layout.addStretch(1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    QIcon.setThemeName("breeze")
    print(f"INFO: Mencoba mengatur tema ikon ke 'breeze'.")
    print(f"--- Diagnostik Ikon ---")
    print(f"Nama Tema Qt Saat Ini (setelah setThemeName): {QIcon.themeName()}")
    print(f"Path Pencarian Tema Qt: {QIcon.themeSearchPaths()}")
    print(f"----------------------")
    
    # app.setStyleSheet("""
    #     QFrame#MaintenanceItemFrame {
    #         border: 1px solid #e0e0e0; 
    #         border-radius: 3px;        
    #         background-color: #f9f9f9; 
    #         padding: 5px;          
    #         margin-bottom: 2px;        
    #     }
    #     QFrame#MaintenanceItemFrame:hover {
    #         background-color: #eef4ff; 
    #     }
    # """)

    # app.setStyle("Fusion") 
    dialog = LinuxPrinterPreferencesDialog()
    dialog.show()
    sys.exit(app.exec_())