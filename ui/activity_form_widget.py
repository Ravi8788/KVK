from math import ceil
from datetime import timedelta
from uuid import uuid4

from PyQt5.QtCore import QDate, QRegExp, Qt
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtWidgets import (
    QButtonGroup,
    QCompleter,
    QComboBox,
    QDateEdit,
    QDialog,
    QDialogButtonBox,
    QFormLayout,
    QFrame,
    QGridLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QScrollArea,
    QRadioButton,
    QSizePolicy,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from services.activity_service import ActivityService


MH_DISTRICT_TEHSILS = {
    "Ahmednagar": ["Akole", "Jamkhed", "Karjat", "Kopargaon", "Nagar", "Nevasa", "Parner", "Pathardi", "Rahata", "Rahuri", "Sangamner", "Shevgaon", "Shrigonda", "Shrirampur"],
    "Akola": ["Akola", "Akot", "Balapur", "Barshitakli", "Murtijapur", "Patur", "Telhara"],
    "Amravati": ["Achalpur", "Amravati", "Anjangaon Surji", "Bhatkuli", "Chandur Railway", "Chandurbazar", "Daryapur", "Dhamangaon Railway", "Dharni", "Morshi", "Nandgaon Khandeshwar", "Teosa", "Warud"],
    "Beed": ["Ambejogai", "Ashti", "Beed", "Dharur", "Georai", "Kaij", "Majalgaon", "Parli", "Patoda", "Shirur (Kasar)", "Wadwani"],
    "Bhandara": ["Bhandara", "Lakhandur", "Lakhani", "Mohadi", "Pauni", "Sakoli", "Tumsar"],
    "Buldhana": ["Buldana", "Chikhli", "Deulgaon Raja", "Jalgaon Jamod", "Khamgaon", "Lonar", "Malkapur", "Mehkar", "Motala", "Nandura", "Sangrampur", "Shegaon", "Sindkhed Raja"],
    "Chandrapur": ["Ballarpur", "Bhadravati", "Brahmapuri", "Chandrapur", "Chimur", "Gondpipri", "Jiwati", "Korpana", "Mul", "Nagbhid", "Pombhurna", "Rajura", "Sawali", "Sindewahi", "Warora"],
    "Dhule": ["Dhule", "Sakri", "Shirpur", "Sindkhede"],
    "Gadchiroli": ["Aheri", "Armori", "Bhamragad", "Chamorshi", "Desaiganj", "Dhanora", "Etapalli", "Gadchiroli", "Kurkheda", "Mulchera", "Sironcha"],
    "Gondia": ["Amgaon", "Arjuni Morgaon", "Deori", "Gondia", "Goregaon", "Sadak Arjuni", "Salekasa", "Tirora"],
    "Hingoli": ["Aundha Nagnath", "Basmath", "Hingoli", "Kalamnuri", "Sengaon"],
    "Jalgaon": ["Amalner", "Bhadgaon", "Bhusawal", "Bodwad", "Chalisgaon", "Chopda", "Dharangaon", "Erandol", "Jalgaon", "Jamner", "Muktainagar", "Pachora", "Parola", "Raver", "Yawal"],
    "Jalna": ["Ambad", "Badnapur", "Bhokardan", "Ghansawangi", "Jafrabad", "Jalna", "Mantha", "Partur"],
    "Kolhapur": ["Ajra", "Bavda", "Bhudargad", "Chandgad", "Gadhinglaj", "Hatkanangale", "Kagal", "Karvir", "Panhala", "Radhanagari", "Shahuwadi", "Shirol"],
    "Latur": ["Ahmedpur", "Ausa", "Chakur", "Deoni", "Jalkot", "Latur", "Nilanga", "Renapur", "Shirur-Anantpal", "Udgir"],
    "Mumbai City": ["Mumbai"],
    "Mumbai Suburban": ["Andheri", "Borivali", "Kurla"],
    "Nagpur": ["Bhiwapur", "Hingna", "Kalameshwar", "Kamptee", "Katol", "Kuhi", "Mauda", "Nagpur (Rural)", "Narkhed", "Parseoni", "Ramtek", "Savner", "Umred"],
    "Nanded": ["Ardhapur", "Bhokar", "Biloli", "Deglur", "Dharmabad", "Hadgaon", "Himayatnagar", "Kandhar", "Kinwat", "Loha", "Mahur", "Mudkhed", "Mukhed", "Naigaon", "Nanded", "Umri"],
    "Nandurbar": ["Akkalkuwa", "Akrani", "Nandurbar", "Nawapur", "Shahada", "Taloda"],
    "Nashik": ["Baglan", "Chandwad", "Deola", "Dindori", "Igatpuri", "Kalwan", "Malegaon", "Nandgaon", "Nashik", "Niphad", "Peint", "Sinnar", "Surgana", "Trimbakeshwar", "Yevla"],
    "Osmanabad": ["Bhoom", "Kalamb", "Lohara", "Osmanabad", "Paranda", "Tuljapur", "Umarga", "Washi"],
    "Palghar": ["Dahanu", "Jawhar", "Mokhada", "Palghar", "Talasari", "Vada", "Vasai", "Vikramgad"],
    "Parbhani": ["Gangakhed", "Jintur", "Manwath", "Palam", "Parbhani", "Pathri", "Purna", "Selu", "Sonpeth"],
    "Pune": ["Ambegaon", "Baramati", "Bhor", "Daund", "Haveli", "Indapur", "Junnar", "Khed", "Maval", "Mulshi", "Purandar", "Shirur", "Velhe"],
    "Raigad": ["Alibag", "Karjat", "Khalapur", "Mahad", "Mangaon", "Mhasla", "Murud", "Panvel", "Pen", "Poladpur", "Roha", "Shrivardhan", "Sudhagad", "Tala", "Uran"],
    "Ratnagiri": ["Chiplun", "Dapoli", "Guhagar", "Khed", "Lanja", "Mandangad", "Rajapur", "Ratnagiri", "Sangameshwar"],
    "Sangli": ["Atpadi", "Jat", "Kadegaon", "Kavathemahankal", "Khanapur", "Miraj", "Palus", "Shirala", "Tasgaon", "Walwa"],
    "Satara": ["Jaoli", "Karad", "Khandala", "Khatav", "Koregaon", "Mahabaleshwar", "Man", "Patan", "Phaltan", "Satara", "Wai"],
    "Sindhudurg": ["Devgad", "Dodamarg", "Kankavli", "Kudal", "Malvan", "Sawantwadi", "Vaibhavwadi", "Vengurla"],
    "Solapur": ["Akkalkot", "Barshi", "Karmala", "Madha", "Malshiras", "Mangalwedha", "Mohol", "North Solapur", "Pandharpur", "Sangole", "South Solapur"],
    "Thane": ["Ambarnath", "Bhiwandi", "Kalyan", "Murbad", "Shahapur", "Thane"],
    "Wardha": ["Arvi", "Ashti", "Deoli", "Hinganghat", "Karanja", "Samudrapur", "Seloo", "Wardha"],
    "Washim": ["Karanja", "Malegaon", "Mangrulpir", "Manora", "Risod", "Washim"],
    "Yavatmal": ["Arni", "Babulgaon", "Darwha", "Digras", "Ghatanji", "Kalamb", "Kelapur", "Mahagaon", "Maregaon", "Ner", "Pandharkawada", "Pusad", "Ralegaon", "Umarkhed", "Wani", "Yavatmal"],
    "Aurangabad": ["Aurangabad", "Gangapur", "Kannad", "Khuldabad", "Paithan", "Phulambri", "Sillod", "Soegaon", "Vaijapur"],
    "Dharashiv": ["Bhoom", "Kalamb", "Lohara", "Paranda", "Tuljapur", "Umarga", "Washi", "Dharashiv"],
}


class ActivityFormWidget(QWidget):
    """Reusable form and table widget for each activity module."""

    def __init__(self, module_name: str, current_user, read_only: bool = False, on_data_changed=None):
        super().__init__()
        self.module_name = module_name
        self.current_user = current_user
        self.read_only = read_only
        self.on_data_changed = on_data_changed
        self.departments = ActivityService.list_departments()
        self.villages = ActivityService.list_villages()
        self.activity_type_presets = {
            "On Farm Testing (OFT)": ["Assessment"],
            "Front Line Demonstrations (FLD)": ["Demonstration", "Field Day", "Follow-up"],
            "Training Programmes": ["Training Session", "Workshop", "Awareness"],
            "Vocational Training Programmes": ["Skill Training", "Hands-on Training"],
            "Extension Activities": [
                "Scientists Visit To Farmers Field",
                "Group Meeting",
                "Diagnostic Visit",
                "Lecture Delivered As Resource Person",
                "Field Day",
                "Method Demonstration",
                "Participated In Meeting",
                "Exposure Visit",
                "Kisan Mela",
                "Mahila Melava",
                "Animal Health Camp",
                "Farmer Seminar",
                "Kisan Goshti",
                "World Soil Day",
                "Swachata Pakhawada",
                "Other All Activities",
            ],
            "Other Extension Activities": [
                "Radio Talk",
                "News Paper Coverage",
                "Popular Article",
                "Extension Literature",
                "TV Shows",
            ],
            "Visitor Farmers": ["Visitor Entry", "Consultation"],
        }
        self.selected_activity_id = None
        self.oft_selected_activity_ids = []
        self.oft_selected_batch_key = ""
        self._table_row_records = []
        self.current_page = 1
        self.page_size = 100
        self.total_records = 0
        self.oft_farmer_forms = []
        self.training_farmer_forms = []
        self.current_farmer_index = 0
        self.current_training_farmer_index = 0

        self._build_ui()
        self._apply_role_permissions()
        self._load_table()

    def _is_oft_style_module(self) -> bool:
        return self.module_name in ["On Farm Testing (OFT)", "Front Line Demonstrations (FLD)"]

    def _notify_data_changed(self) -> None:
        if callable(self.on_data_changed):
            self.on_data_changed()

    def _build_ui(self) -> None:
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.setSpacing(0)

        self.page_scroll_area = QScrollArea()
        self.page_scroll_area.setWidgetResizable(True)
        self.page_scroll_area.setFrameShape(QFrame.NoFrame)
        self.page_scroll_area.verticalScrollBar().setSingleStep(18)

        page_content = QWidget()
        root = QVBoxLayout(page_content)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        self.page_scroll_area.setWidget(page_content)
        page_layout.addWidget(self.page_scroll_area)

        header = QLabel(self.module_name)
        header.setObjectName("CardTitle")
        root.addWidget(header)

        self.mode_label = QLabel("")
        root.addWidget(self.mode_label)

        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            self._build_training_ui(root)
            return

        if self.module_name == "Extension Activities":
            self._build_extension_ui(root)
            return

        if self.module_name == "Other Extension Activities":
            self._build_other_extension_ui(root)
            return

        if self._is_oft_style_module():
            self._build_oft_ui(root)
            return

        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QGridLayout(form_card)

        form_left = QFormLayout()
        self.farmer_name_input = QLineEdit()
        self.village_input = QComboBox()
        self.village_input.setEditable(True)
        self.village_input.setInsertPolicy(QComboBox.NoInsert)
        self.village_input.addItems(self.villages)
        self.village_input.setCurrentIndex(-1)
        self.village_input.lineEdit().setPlaceholderText("Select or type village")
        self._configure_searchable_combo(self.village_input)
        self.contact_input = QLineEdit()
        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.tehsil_input = QComboBox()
        self.district_input = QComboBox()
        self.scientist_input = QLineEdit()
        self._configure_mobile_input(self.contact_input)

        self.district_input.setEditable(True)
        self.tehsil_input.setEditable(True)

        self.district_input.addItem("Select District", None)
        for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
            self.district_input.addItem(district_name, district_name)
        self.district_input.lineEdit().setPlaceholderText("Select or type district")
        self._configure_searchable_combo(self.district_input)
        self.tehsil_input.addItem("Select Tehsil", None)
        self.tehsil_input.setEnabled(False)
        self.tehsil_input.lineEdit().setPlaceholderText("Select or type tehsil")
        self._configure_searchable_combo(self.tehsil_input)

        form_right = QFormLayout()
        self.department_combo = QComboBox()
        if self.module_name in {"On Farm Testing (OFT)", "Training Programmes", "Vocational Training Programmes"}:
            self.department_combo.addItem("Select Department", None)
        for dept in self.departments:
            self.department_combo.addItem(dept.name, dept.id)

        self.season_combo = QComboBox()
        self.season_combo.addItems(["Kharif", "Rabi"])

        self.activity_type_input = QComboBox()
        self.training_type_combo = QComboBox()
        self.training_type_combo.addItems(["Regular", "Vocational", "Sponsored"])
        if self.module_name == "Vocational Training Programmes":
            vocational_index = self.training_type_combo.findText("Vocational")
            if vocational_index >= 0:
                self.training_type_combo.setCurrentIndex(vocational_index)

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())

        self.clientele_input = QLineEdit()
        self.thematic_area_input = QLineEdit()

        self.venue_on_radio = QRadioButton("On")
        self.venue_off_radio = QRadioButton("Off")
        self.venue_on_radio.setChecked(True)

        self.venue_offline_village_input = QLineEdit()
        self.venue_offline_district_input = QComboBox()
        self.venue_offline_taluka_input = QComboBox()
        self.venue_offline_village_input.setPlaceholderText("Village name")
        self.venue_offline_district_input.addItem("Select District", None)
        for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
            self.venue_offline_district_input.addItem(district_name, district_name)
        self.venue_offline_taluka_input.addItem("Select Taluka", None)

        self.training_farmer_count_input = QLineEdit()
        self.training_farmer_count_input.setPlaceholderText("Enter number of farmers")
        self.training_farmer_count_input.setValidator(QRegExpValidator(QRegExp(r"\d{0,6}"), self.training_farmer_count_input))

        self.description_input = QTextEdit()
        self.remarks_input = QTextEdit()
        self.description_input.setFixedHeight(65)
        self.remarks_input.setFixedHeight(65)

        training_title_label = "Training Title*" if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else "Farmer Name*"
        venue_label = "Venue*" if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else "Village*"
        contact_label = "Contact Number*" if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else "Contact Number*"
        description_label_text = "Training Description" if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else "Description"

        fld_description_widget = self.description_input
        fld_description_label = description_label_text
        if self.module_name == "Front Line Demonstrations (FLD)":
            self.description_input.hide()
            self.fld_technical_group = QButtonGroup(self)
            self.fld_t1_radio = QRadioButton("T1")
            self.fld_t2_radio = QRadioButton("T2")
            self.fld_t3_radio = QRadioButton("T3")
            self.fld_technical_group.addButton(self.fld_t1_radio)
            self.fld_technical_group.addButton(self.fld_t2_radio)
            self.fld_technical_group.addButton(self.fld_t3_radio)

            fld_row = QWidget()
            fld_row_layout = QHBoxLayout(fld_row)
            fld_row_layout.setContentsMargins(0, 0, 0, 0)
            fld_row_layout.setSpacing(18)
            fld_row_layout.addWidget(self.fld_t1_radio)
            fld_row_layout.addWidget(self.fld_t2_radio)
            fld_row_layout.addWidget(self.fld_t3_radio)
            fld_row_layout.addStretch(1)

            self.fld_t1_radio.toggled.connect(lambda checked: self.description_input.setPlainText("T1") if checked else None)
            self.fld_t2_radio.toggled.connect(lambda checked: self.description_input.setPlainText("T2") if checked else None)
            self.fld_t3_radio.toggled.connect(lambda checked: self.description_input.setPlainText("T3") if checked else None)

            fld_description_widget = fld_row
            fld_description_label = "Technical Assessment*"

        self.department_label = QLabel("Department*")
        self.season_label = QLabel("Season*")
        self.activity_type_label = QLabel("Activity Type*")

        if self.module_name == "Visitor Farmers":
            form_left.addRow("Date*", self.date_input)
            form_left.addRow("Name of Farmer*", self.farmer_name_input)
            form_left.addRow("District*", self.district_input)
            form_left.addRow("Tehsil*", self.tehsil_input)
            form_left.addRow("Village*", self.village_input)

            form_left.addRow("Mobile No.*", self.contact_input)
            form_left.addRow("Name of Scientist*", self.scientist_input)
            self.department_label.setText("Name of Dept.*")
            form_left.addRow(self.department_label, self.department_combo)
            self.activity_type_label.setText("Purpose*")
            form_left.addRow(self.activity_type_label, self.activity_type_input)
            
            # Hide season and description/remarks fields entirely for Visitor Farmers
            self.season_label.hide()
            self.season_combo.hide()
            self.description_input.hide()
            self.remarks_input.hide()
        else:
            form_left.addRow(training_title_label, self.farmer_name_input)
            form_left.addRow(venue_label, self.village_input)
            form_left.addRow(contact_label, self.contact_input)
            form_left.addRow("Start Date*", self.date_input)

            form_right.addRow(self.department_label, self.department_combo)
            form_right.addRow("Training Type*", self.training_type_combo)
            form_right.addRow("End Date*", self.end_date_input)
            form_right.addRow("Clientele*", self.clientele_input)
            form_right.addRow("Thematic Area*", self.thematic_area_input)

            venue_mode_widget = QWidget()
            venue_mode_layout = QHBoxLayout(venue_mode_widget)
            venue_mode_layout.setContentsMargins(0, 0, 0, 0)
            venue_mode_layout.setSpacing(8)
            venue_mode_layout.addWidget(self.venue_on_radio)
            venue_mode_layout.addWidget(self.venue_off_radio)
            venue_mode_layout.addStretch(1)
            form_right.addRow("Venue Mode", venue_mode_widget)

            form_right.addRow("Venue*", self.village_input)

            self.venue_offline_widget = QWidget()
            self.venue_offline_widget.setVisible(False)
            venue_offline_layout = QFormLayout(self.venue_offline_widget)
            venue_offline_layout.addRow("Village*", self.venue_offline_village_input)
            venue_offline_layout.addRow("Taluka*", self.venue_offline_taluka_input)
            venue_offline_layout.addRow("District*", self.venue_offline_district_input)
            form_right.addRow(self.venue_offline_widget)

            form_right.addRow("No. of Farmers*", self.training_farmer_count_input)
            form_right.addRow(fld_description_label, fld_description_widget)
            form_right.addRow("Remarks", self.remarks_input)

        if self.module_name == "Front Line Demonstrations (FLD)":
            self.activity_type_label.hide()
            self.activity_type_input.hide()

        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            self.season_label.hide()
            self.season_combo.hide()
            self.activity_type_label.hide()
            self.activity_type_input.hide()

        if self.module_name == "Extension Activities":
            self.department_label.hide()
            self.department_combo.hide()
            self.season_label.hide()
            self.season_combo.hide()

            # Extension Activities use fixed internal department value.
            ext_idx = self.department_combo.findText("Agricultural Extension")
            if ext_idx >= 0:
                self.department_combo.setCurrentIndex(ext_idx)

        if self.module_name == "Other Extension Activities":
            self.department_label.hide()
            self.department_combo.hide()
            self.season_label.hide()
            self.season_combo.hide()

            # Other Extension Activities use fixed internal department value.
            ext_idx = self.department_combo.findText("Agricultural Extension")
            if ext_idx >= 0:
                self.department_combo.setCurrentIndex(ext_idx)

        self.department_combo.currentIndexChanged.connect(self._refresh_activity_type_options)
        self.activity_type_input.currentIndexChanged.connect(self._refresh_season_options)
        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            self.venue_on_radio.toggled.connect(self._update_training_venue_mode)
            self.venue_off_radio.toggled.connect(self._update_training_venue_mode)
        if self.module_name == "Visitor Farmers":
            self.district_input.currentIndexChanged.connect(self._on_district_changed)
            self.tehsil_input.currentIndexChanged.connect(self._on_tehsil_changed)
        self._refresh_activity_type_options()
        self._refresh_season_options()

        if self.module_name == "Visitor Farmers":
            form_layout.addLayout(form_left, 0, 0)
        else:
            form_layout.addLayout(form_left, 0, 0)
            form_layout.addLayout(form_right, 0, 1)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")

        self.save_btn.clicked.connect(self._save_record)
        self.reset_btn.clicked.connect(self._reset_form)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch(1)
        if self.module_name == "Visitor Farmers":
            form_layout.addLayout(btn_row, 1, 0)
        else:
            form_layout.addLayout(btn_row, 1, 0, 1, 2)

        root.addWidget(form_card)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)

        filters_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search farmer, village, contact, activity...")

        self.filter_department_combo = QComboBox()
        self.filter_department_combo.addItem("All Departments", None)
        for dept in self.departments:
            self.filter_department_combo.addItem(dept.name, dept.id)

        self.filter_season_combo = QComboBox()
        self.filter_season_combo.addItems(["All", "Kharif", "Rabi"])

        self.filter_date_mode_combo = QComboBox()
        self.filter_date_mode_combo.addItems(["All Dates", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"])
        self.filter_date_mode_combo.currentTextChanged.connect(self._on_filter_date_mode_changed)

        self.filter_from_date = QDateEdit()
        self.filter_from_date.setCalendarPopup(True)
        self.filter_from_date.setDate(QDate.currentDate().addDays(-30))
        self.filter_to_date = QDateEdit()
        self.filter_to_date.setCalendarPopup(True)
        self.filter_to_date.setDate(QDate.currentDate())
        self.filter_from_date.hide()
        self.filter_to_date.hide()

        apply_filter_btn = QPushButton("Apply Filter")
        clear_filter_btn = QPushButton("Clear")
        apply_filter_btn.clicked.connect(self._apply_filters)
        clear_filter_btn.clicked.connect(self._clear_filters)

        filters_row.addWidget(self.search_input)
        filters_row.addWidget(self.filter_department_combo)
        filters_row.addWidget(self.filter_season_combo)
        filters_row.addWidget(self.filter_date_mode_combo)
        filters_row.addWidget(self.filter_from_date)
        filters_row.addWidget(self.filter_to_date)
        filters_row.addWidget(apply_filter_btn)
        filters_row.addWidget(clear_filter_btn)

        table_layout.addLayout(filters_row)

        # Visitor Farmers uses 11 columns, OFT uses 10 columns, other modules use 10
        if self.module_name == "Visitor Farmers":
            col_count = 12
        elif self.module_name == "On Farm Testing (OFT)":
            col_count = 10
        else:
            col_count = 10
        self.table = QTableWidget(0, col_count)
        
        if self.module_name == "Visitor Farmers":
            headers = [
                "Sr No",
                "Farmer",
                "Farmer ID",
                "Village",
                "Contact",
                "Date",
                "Department",
                "District",
                "Tehsil",
                "Activity",
                "Description",
                "Remarks",
            ]
        elif self.module_name == "On Farm Testing (OFT)":
            headers = [
                "Sr No",
                "Date",
                "Title of OFT",
                "Crop Variety",
                "No. of Farmers",
                "Technical Assessment",
                "Area",
                "Department",
                "Activity",
                "Season",
            ]
        else:
            headers = [
                "Sr No",
                "Farmer",
                "Village",
                "Contact",
                "Date",
                "Department",
                "Season",
                "Activity",
                "Description",
                "Remarks",
            ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self._on_row_selected)

        pager_row = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.table_edit_btn = None
        self.table_delete_btn = None
        
        if self.module_name in ("Front Line Demonstrations (FLD)", "Visitor Farmers"):
            self.table_edit_btn = QPushButton("Open Edit Dialog")
            self.table_delete_btn = QPushButton("Delete Selected")
            self.table_edit_btn.setEnabled(False)
            self.table_delete_btn.setEnabled(False)
            
            if self.module_name == "Front Line Demonstrations (FLD)":
                self.table_edit_btn.clicked.connect(self._open_fld_edit_dialog)
            else:  # Visitor Farmers
                self.table_edit_btn.clicked.connect(self._open_visitor_farmers_edit_dialog)
            
            self.table_delete_btn.clicked.connect(self._delete_record)
        
        self.page_label = QLabel("Page 1")

        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)

        pager_row.addWidget(self.prev_btn)
        pager_row.addWidget(self.next_btn)
        if self.table_edit_btn is not None:
            pager_row.addWidget(self.table_edit_btn)
            pager_row.addWidget(self.table_delete_btn)
        pager_row.addWidget(self.page_label)
        pager_row.addStretch(1)

        table_layout.addWidget(self.table)
        table_layout.addLayout(pager_row)

        root.addWidget(table_card)

    def _build_extension_ui(self, root: QVBoxLayout) -> None:
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)

        form = QFormLayout()
        self.activity_type_input = QComboBox()
        self.activity_type_input.addItem("Select Extension Activity", None)
        self.activity_type_input.addItems(self.activity_type_presets["Extension Activities"])
        self.activity_type_input.setEditable(False)
        form.addRow("Activity*", self.activity_type_input)

        self.extension_fields_widget = QWidget()
        self.extension_fields_widget.setVisible(False)
        fields_layout = QFormLayout(self.extension_fields_widget)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.extension_venue_input = QLineEdit()
        self.extension_location_input = QLineEdit()
        self.department_combo = QComboBox()
        self.department_combo.addItem("Select Department", None)
        for dept in self.departments:
            self.department_combo.addItem(dept.name, dept.id)
        ext_idx = self.department_combo.findText("Agricultural Extension")
        if ext_idx >= 0:
            self.department_combo.setCurrentIndex(ext_idx)

        self.extension_purpose_input = QTextEdit()
        self.extension_purpose_input.setFixedHeight(70)
        self.extension_farmer_count_input = QLineEdit()
        self.extension_farmer_count_input.setPlaceholderText("Enter number of farmers")
        self.extension_farmer_count_input.setValidator(QRegExpValidator(QRegExp(r"\d{0,6}"), self.extension_farmer_count_input))

        fields_layout.addRow("Date*", self.date_input)
        fields_layout.addRow("Venue*", self.extension_venue_input)
        fields_layout.addRow("Location*", self.extension_location_input)
        fields_layout.addRow("Department*", self.department_combo)
        fields_layout.addRow("Purpose of Visit*", self.extension_purpose_input)
        fields_layout.addRow("No. of Farmers*", self.extension_farmer_count_input)

        form.addRow(self.extension_fields_widget)
        form_layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")
        self.save_btn.clicked.connect(self._save_record)
        self.reset_btn.clicked.connect(self._reset_form)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch(1)
        form_layout.addLayout(btn_row)
        root.addWidget(form_card)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)

        filters_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search activity, venue, location, purpose...")
        self.filter_department_combo = QComboBox()
        self.filter_department_combo.addItem("All Departments", None)
        for dept in self.departments:
            self.filter_department_combo.addItem(dept.name, dept.id)
        self.filter_season_combo = QComboBox()
        self.filter_season_combo.addItems(["All", "Kharif", "Rabi"])
        self.filter_date_mode_combo = QComboBox()
        self.filter_date_mode_combo.addItems(["All Dates", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"])
        self.filter_date_mode_combo.currentTextChanged.connect(self._on_filter_date_mode_changed)
        self.filter_from_date = QDateEdit()
        self.filter_from_date.setCalendarPopup(True)
        self.filter_from_date.setDate(QDate.currentDate().addDays(-30))
        self.filter_to_date = QDateEdit()
        self.filter_to_date.setCalendarPopup(True)
        self.filter_to_date.setDate(QDate.currentDate())
        self.filter_from_date.hide()
        self.filter_to_date.hide()

        apply_filter_btn = QPushButton("Apply Filter")
        clear_filter_btn = QPushButton("Clear")
        apply_filter_btn.clicked.connect(self._apply_filters)
        clear_filter_btn.clicked.connect(self._clear_filters)

        filters_row.addWidget(self.search_input)
        filters_row.addWidget(self.filter_department_combo)
        filters_row.addWidget(self.filter_season_combo)
        filters_row.addWidget(self.filter_date_mode_combo)
        filters_row.addWidget(self.filter_from_date)
        filters_row.addWidget(self.filter_to_date)
        filters_row.addWidget(apply_filter_btn)
        filters_row.addWidget(clear_filter_btn)
        table_layout.addLayout(filters_row)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels([
            "Sr No",
            "Date",
            "Activity",
            "Venue",
            "Location",
            "Department",
            "Purpose of Visit",
            "No. of Farmers",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self._on_row_selected)
        table_layout.addWidget(self.table)

        pager_row = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page 1")
        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)
        pager_row.addWidget(self.prev_btn)
        pager_row.addWidget(self.next_btn)
        pager_row.addWidget(self.page_label)
        pager_row.addStretch(1)
        table_layout.addLayout(pager_row)
        root.addWidget(table_card)

        self.activity_type_input.currentIndexChanged.connect(self._on_extension_activity_changed)

    def _build_other_extension_ui(self, root: QVBoxLayout) -> None:
        form_card = QFrame()
        form_card.setObjectName("Card")
        form_layout = QVBoxLayout(form_card)

        form = QFormLayout()
        self.activity_type_input = QComboBox()
        self.activity_type_input.addItem("Select Other Extension Activity", None)
        self.activity_type_input.addItems(self.activity_type_presets["Other Extension Activities"])
        self.activity_type_input.setEditable(False)
        form.addRow("Activity*", self.activity_type_input)

        self.other_extension_fields_widget = QWidget()
        self.other_extension_fields_widget.setVisible(False)
        fields_layout = QFormLayout(self.other_extension_fields_widget)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.other_extension_title_input = QLineEdit()

        self.department_combo = QComboBox()
        self.department_combo.addItem("Select Department", None)
        for dept in self.departments:
            self.department_combo.addItem(dept.name, dept.id)
        ext_idx = self.department_combo.findText("Agricultural Extension")
        if ext_idx >= 0:
            self.department_combo.setCurrentIndex(ext_idx)

        fields_layout.addRow("Date*", self.date_input)
        fields_layout.addRow("Title of Show*", self.other_extension_title_input)
        form.addRow(self.other_extension_fields_widget)
        form_layout.addLayout(form)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")
        self.save_btn.clicked.connect(self._save_record)
        self.reset_btn.clicked.connect(self._reset_form)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch(1)
        form_layout.addLayout(btn_row)
        root.addWidget(form_card)

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)

        filters_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search activity or title...")
        self.filter_department_combo = QComboBox()
        self.filter_department_combo.addItem("All Departments", None)
        for dept in self.departments:
            self.filter_department_combo.addItem(dept.name, dept.id)
        self.filter_season_combo = QComboBox()
        self.filter_season_combo.addItems(["All", "Kharif", "Rabi"])
        self.filter_date_mode_combo = QComboBox()
        self.filter_date_mode_combo.addItems(["All Dates", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"])
        self.filter_date_mode_combo.currentTextChanged.connect(self._on_filter_date_mode_changed)
        self.filter_from_date = QDateEdit()
        self.filter_from_date.setCalendarPopup(True)
        self.filter_from_date.setDate(QDate.currentDate().addDays(-30))
        self.filter_to_date = QDateEdit()
        self.filter_to_date.setCalendarPopup(True)
        self.filter_to_date.setDate(QDate.currentDate())
        self.filter_from_date.hide()
        self.filter_to_date.hide()

        apply_filter_btn = QPushButton("Apply Filter")
        clear_filter_btn = QPushButton("Clear")
        apply_filter_btn.clicked.connect(self._apply_filters)
        clear_filter_btn.clicked.connect(self._clear_filters)

        filters_row.addWidget(self.search_input)
        filters_row.addWidget(self.filter_department_combo)
        filters_row.addWidget(self.filter_season_combo)
        filters_row.addWidget(self.filter_date_mode_combo)
        filters_row.addWidget(self.filter_from_date)
        filters_row.addWidget(self.filter_to_date)
        filters_row.addWidget(apply_filter_btn)
        filters_row.addWidget(clear_filter_btn)
        table_layout.addLayout(filters_row)

        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels([
            "Sr No",
            "Date",
            "Activity",
            "Title of Show",
        ])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self._on_row_selected)
        table_layout.addWidget(self.table)

        pager_row = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page 1")
        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)
        pager_row.addWidget(self.prev_btn)
        pager_row.addWidget(self.next_btn)
        pager_row.addWidget(self.page_label)
        pager_row.addStretch(1)
        table_layout.addLayout(pager_row)
        root.addWidget(table_card)

        self.activity_type_input.currentIndexChanged.connect(self._on_other_extension_activity_changed)

    def _build_oft_ui(self, root: QVBoxLayout) -> None:
        module_short = "OFT" if self.module_name == "On Farm Testing (OFT)" else "FLD"
        selection_card = QFrame()
        selection_card.setObjectName("Card")
        selection_layout = QGridLayout(selection_card)
        selection_layout.setHorizontalSpacing(12)
        selection_layout.setVerticalSpacing(8)

        self.department_combo = QComboBox()
        self.department_combo.addItem("Select Department", None)
        for dept in self.departments:
            if dept.name.strip().lower() == "agricultural extension":
                continue
            self.department_combo.addItem(dept.name, dept.id)

        self.activity_type_input = QComboBox()
        self.activity_type_input.addItem("Select Activity Type")

        self.season_label = QLabel("Season*")
        self.season_combo = QComboBox()
        self.season_combo.addItems(["Select Season", "Kharif", "Rabi"])

        selection_layout.addWidget(QLabel("Department*"), 0, 0)
        selection_layout.addWidget(self.department_combo, 0, 1)
        selection_layout.addWidget(QLabel("Activity Type*"), 0, 2)
        selection_layout.addWidget(self.activity_type_input, 0, 3)
        selection_layout.addWidget(self.season_label, 0, 4)
        selection_layout.addWidget(self.season_combo, 0, 5)
        selection_layout.setColumnStretch(1, 1)
        selection_layout.setColumnStretch(3, 1)
        selection_layout.setColumnStretch(5, 1)

        self.department_combo.currentIndexChanged.connect(self._refresh_activity_type_options)
        self.activity_type_input.currentIndexChanged.connect(self._update_oft_form_visibility)
        self.season_combo.currentIndexChanged.connect(self._update_oft_form_visibility)

        root.addWidget(selection_card)

        form_card = QFrame()
        form_card.setObjectName("Card")
        self.oft_data_card = form_card
        form_layout = QFormLayout(form_card)
        form_layout.setHorizontalSpacing(12)
        form_layout.setVerticalSpacing(10)
        form_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())

        self.farmer_name_input = QLineEdit()
        self.farmer_name_input.setPlaceholderText("Enter OFT title")
        self.farmer_name_input.setMinimumHeight(34)

        self.village_input = QLineEdit()
        self.village_input.setPlaceholderText("Enter crop variety")
        self.village_input.setMinimumHeight(34)

        self.contact_input = QLineEdit()
        self.contact_input.setPlaceholderText("Enter number of farmers")
        self.contact_input.setMinimumHeight(34)

        self.oft_show_btn = QPushButton("Show")
        self.oft_show_btn.setMinimumHeight(34)
        self.oft_show_btn.setMinimumWidth(140)
        self.oft_show_btn.setMaximumWidth(160)
        self.oft_show_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.oft_show_btn.clicked.connect(self._show_oft_farmer_boxes)

        self.description_input = QTextEdit()
        self.description_input.hide()

        self.oft_technical_widget = QWidget()
        oft_technical_layout = QGridLayout(self.oft_technical_widget)
        oft_technical_layout.setContentsMargins(0, 0, 0, 0)
        oft_technical_layout.setHorizontalSpacing(8)
        oft_technical_layout.setVerticalSpacing(6)

        self.oft_t1_input = QLineEdit()
        self.oft_t2_input = QLineEdit()
        self.oft_t3_input = QLineEdit()
        for name, widget in (
            ("t1", self.oft_t1_input),
            ("t2", self.oft_t2_input),
            ("t3", self.oft_t3_input),
        ):
            widget.setObjectName(name)
            widget.setPlaceholderText(name)
            widget.setMinimumHeight(34)

        oft_technical_layout.addWidget(QLabel("t1"), 0, 0)
        oft_technical_layout.addWidget(self.oft_t1_input, 0, 1)
        oft_technical_layout.addWidget(QLabel("t2"), 1, 0)
        oft_technical_layout.addWidget(self.oft_t2_input, 1, 1)
        oft_technical_layout.addWidget(QLabel("t3"), 2, 0)
        oft_technical_layout.addWidget(self.oft_t3_input, 2, 1)
        oft_technical_layout.setColumnStretch(1, 1)

        self.remarks_input = QLineEdit()
        self.remarks_input.setPlaceholderText("Enter area")
        self.remarks_input.setMinimumHeight(34)

        self.date_input.setMinimumHeight(34)
        self.department_combo.setMinimumHeight(34)
        self.activity_type_input.setMinimumHeight(34)
        self.season_combo.setMinimumHeight(34)

        form_layout.addRow("Date*", self.date_input)
        form_layout.addRow(f"Title of {module_short}*", self.farmer_name_input)
        form_layout.addRow("Crop Variety*", self.village_input)
        farmers_row = QHBoxLayout()
        farmers_row.setSpacing(8)
        farmers_row.addWidget(self.contact_input)
        farmers_row.addWidget(self.oft_show_btn)
        farmers_row.addStretch(1)
        form_layout.addRow("No. of Farmers*", farmers_row)
        if self.module_name == "On Farm Testing (OFT)":
            form_layout.addRow("Technical Assessment*", self.oft_technical_widget)
        form_layout.addRow("Area*", self.remarks_input)

        self.oft_farmer_boxes_card = QFrame()
        self.oft_farmer_boxes_card.setObjectName("Card")
        self.oft_farmer_boxes_layout = QVBoxLayout(self.oft_farmer_boxes_card)
        self.oft_farmer_boxes_card.hide()
        self.oft_boxes_visible = False

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")

        self.save_btn.setMinimumHeight(34)
        self.reset_btn.setMinimumHeight(34)

        self.save_btn.clicked.connect(self._save_record)
        self.reset_btn.clicked.connect(self._reset_form)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch(1)
        form_layout.addRow(btn_row)

        # OFT final save is intentionally placed below farmer forms.
        self.save_btn.hide()

        self.oft_saved_summary_label = QLabel("Saved farmer forms: 0")
        form_layout.addRow(self.oft_saved_summary_label)

        form_card.hide()
        root.addWidget(form_card)

        self.oft_boxes_scroll = QScrollArea()
        self.oft_boxes_scroll.setWidgetResizable(True)
        self.oft_boxes_scroll.setWidget(self.oft_farmer_boxes_card)
        self.oft_boxes_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.oft_boxes_scroll.setMinimumHeight(500)
        self.oft_boxes_scroll.setMaximumHeight(700)
        self.oft_boxes_scroll.verticalScrollBar().setSingleStep(18)
        self.oft_boxes_scroll.hide()
        root.addWidget(self.oft_boxes_scroll)

        save_all_row = QHBoxLayout()
        self.oft_save_all_btn = QPushButton(f"Save All {module_short} Changes")
        self.oft_save_all_btn.setMinimumHeight(36)
        self.oft_save_all_btn.clicked.connect(self._save_record)
        save_all_row.addWidget(self.oft_save_all_btn)
        save_all_row.addStretch(1)
        root.addLayout(save_all_row)

        self._refresh_activity_type_options()
        self._update_oft_form_visibility()

        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)

        filters_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search farmer, village, contact, activity...")

        self.filter_department_combo = QComboBox()
        self.filter_department_combo.addItem("All Departments", None)
        for dept in self.departments:
            self.filter_department_combo.addItem(dept.name, dept.id)

        self.filter_season_combo = QComboBox()
        self.filter_season_combo.addItems(["All", "Kharif", "Rabi"])

        self.filter_date_mode_combo = QComboBox()
        self.filter_date_mode_combo.addItems(["All Dates", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"])
        self.filter_date_mode_combo.currentTextChanged.connect(self._on_filter_date_mode_changed)

        self.filter_from_date = QDateEdit()
        self.filter_from_date.setCalendarPopup(True)
        self.filter_from_date.setDate(QDate.currentDate().addDays(-30))
        self.filter_to_date = QDateEdit()
        self.filter_to_date.setCalendarPopup(True)
        self.filter_to_date.setDate(QDate.currentDate())
        self.filter_from_date.hide()
        self.filter_to_date.hide()

        apply_filter_btn = QPushButton("Apply Filter")
        clear_filter_btn = QPushButton("Clear")
        apply_filter_btn.clicked.connect(self._apply_filters)
        clear_filter_btn.clicked.connect(self._clear_filters)

        filters_row.addWidget(self.search_input)
        filters_row.addWidget(self.filter_department_combo)
        filters_row.addWidget(self.filter_season_combo)
        filters_row.addWidget(self.filter_date_mode_combo)
        filters_row.addWidget(self.filter_from_date)
        filters_row.addWidget(self.filter_to_date)
        filters_row.addWidget(apply_filter_btn)
        filters_row.addWidget(clear_filter_btn)

        table_layout.addLayout(filters_row)

        headers = [
            "Sr No",
            "Date",
            f"Title of {module_short}",
            "Crop Variety",
            "No. of Farmers",
            "Farmer Name",
            "Farmer ID",
            "Farmer Village",
            "Mobile No.",
            "Scientist",
            "Purpose",
            "District",
            "Tehsil",
        ]
        if self.module_name == "On Farm Testing (OFT)":
            headers.extend(["t1", "t2", "t3"])
        headers.extend([
            "Area",
            "Department",
            "Activity",
            "Season",
        ])
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self._on_row_selected)

        pager_row = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.oft_table_edit_btn = QPushButton("Open Edit Dialog")
        self.oft_table_delete_btn = QPushButton("Delete Selected")
        self.oft_table_edit_btn.setEnabled(False)
        self.oft_table_delete_btn.setEnabled(False)
        if self.module_name == "On Farm Testing (OFT)":
            self.oft_table_edit_btn.clicked.connect(self._open_oft_edit_dialog)
        else:
            self.oft_table_edit_btn.clicked.connect(self._open_fld_edit_dialog)
        self.oft_table_delete_btn.clicked.connect(self._delete_record)
        self.page_label = QLabel("Page 1")

        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)

        pager_row.addWidget(self.prev_btn)
        pager_row.addWidget(self.next_btn)
        pager_row.addWidget(self.oft_table_edit_btn)
        pager_row.addWidget(self.oft_table_delete_btn)
        pager_row.addWidget(self.page_label)
        pager_row.addStretch(1)

        table_layout.addWidget(self.table)
        table_layout.addLayout(pager_row)
        root.addWidget(table_card)

    def _build_training_ui(self, root: QVBoxLayout) -> None:
        """Build training-specific UI with selection card and data form."""
        
        # Selection card: Training Type and Department
        selection_card = QFrame()
        selection_card.setObjectName("Card")
        selection_layout = QGridLayout(selection_card)
        selection_layout.setHorizontalSpacing(12)
        selection_layout.setVerticalSpacing(8)

        self.training_type_combo = QComboBox()
        self.training_type_combo.addItems(["Regular", "Vocational", "Sponsored"])
        if self.module_name == "Vocational Training Programmes":
            self.training_type_combo.setCurrentIndex(1)  # Vocational

        self.department_combo = QComboBox()
        self.department_combo.addItem("Select Department", None)
        for dept in self.departments:
            self.department_combo.addItem(dept.name, dept.id)

        selection_layout.addWidget(QLabel("Training Type*"), 0, 0)
        selection_layout.addWidget(self.training_type_combo, 0, 1)
        selection_layout.addWidget(QLabel("Department*"), 0, 2)
        selection_layout.addWidget(self.department_combo, 0, 3)
        selection_layout.setColumnStretch(1, 1)
        selection_layout.setColumnStretch(3, 1)

        root.addWidget(selection_card)

        # Data form: only visible when department is selected
        data_card = QFrame()
        data_card.setObjectName("Card")
        self.training_data_card = data_card
        data_layout = QFormLayout(data_card)
        data_layout.setHorizontalSpacing(12)
        data_layout.setVerticalSpacing(10)
        data_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDate(QDate.currentDate())
        self.date_input.setMinimumHeight(34)

        self.end_date_input = QDateEdit()
        self.end_date_input.setCalendarPopup(True)
        self.end_date_input.setDate(QDate.currentDate())
        self.end_date_input.setMinimumHeight(34)

        self.farmer_name_input = QLineEdit()
        self.farmer_name_input.setPlaceholderText("Enter training title")
        self.farmer_name_input.setMinimumHeight(34)

        self.clientele_input = QComboBox()
        self.clientele_input.addItem("Select Clientele", None)
        for clientele_code in ("PF", "RY", "EF"):
            self.clientele_input.addItem(clientele_code, clientele_code)
        self.clientele_input.setMinimumHeight(34)

        self.village_input = QLineEdit()
        self.village_input.setPlaceholderText("Enter venue")
        self.village_input.setText("KVK")
        self.village_input.setMinimumHeight(34)

        venue_mode_widget = QWidget()
        venue_mode_layout = QHBoxLayout(venue_mode_widget)
        venue_mode_layout.setContentsMargins(0, 0, 0, 0)
        venue_mode_layout.setSpacing(12)
        venue_mode_layout.addWidget(self.village_input)
        self.venue_on_radio = QRadioButton("On")
        self.venue_off_radio = QRadioButton("Off")
        self.venue_on_radio.setChecked(True)
        venue_mode_layout.addWidget(self.venue_on_radio)
        venue_mode_layout.addWidget(self.venue_off_radio)
        venue_mode_layout.addStretch(1)

        data_layout.addRow("Start Date*", self.date_input)
        data_layout.addRow("End Date*", self.end_date_input)
        data_layout.addRow("Title*", self.farmer_name_input)
        data_layout.addRow("Clientele*", self.clientele_input)
        data_layout.addRow("Venue*", venue_mode_widget)

        # Offline venue fields (hidden by default)
        self.venue_offline_village_input = QLineEdit()
        self.venue_offline_village_input.setPlaceholderText("Village name")
        self.venue_offline_village_input.setMinimumHeight(34)

        self.venue_offline_taluka_input = QComboBox()
        self.venue_offline_taluka_input.addItem("Select Taluka", None)
        self.venue_offline_taluka_input.setMinimumHeight(34)

        self.venue_offline_district_input = QComboBox()
        self.venue_offline_district_input.addItem("Select District", None)
        for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
            self.venue_offline_district_input.addItem(district_name, district_name)
        self.venue_offline_district_input.setMinimumHeight(34)

        self.venue_offline_widget = QWidget()
        self.venue_offline_widget.setVisible(False)
        venue_offline_layout = QFormLayout(self.venue_offline_widget)
        venue_offline_layout.setContentsMargins(0, 0, 0, 0)
        venue_offline_layout.addRow("Village*", self.venue_offline_village_input)
        venue_offline_layout.addRow("Taluka*", self.venue_offline_taluka_input)
        venue_offline_layout.addRow("District*", self.venue_offline_district_input)
        data_layout.addRow(self.venue_offline_widget)

        # No. of Farmers and Show button
        self.training_farmer_count_input = QLineEdit()
        self.training_farmer_count_input.setPlaceholderText("Enter number of farmers")
        self.training_farmer_count_input.setValidator(QRegExpValidator(QRegExp(r"\d{0,6}"), self.training_farmer_count_input))
        self.training_farmer_count_input.setMinimumHeight(34)

        self.training_show_btn = QPushButton("Show")
        self.training_show_btn.setMinimumHeight(34)
        self.training_show_btn.setMinimumWidth(140)
        self.training_show_btn.setMaximumWidth(160)
        self.training_show_btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.training_show_btn.clicked.connect(self._show_training_farmer_boxes)

        farmers_row = QHBoxLayout()
        farmers_row.setSpacing(8)
        farmers_row.addWidget(self.training_farmer_count_input)
        farmers_row.addWidget(self.training_show_btn)
        farmers_row.addStretch(1)
        data_layout.addRow("No. of Farmers*", farmers_row)

        # Description and Remarks
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(65)
        self.description_input.setPlaceholderText("Training description")

        self.remarks_input = QTextEdit()
        self.remarks_input.setFixedHeight(65)
        self.remarks_input.setPlaceholderText("Remarks")

        data_layout.addRow("Description", self.description_input)
        data_layout.addRow("Remarks", self.remarks_input)

        # Farmer forms container (like OFT)
        self.training_farmer_boxes_card = QFrame()
        self.training_farmer_boxes_card.setObjectName("Card")
        self.training_farmer_boxes_layout = QVBoxLayout(self.training_farmer_boxes_card)
        self.training_farmer_boxes_card.hide()
        self.training_boxes_visible = False

        # Save and Reset buttons
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")
        self.save_btn.setMinimumHeight(34)
        self.reset_btn.setMinimumHeight(34)
        self.save_btn.clicked.connect(self._save_record)
        self.reset_btn.clicked.connect(self._reset_form)
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addStretch(1)
        data_layout.addRow(btn_row)

        self.training_saved_summary_label = QLabel("Saved farmer forms: 0")
        data_layout.addRow(self.training_saved_summary_label)

        data_card.hide()
        root.addWidget(data_card)

        # Farmer forms scroll area (like OFT)
        self.training_boxes_scroll = QScrollArea()
        self.training_boxes_scroll.setWidgetResizable(True)
        self.training_boxes_scroll.setWidget(self.training_farmer_boxes_card)
        self.training_boxes_scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.training_boxes_scroll.setMinimumHeight(500)
        self.training_boxes_scroll.setMaximumHeight(700)
        self.training_boxes_scroll.verticalScrollBar().setSingleStep(18)
        self.training_boxes_scroll.hide()
        root.addWidget(self.training_boxes_scroll)

        save_all_row = QHBoxLayout()
        self.training_save_all_btn = QPushButton("Save All Training Changes")
        self.training_save_all_btn.setMinimumHeight(36)
        self.training_save_all_btn.clicked.connect(self._save_record)
        save_all_row.addWidget(self.training_save_all_btn)
        save_all_row.addStretch(1)
        root.addLayout(save_all_row)
        self.training_save_all_btn.hide()

        # Connect signals
        self.department_combo.currentIndexChanged.connect(self._update_training_form_visibility)
        self.venue_on_radio.toggled.connect(self._update_training_venue_mode)
        self.venue_off_radio.toggled.connect(self._update_training_venue_mode)
        self.venue_offline_district_input.currentIndexChanged.connect(self._on_training_district_changed)
        self._update_training_venue_mode()

        # Build table
        self._build_training_table(root)

    def _on_training_district_changed(self) -> None:
        """Update taluka options when training district changes."""
        district = self.venue_offline_district_input.currentData()
        self.venue_offline_taluka_input.clear()
        self.venue_offline_taluka_input.addItem("Select Taluka", None)
        if district and district in MH_DISTRICT_TEHSILS:
            for taluka in MH_DISTRICT_TEHSILS[district]:
                self.venue_offline_taluka_input.addItem(taluka, taluka)

    def _update_training_form_visibility(self) -> None:
        """Show/hide training data form based on department selection."""
        department_selected = self.department_combo.currentData() is not None
        if hasattr(self, "training_data_card"):
            self.training_data_card.setVisible(department_selected)
        if hasattr(self, "training_boxes_scroll"):
            self.training_boxes_scroll.setVisible(department_selected and self.training_boxes_visible)
        if hasattr(self, "training_save_all_btn"):
            self.training_save_all_btn.setVisible(department_selected and self.training_boxes_visible)

    def _build_training_table(self, root: QVBoxLayout) -> None:
        """Build the training records table."""
        table_card = QFrame()
        table_card.setObjectName("Card")
        table_layout = QVBoxLayout(table_card)

        filters_row = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search title, venue, contact, activity...")

        self.filter_department_combo = QComboBox()
        self.filter_department_combo.addItem("All Departments", None)
        for dept in self.departments:
            self.filter_department_combo.addItem(dept.name, dept.id)

        self.filter_season_combo = QComboBox()
        self.filter_season_combo.addItems(["All", "Kharif", "Rabi"])

        self.filter_date_mode_combo = QComboBox()
        self.filter_date_mode_combo.addItems(["All Dates", "Today", "Last 7 Days", "Last 30 Days", "Custom Range"])
        self.filter_date_mode_combo.currentTextChanged.connect(self._on_filter_date_mode_changed)

        self.filter_from_date = QDateEdit()
        self.filter_from_date.setCalendarPopup(True)
        self.filter_from_date.setDate(QDate.currentDate().addDays(-30))
        self.filter_to_date = QDateEdit()
        self.filter_to_date.setCalendarPopup(True)
        self.filter_to_date.setDate(QDate.currentDate())
        self.filter_from_date.hide()
        self.filter_to_date.hide()

        apply_filter_btn = QPushButton("Apply Filter")
        clear_filter_btn = QPushButton("Clear")
        apply_filter_btn.clicked.connect(self._apply_filters)
        clear_filter_btn.clicked.connect(self._clear_filters)

        filters_row.addWidget(self.search_input)
        filters_row.addWidget(self.filter_department_combo)
        filters_row.addWidget(self.filter_season_combo)
        filters_row.addWidget(self.filter_date_mode_combo)
        filters_row.addWidget(self.filter_from_date)
        filters_row.addWidget(self.filter_to_date)
        filters_row.addWidget(apply_filter_btn)
        filters_row.addWidget(clear_filter_btn)

        table_layout.addLayout(filters_row)

        headers = [
            "Sr No",
            "Title",
            "Venue",
            "Clientele",
            "Date",
            "Department",
            "Training Type",
            "Farmer Name",
            "Farmer ID",
            "Farmer Village",
            "Mobile No.",
            "Scientist",
            "Purpose",
            "Category",
            "District",
            "Tehsil",
            "Description",
            "Remarks",
        ]
        self.table = QTableWidget(0, len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setAlternatingRowColors(True)
        self.table.setShowGrid(False)
        self.table.verticalHeader().setVisible(False)
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self._on_row_selected)

        pager_row = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.page_label = QLabel("Page 1")
        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)

        pager_row.addWidget(self.prev_btn)
        pager_row.addWidget(self.next_btn)
        pager_row.addWidget(self.page_label)
        pager_row.addStretch(1)

        table_layout.addWidget(self.table)
        table_layout.addLayout(pager_row)

        root.addWidget(table_card)

    def _show_training_farmer_boxes(self) -> None:
        """Show farmer detail boxes when number is entered (like OFT)."""
        count_text = self.training_farmer_count_input.text().strip()
        if not count_text.isdigit() or int(count_text) <= 0:
            QMessageBox.warning(self, "Validation", "Enter a valid number of farmers before showing the form.")
            return

        farmer_count = int(count_text)
        self.training_farmer_forms = []
        while self.training_farmer_boxes_layout.count():
            item = self.training_farmer_boxes_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                while child_layout.count():
                    child_item = child_layout.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget is not None:
                        child_widget.deleteLater()
                child_layout.deleteLater()

        for index in range(farmer_count):
            form_state = {
                "index": index,
                "farmer_name": QLineEdit(),
                "district": QComboBox(),
                "tehsil": QComboBox(),
                "village": QComboBox(),
                "mobile": QLineEdit(),
                "scientist": QLineEdit(),
                "purpose": QComboBox(),
                "category": QComboBox(),
                "saved": False,
            }
            form_state["farmer_name"].setPlaceholderText("Farmer name")
            self.training_farmer_forms.append(form_state)

        self.training_boxes_visible = True
        self.training_farmer_boxes_card.show()
        self.training_boxes_scroll.show()
        self.training_save_all_btn.show()
        self.current_training_farmer_index = 0
        self._display_training_farmer_form(0)
        self._update_training_saved_summary()

    def _display_training_farmer_form(self, farmer_index: int) -> None:
        if farmer_index < 0 or farmer_index >= len(self.training_farmer_forms):
            return

        previous_index = self.current_training_farmer_index
        if 0 <= previous_index < len(self.training_farmer_forms):
            previous_form = self.training_farmer_forms[previous_index]
            for key in ["farmer_name", "district", "tehsil", "village", "mobile", "scientist", "purpose", "category"]:
                prev_widget = previous_form.get(key)
                if prev_widget is not None and prev_widget.parent() is not None:
                    prev_widget.setParent(None)

        self.current_training_farmer_index = farmer_index
        while self.training_farmer_boxes_layout.count():
            item = self.training_farmer_boxes_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                while child_layout.count():
                    child_item = child_layout.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget is not None:
                        child_widget.deleteLater()
                child_layout.deleteLater()

        form_state = self.training_farmer_forms[farmer_index]
        if form_state["district"].count() == 0:
            self._setup_training_farmer_form_widgets(form_state)

        box = QFrame()
        box.setObjectName("Card")
        box_layout = QFormLayout(box)
        box_layout.setHorizontalSpacing(12)
        box_layout.setVerticalSpacing(8)
        box_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        box.setMinimumHeight(450)
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        box_title = QLabel(f"Farmer Form {farmer_index + 1} of {len(self.training_farmer_forms)}")
        box_title.setObjectName("CardTitle")
        box_layout.addRow(box_title)
        box_layout.addRow(f"Farmer {farmer_index + 1} Name*", form_state["farmer_name"])
        box_layout.addRow("District*", form_state["district"])
        box_layout.addRow("Tehsil*", form_state["tehsil"])
        box_layout.addRow("Village*", form_state["village"])
        box_layout.addRow("Mobile No.*", form_state["mobile"])
        box_layout.addRow("Name of Scientist*", form_state["scientist"])
        box_layout.addRow("Purpose*", form_state["purpose"])
        box_layout.addRow("Category*", form_state["category"])

        status_label = QLabel("Saved" if form_state["saved"] else "Not saved")
        status_label.setStyleSheet("color: " + ("green" if form_state["saved"] else "orange") + ";")
        box_layout.addRow("Status:", status_label)
        self.training_farmer_boxes_layout.addWidget(box)

        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        save_next_btn = QPushButton("Save & Next" if farmer_index < len(self.training_farmer_forms) - 1 else "Save & Finish")
        save_next_btn.setMinimumHeight(32)
        save_next_btn.clicked.connect(lambda: self._save_and_next_training_farmer(farmer_index))
        nav_layout.addWidget(save_next_btn)

        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(32)
        prev_btn.setEnabled(farmer_index > 0)
        prev_btn.clicked.connect(lambda: self._display_training_farmer_form(farmer_index - 1))
        nav_layout.addWidget(prev_btn)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(32)
        next_btn.setEnabled(farmer_index < len(self.training_farmer_forms) - 1)
        next_btn.clicked.connect(lambda: self._display_training_farmer_form(farmer_index + 1))
        nav_layout.addWidget(next_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setMinimumHeight(32)
        reset_btn.setStyleSheet("background-color: #fff3cd;")
        reset_btn.clicked.connect(lambda: self._reset_training_farmer(farmer_index))
        nav_layout.addWidget(reset_btn)

        nav_layout.addStretch(1)
        self.training_farmer_boxes_layout.addLayout(nav_layout)

    def _setup_training_farmer_form_widgets(self, form_state) -> None:
        district = form_state["district"]
        tehsil = form_state["tehsil"]
        village = form_state["village"]

        district.setEditable(True)
        district.addItem("Select District", None)
        for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
            district.addItem(district_name, district_name)
        district.lineEdit().setPlaceholderText("Select district")
        self._configure_searchable_combo(district)
        district.setMinimumHeight(32)

        tehsil.setEditable(True)
        tehsil.addItem("Select Tehsil", None)
        tehsil.setEnabled(False)
        tehsil.lineEdit().setPlaceholderText("Select tehsil")
        self._configure_searchable_combo(tehsil)
        tehsil.setMinimumHeight(32)

        village.setEditable(True)
        village.setInsertPolicy(QComboBox.NoInsert)
        village.setCurrentIndex(-1)
        village.setEnabled(False)
        village.lineEdit().setPlaceholderText("Select village")
        self._configure_searchable_combo(village)
        village.setMinimumHeight(32)

        form_state["farmer_name"].setMinimumHeight(32)
        form_state["mobile"].setMinimumHeight(32)
        form_state["mobile"].setPlaceholderText("10 digit mobile number")
        self._configure_mobile_input(form_state["mobile"])
        form_state["scientist"].setMinimumHeight(32)
        form_state["purpose"].addItems(["Visitor Entry", "Consultation"])
        form_state["purpose"].setMinimumHeight(32)
        form_state["category"].addItems(["Select Category", "SC", "ST", "Other"])
        form_state["category"].setMinimumHeight(32)

        def _refresh_training_box_villages(_index: int = -1) -> None:
            district_value = district.currentText().strip()
            tehsil_value = tehsil.currentText().strip()
            if self._is_valid_district(district_value) and self._is_valid_tehsil(district_value, tehsil_value):
                village.setEnabled(True)
                villages = ActivityService.list_villages_for_training(district_value, tehsil_value, self.module_name)
            else:
                village.setEnabled(False)
                villages = []
            village.blockSignals(True)
            village.clear()
            village.addItems(villages)
            village.setCurrentIndex(-1)
            village.blockSignals(False)

        def _refresh_training_tehsils(_index: int = -1) -> None:
            district_value = district.currentText().strip()
            tehsil.blockSignals(True)
            tehsil.clear()
            tehsil.addItem("Select Tehsil", None)
            if self._is_valid_district(district_value):
                for tehsil_name in MH_DISTRICT_TEHSILS.get(district_value, []):
                    tehsil.addItem(tehsil_name, tehsil_name)
                tehsil.setEnabled(True)
            else:
                tehsil.setEnabled(False)
            tehsil.setCurrentIndex(0)
            tehsil.blockSignals(False)
            _refresh_training_box_villages()

        district.currentIndexChanged.connect(_refresh_training_tehsils)
        tehsil.currentIndexChanged.connect(_refresh_training_box_villages)

    def _validate_training_farmer_form(self, form_state) -> bool:
        farmer_index = form_state["index"] + 1
        farmer_name = form_state["farmer_name"].text().strip()
        district_value = form_state["district"].currentText().strip()
        tehsil_value = form_state["tehsil"].currentText().strip()
        village_value = form_state["village"].currentText().strip()
        mobile = form_state["mobile"].text().strip()
        scientist_value = form_state["scientist"].text().strip()
        purpose_value = form_state["purpose"].currentText().strip()
        category_value = form_state["category"].currentText().strip()

        if not farmer_name:
            QMessageBox.warning(self, "Validation", f"Enter farmer name in Farmer Form {farmer_index}.")
            return False
        if not self._is_valid_district(district_value):
            QMessageBox.warning(self, "Validation", f"Select valid district in Farmer Form {farmer_index}.")
            return False
        if not self._is_valid_tehsil(district_value, tehsil_value):
            QMessageBox.warning(self, "Validation", f"Select valid tehsil in Farmer Form {farmer_index}.")
            return False
        if not village_value:
            QMessageBox.warning(self, "Validation", f"Select village in Farmer Form {farmer_index}.")
            return False
        if not mobile.isdigit() or len(mobile) != 10:
            QMessageBox.warning(self, "Validation", f"Enter exactly 10 digits for mobile number in Farmer Form {farmer_index}.")
            return False
        if not scientist_value:
            QMessageBox.warning(self, "Validation", f"Enter scientist name in Farmer Form {farmer_index}.")
            return False
        if not purpose_value:
            QMessageBox.warning(self, "Validation", f"Select purpose in Farmer Form {farmer_index}.")
            return False
        if category_value == "Select Category":
            QMessageBox.warning(self, "Validation", f"Select category in Farmer Form {farmer_index}.")
            return False
        return True

    def _save_and_next_training_farmer(self, farmer_index: int) -> None:
        if farmer_index >= len(self.training_farmer_forms):
            return
        form_state = self.training_farmer_forms[farmer_index]
        if not self._validate_training_farmer_form(form_state):
            return
        form_state["saved"] = True
        self._update_training_saved_summary()
        if farmer_index < len(self.training_farmer_forms) - 1:
            self._display_training_farmer_form(farmer_index + 1)
        else:
            self._display_training_farmer_form(farmer_index)

    def _reset_training_farmer(self, farmer_index: int) -> None:
        if farmer_index >= len(self.training_farmer_forms):
            return
        form_state = self.training_farmer_forms[farmer_index]
        form_state["farmer_name"].clear()
        form_state["district"].setCurrentIndex(0)
        form_state["tehsil"].setCurrentIndex(0)
        form_state["village"].setCurrentIndex(-1)
        form_state["mobile"].clear()
        form_state["scientist"].clear()
        form_state["purpose"].setCurrentIndex(0)
        form_state["category"].setCurrentIndex(0)
        form_state["saved"] = False
        self._display_training_farmer_form(farmer_index)
        self._update_training_saved_summary()

    def _update_training_saved_summary(self) -> None:
        if not hasattr(self, "training_saved_summary_label"):
            return
        saved_count = sum(1 for form in self.training_farmer_forms if form.get("saved"))
        total_count = len(self.training_farmer_forms)
        self.training_saved_summary_label.setText(f"Saved farmer forms: {saved_count} of {total_count}")

    def _update_oft_form_visibility(self) -> None:

        if not self._is_oft_style_module():
            return

        department_selected = self.department_combo.currentData() is not None
        activity_text = self.activity_type_input.currentText().strip()
        activity_selected = activity_text not in {"", "Select Activity Type", "Select Department First", "Not Applicable"}
        season_text = self.season_combo.currentText().strip()
        season_selected = season_text in {"Kharif", "Rabi"}
        header_ready = department_selected and activity_selected and season_selected

        if hasattr(self, "oft_data_card") and self.oft_data_card is not None:
            self.oft_data_card.setVisible(header_ready)

        if hasattr(self, "oft_boxes_scroll") and self.oft_boxes_scroll is not None:
            self.oft_boxes_scroll.setVisible(header_ready and self.oft_boxes_visible)

        if hasattr(self, "oft_save_all_btn") and self.oft_save_all_btn is not None:
            self.oft_save_all_btn.setVisible(header_ready and self.oft_boxes_visible)
            self.oft_save_all_btn.setEnabled(header_ready and self.oft_boxes_visible)

        self.save_btn.setEnabled(header_ready)

    def _update_training_venue_mode(self) -> None:
        if self.module_name not in ["Training Programmes", "Vocational Training Programmes"]:
            return

        is_offline = self.venue_off_radio.isChecked()
        self.venue_offline_widget.setVisible(is_offline)
        if self.venue_on_radio.isChecked():
            self.village_input.setText("KVK")

    def _on_extension_activity_changed(self, _index: int = -1) -> None:
        if hasattr(self, "extension_fields_widget"):
            self.extension_fields_widget.setVisible(self.activity_type_input.currentIndex() > 0)

    def _on_other_extension_activity_changed(self, _index: int = -1) -> None:
        if hasattr(self, "other_extension_fields_widget"):
            self.other_extension_fields_widget.setVisible(self.activity_type_input.currentIndex() > 0)

    def _show_oft_farmer_boxes(self) -> None:
        if not self._is_oft_style_module():
            return

        count_text = self.contact_input.text().strip()
        if not count_text.isdigit() or int(count_text) <= 0:
            QMessageBox.warning(self, "Validation", "Enter a valid number of farmers before showing the form.")
            return

        farmer_count = int(count_text)
        self.oft_farmer_forms = []
        while self.oft_farmer_boxes_layout.count():
            item = self.oft_farmer_boxes_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

        # Initialize farmer forms with data structures
        for index in range(farmer_count):
            form_state = {
                "index": index,
                "farmer_name": QLineEdit(),
                "district": QComboBox(),
                "tehsil": QComboBox(),
                "village": QComboBox(),
                "mobile": QLineEdit(),
                "scientist": QLineEdit(),
                "purpose": QComboBox(),
                "saved": False,
            }
            self.oft_farmer_forms.append(form_state)

        # Build and display the first farmer form
        self._display_farmer_form(0)
        self.oft_boxes_visible = True
        self.oft_farmer_boxes_card.setVisible(True)
        self.oft_boxes_scroll.setVisible(True)
        self._update_oft_saved_summary()
        self._update_oft_form_visibility()

    def _setup_farmer_form_widgets(self, form_state) -> None:
        """Configure combo boxes and connections for a farmer form"""
        district = form_state["district"]
        tehsil = form_state["tehsil"]
        village = form_state["village"]
        
        # Configure District
        district.setEditable(True)
        district.addItem("Select District", None)
        for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
            district.addItem(district_name, district_name)
        district.lineEdit().setPlaceholderText("Select district")
        self._configure_searchable_combo(district)
        district.setMinimumHeight(32)

        # Configure Tehsil
        tehsil.setEditable(True)
        tehsil.addItem("Select Tehsil", None)
        tehsil.setEnabled(False)
        tehsil.lineEdit().setPlaceholderText("Select tehsil")
        self._configure_searchable_combo(tehsil)
        tehsil.setMinimumHeight(32)

        # Configure Village
        village.setEditable(True)
        village.setInsertPolicy(QComboBox.NoInsert)
        village.setCurrentIndex(-1)
        village.setEnabled(False)
        village.lineEdit().setPlaceholderText("Select village")
        self._configure_searchable_combo(village)
        village.setMinimumHeight(32)

        # Configure other fields
        form_state["farmer_name"].setMinimumHeight(32)
        form_state["mobile"].setMinimumHeight(32)
        self._configure_mobile_input(form_state["mobile"])
        form_state["scientist"].setMinimumHeight(32)
        form_state["purpose"].addItems(["Visitor Entry", "Consultation"])
        form_state["purpose"].setMinimumHeight(32)

        # Set up district/tehsil/village cascading
        def _refresh_box_villages(_index: int = -1) -> None:
            district_value = district.currentText().strip()
            tehsil_value = tehsil.currentText().strip()
            if self._is_valid_district(district_value) and self._is_valid_tehsil(district_value, tehsil_value):
                village.setEnabled(True)
                villages = ActivityService.list_villages_for_oft(district_value, tehsil_value, self.module_name)
            else:
                village.setEnabled(False)
                villages = []
            village.blockSignals(True)
            village.clear()
            village.addItems(villages)
            village.setCurrentIndex(-1)
            village.blockSignals(False)

        def _refresh_tehsils(_index: int = -1) -> None:
            district_value = district.currentText().strip()
            tehsil.blockSignals(True)
            tehsil.clear()
            tehsil.addItem("Select Tehsil", None)
            if self._is_valid_district(district_value):
                for tehsil_name in MH_DISTRICT_TEHSILS.get(district_value, []):
                    tehsil.addItem(tehsil_name, tehsil_name)
                tehsil.setEnabled(True)
            else:
                tehsil.setEnabled(False)
            tehsil.setCurrentIndex(0)
            tehsil.blockSignals(False)
            _refresh_box_villages()

        district.currentIndexChanged.connect(_refresh_tehsils)
        tehsil.currentIndexChanged.connect(_refresh_box_villages)

    def _display_farmer_form(self, farmer_index: int) -> None:
        """Display a specific farmer form (sequential view)"""
        if farmer_index < 0 or farmer_index >= len(self.oft_farmer_forms):
            return

        previous_index = self.current_farmer_index
        if 0 <= previous_index < len(self.oft_farmer_forms):
            previous_form = self.oft_farmer_forms[previous_index]
            for key in ["farmer_name", "district", "tehsil", "village", "mobile", "scientist", "purpose"]:
                prev_widget = previous_form.get(key)
                if prev_widget is not None and prev_widget.parent() is not None:
                    prev_widget.setParent(None)

        self.current_farmer_index = farmer_index
        
        # Clear existing widgets
        while self.oft_farmer_boxes_layout.count():
            item = self.oft_farmer_boxes_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
                continue
            child_layout = item.layout()
            if child_layout is not None:
                while child_layout.count():
                    child_item = child_layout.takeAt(0)
                    child_widget = child_item.widget()
                    if child_widget is not None:
                        child_widget.deleteLater()
                child_layout.deleteLater()

        form_state = self.oft_farmer_forms[farmer_index]
        
        # Setup widgets if not already done
        if form_state["district"].count() == 0:
            self._setup_farmer_form_widgets(form_state)
        
        # Create main form card
        box = QFrame()
        box.setObjectName("Card")
        box_layout = QFormLayout(box)
        box_layout.setHorizontalSpacing(12)
        box_layout.setVerticalSpacing(8)
        box_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        box.setMinimumHeight(450)
        box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Title
        box_title = QLabel(f"Farmer Form {farmer_index + 1} of {len(self.oft_farmer_forms)}")
        box_title.setObjectName("CardTitle")
        box_layout.addRow(box_title)

        # Form fields
        box_layout.addRow(f"Farmer {farmer_index + 1} Name*", form_state["farmer_name"])
        box_layout.addRow("District*", form_state["district"])
        box_layout.addRow("Tehsil*", form_state["tehsil"])
        box_layout.addRow("Village*", form_state["village"])
        box_layout.addRow("Mobile No.*", form_state["mobile"])
        box_layout.addRow("Name of Scientist*", form_state["scientist"])
        box_layout.addRow("Purpose*", form_state["purpose"])

        # Status label
        status_label = QLabel("Not saved" if not form_state["saved"] else "Saved ✓")
        status_label.setStyleSheet("color: " + ("green" if form_state["saved"] else "orange") + ";")
        box_layout.addRow("Status:", status_label)

        self.oft_farmer_boxes_layout.addWidget(box)

        # Navigation and action buttons
        nav_layout = QHBoxLayout()
        nav_layout.setSpacing(10)

        save_next_btn = QPushButton("Save & Next" if farmer_index < len(self.oft_farmer_forms) - 1 else "Save & Finish")
        save_next_btn.setMinimumHeight(32)
        save_next_btn.clicked.connect(lambda: self._save_and_next_farmer(farmer_index))
        nav_layout.addWidget(save_next_btn)

        prev_btn = QPushButton("Previous")
        prev_btn.setMinimumHeight(32)
        prev_btn.setEnabled(farmer_index > 0)
        prev_btn.clicked.connect(lambda: self._previous_farmer(farmer_index))
        nav_layout.addWidget(prev_btn)

        next_btn = QPushButton("Next")
        next_btn.setMinimumHeight(32)
        next_btn.setEnabled(farmer_index < len(self.oft_farmer_forms) - 1)
        next_btn.clicked.connect(lambda: self._next_farmer(farmer_index))
        nav_layout.addWidget(next_btn)

        reset_btn = QPushButton("Reset")
        reset_btn.setMinimumHeight(32)
        reset_btn.setStyleSheet("background-color: #fff3cd;")
        reset_btn.clicked.connect(lambda: self._reset_current_farmer(farmer_index))
        nav_layout.addWidget(reset_btn)

        nav_layout.addStretch(1)
        self.oft_farmer_boxes_layout.addLayout(nav_layout)


    def _save_and_next_farmer(self, farmer_index: int) -> None:
        """Validate and save current farmer, then move to next"""
        if farmer_index >= len(self.oft_farmer_forms):
            return

        form_state = self.oft_farmer_forms[farmer_index]
        
        if not self._validate_oft_farmer_form(form_state):
            return

        # Mark as saved
        form_state["saved"] = True
        self._update_oft_saved_summary()

        farmer_count = len(self.oft_farmer_forms)
        
        # If this is the last farmer, show submit dialog
        if farmer_index == farmer_count - 1:
            self._show_final_submit_dialog()
        else:
            # Move to next farmer
            self._display_farmer_form(farmer_index + 1)

    def _previous_farmer(self, current_index: int) -> None:
        """Navigate to previous farmer form"""
        if current_index > 0:
            self._display_farmer_form(current_index - 1)

    def _next_farmer(self, current_index: int) -> None:
        """Navigate to next farmer form"""
        if current_index < len(self.oft_farmer_forms) - 1:
            self._display_farmer_form(current_index + 1)

    def _reset_current_farmer(self, farmer_index: int) -> None:
        """Clear all fields in current farmer form"""
        if farmer_index >= len(self.oft_farmer_forms):
            return

        form_state = self.oft_farmer_forms[farmer_index]
        
        # Clear all fields
        form_state["farmer_name"].clear()
        form_state["district"].setCurrentIndex(0)
        form_state["tehsil"].setCurrentIndex(0)
        form_state["village"].setCurrentIndex(-1)
        form_state["mobile"].clear()
        form_state["scientist"].clear()
        form_state["purpose"].setCurrentIndex(0)
        
        # Reset saved status
        form_state["saved"] = False
        
        # Refresh display
        self._display_farmer_form(farmer_index)
        self._update_oft_saved_summary()

    def _show_final_submit_dialog(self) -> None:
        """Show final submit dialog when all farmers are saved"""
        module_short = "OFT" if self.module_name == "On Farm Testing (OFT)" else "FLD"
        all_saved = all(form.get("saved") for form in self.oft_farmer_forms)
        
        if not all_saved:
            QMessageBox.warning(self, "Incomplete", "Please save all farmer forms before submitting.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Confirm Submission")
        dialog.resize(400, 250)
        
        layout = QVBoxLayout(dialog)
        
        message = QLabel(
            f"All {len(self.oft_farmer_forms)} farmer forms have been filled and saved.\n\n"
            f"Click 'Save All {module_short} Data' to submit all records."
        )
        message.setWordWrap(True)
        layout.addWidget(message)
        
        layout.addStretch(1)
        
        buttons = QHBoxLayout()
        save_all_btn = QPushButton(f"Save All {module_short} Data")
        save_all_btn.setMinimumHeight(34)
        save_all_btn.clicked.connect(lambda: [dialog.accept(), self._save_all_oft_records()])
        buttons.addWidget(save_all_btn)
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setMinimumHeight(34)
        cancel_btn.clicked.connect(dialog.reject)
        buttons.addWidget(cancel_btn)
        
        layout.addLayout(buttons)
        dialog.exec_()

    def _collect_oft_common_payload(self):
        payload = self._collect_payload()
        if not self._validate_payload(payload):
            return None
        return payload

    def _validate_oft_farmer_form(self, form_state) -> bool:
        farmer_name = form_state["farmer_name"].text().strip()
        district_value = form_state["district"].currentText().strip()
        tehsil_value = form_state["tehsil"].currentText().strip()
        village_value = form_state["village"].currentText().strip()
        mobile_value = form_state["mobile"].text().strip()
        scientist_value = form_state["scientist"].text().strip()
        purpose_value = form_state["purpose"].currentText().strip()

        if not farmer_name:
            QMessageBox.warning(self, "Validation", f"Enter farmer name in Farmer Form {form_state['index'] + 1}.")
            return False
        if not self._is_valid_district(district_value):
            QMessageBox.warning(self, "Validation", f"Select valid district in Farmer Form {form_state['index'] + 1}.")
            return False
        if not self._is_valid_tehsil(district_value, tehsil_value):
            QMessageBox.warning(self, "Validation", f"Select valid tehsil in Farmer Form {form_state['index'] + 1}.")
            return False
        if not village_value:
            QMessageBox.warning(self, "Validation", f"Select village in Farmer Form {form_state['index'] + 1}.")
            return False
        if not mobile_value.isdigit() or len(mobile_value) != 10:
            QMessageBox.warning(self, "Validation", f"Enter exactly 10 digits for mobile number in Farmer Form {form_state['index'] + 1}.")
            return False
        if not scientist_value:
            QMessageBox.warning(self, "Validation", f"Enter scientist name in Farmer Form {form_state['index'] + 1}.")
            return False
        if not purpose_value:
            QMessageBox.warning(self, "Validation", f"Select purpose in Farmer Form {form_state['index'] + 1}.")
            return False
        return True

    def _update_oft_saved_summary(self) -> None:
        if not self._is_oft_style_module():
            return
        saved_count = sum(1 for form_state in self.oft_farmer_forms if form_state.get("saved"))
        total_count = len(self.oft_farmer_forms)
        if hasattr(self, "oft_saved_summary_label"):
            self.oft_saved_summary_label.setText(f"Saved farmer forms: {saved_count} of {total_count}")

    def _save_all_oft_records(self) -> None:
        common_payload = self._collect_oft_common_payload()
        if common_payload is None:
            return

        oft_batch_key = f"OFT-{uuid4().hex[:12]}"

        farmer_count = int(self.contact_input.text().strip()) if self.contact_input.text().strip().isdigit() else 0
        if farmer_count <= 0:
            QMessageBox.warning(self, "Validation", "Enter valid No. of Farmers and click Show.")
            return
        if not self.oft_farmer_forms:
            QMessageBox.warning(self, "Validation", "Click Show to generate farmer forms first.")
            return
        if len(self.oft_farmer_forms) != farmer_count:
            QMessageBox.warning(self, "Validation", "Farmer form count does not match No. of Farmers. Click Show again.")
            return

        unsaved_forms = [form_state for form_state in self.oft_farmer_forms if not form_state.get("saved")]
        if unsaved_forms:
            first_unsaved = unsaved_forms[0]["index"] + 1
            QMessageBox.warning(self, "Validation", f"Save Farmer Form {first_unsaved} before Save All Changes.")
            return

        try:
            for form_state in self.oft_farmer_forms:
                district_value = form_state["district"].currentText().strip()
                tehsil_value = form_state["tehsil"].currentText().strip()
                village_value = form_state["village"].currentText().strip()
                scientist_value = form_state["scientist"].text().strip()
                purpose_value = form_state["purpose"].currentText().strip()

                payload = {
                    "module_type": self.module_name,
                    "farmer_name": form_state["farmer_name"].text().strip(),
                    "village": village_value,
                    "contact_number": form_state["mobile"].text().strip(),
                    "activity_date": common_payload["activity_date"],
                    "department_id": common_payload["department_id"],
                    "season": common_payload["season"],
                    "activity_type": common_payload["activity_type"],
                    "description": common_payload["description"],
                    "remarks": f"OFT_META|District: {district_value}|Tehsil: {tehsil_value}",
                    "oft_title": common_payload["farmer_name"],
                    "oft_batch_key": oft_batch_key,
                    "oft_crop_variety": common_payload["village"],
                    "oft_farmer_count": int(common_payload["contact_number"]),
                    "oft_technical_assessment": common_payload["description"],
                    "oft_area": common_payload["remarks"],
                    "oft_farmer_scientist": scientist_value,
                    "oft_farmer_purpose": purpose_value,
                    "oft_farmer_district": district_value,
                    "oft_farmer_tehsil": tehsil_value,
                }
                ActivityService.create_activity(payload, self.current_user.id)

            module_short = "OFT" if self.module_name == "On Farm Testing (OFT)" else "FLD"
            QMessageBox.information(self, "Saved", f"All {module_short} farmer records saved successfully.")
            self._reset_form()
            self.current_page = 1
            self._load_table()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not save OFT records: {exc}")

    def _apply_role_permissions(self) -> None:
        if not self.read_only:
            self.mode_label.setText("Mode: Full access")
            return

        self.mode_label.setText("Mode: Staff read-only for this module")
        for field_name in (
            "farmer_name_input",
            "contact_input",
            "scientist_input",
            "training_farmer_count_input",
            "venue_offline_village_input",
            "extension_venue_input",
            "extension_location_input",
            "extension_farmer_count_input",
            "other_extension_title_input",
        ):
            if hasattr(self, field_name):
                getattr(self, field_name).setReadOnly(True)

        for widget_name in (
            "village_input",
            "tehsil_input",
            "district_input",
            "date_input",
            "department_combo",
            "season_combo",
            "activity_type_input",
            "training_type_combo",
            "clientele_input",
            "training_show_btn",
            "venue_on_radio",
            "venue_off_radio",
            "venue_offline_taluka_input",
            "venue_offline_district_input",
            "other_extension_fields_widget",
            ):
            if hasattr(self, widget_name):
                getattr(self, widget_name).setEnabled(False)

        if self.module_name == "Front Line Demonstrations (FLD)" and hasattr(self, "fld_technical_group"):
            for btn in self.fld_technical_group.buttons():
                btn.setEnabled(False)
        elif self.module_name == "On Farm Testing (OFT)" and hasattr(self, "oft_t1_input"):
            self.oft_t1_input.setReadOnly(True)
            self.oft_t2_input.setReadOnly(True)
            self.oft_t3_input.setReadOnly(True)
        elif hasattr(self, "description_input"):
            self.description_input.setReadOnly(True)
        if hasattr(self, "extension_purpose_input"):
            self.extension_purpose_input.setReadOnly(True)
        if hasattr(self, "remarks_input"):
            self.remarks_input.setReadOnly(True)
        if hasattr(self, "save_btn"):
            self.save_btn.setEnabled(False)
        for button_name in ("oft_save_all_btn", "training_save_all_btn"):
            if hasattr(self, button_name):
                getattr(self, button_name).setEnabled(False)

    def _collect_payload(self):
        activity_type = self.activity_type_input.currentText().strip() if hasattr(self, "activity_type_input") else ""
        season_value = self.season_combo.currentText() if hasattr(self, "season_combo") else "Kharif"
        selected_department = self.department_combo.currentText().strip()

        if self.module_name == "Extension Activities":
            purpose_value = self.extension_purpose_input.toPlainText().strip()
            farmer_count_text = self.extension_farmer_count_input.text().strip()
            venue_value = self.extension_venue_input.text().strip()
            location_value = self.extension_location_input.text().strip()
            department_name = self.department_combo.currentText().strip()
            return {
                "module_type": self.module_name,
                "farmer_name": "N/A",
                "village": location_value or venue_value,
                "contact_number": "0000000000",
                "activity_date": self.date_input.date().toPyDate(),
                "department_id": self.department_combo.currentData(),
                "season": "Kharif",
                "activity_type": activity_type,
                "description": purpose_value,
                "remarks": "",
                "extension_venue": venue_value,
                "extension_location": location_value,
                "extension_department": department_name,
                "extension_purpose": purpose_value,
                "extension_farmer_count": int(farmer_count_text) if farmer_count_text.isdigit() else None,
            }

        if self.module_name == "Other Extension Activities":
            title_value = self.other_extension_title_input.text().strip()
            ext_idx = self.department_combo.findText("Agricultural Extension")
            if ext_idx >= 0:
                self.department_combo.setCurrentIndex(ext_idx)
            return {
                "module_type": self.module_name,
                "farmer_name": "N/A",
                "village": "Other Extension",
                "contact_number": "0000000000",
                "activity_date": self.date_input.date().toPyDate(),
                "department_id": self.department_combo.currentData(),
                "season": "Kharif",
                "activity_type": activity_type,
                "description": title_value,
                "remarks": "",
                "other_extension_title": title_value,
            }

        if self.module_name == "Visitor Farmers":
            # Visitor Farmers uses a custom field sequence and keeps season as internal default.
            season_value = "Kharif"
        elif self._is_oft_style_module():
            season_value = self.season_combo.currentText().strip()
        elif self.module_name == "Front Line Demonstrations (FLD)":
            # FLD does not use activity type in UI; store a stable default value.
            activity_type = "FLD Entry"
            if selected_department != "Horticulture":
                season_value = "Kharif"
        elif self.module_name == "Training Programmes":
            # Training Programmes use department and training type
            activity_type = "Training Entry"
            season_value = "Kharif"
        elif self.module_name == "Vocational Training Programmes":
            # Vocational Training Programmes use department and training type
            activity_type = "Vocational Entry"
            season_value = "Kharif"
        elif self.module_name == "Extension Activities":
            # Extension Activities use fixed department and no season UI.
            ext_idx = self.department_combo.findText("Agricultural Extension")
            if ext_idx >= 0:
                self.department_combo.setCurrentIndex(ext_idx)
            season_value = "Kharif"
        elif self.module_name == "Other Extension Activities":
            # Other Extension Activities use fixed department and no season UI.
            ext_idx = self.department_combo.findText("Agricultural Extension")
            if ext_idx >= 0:
                self.department_combo.setCurrentIndex(ext_idx)
            season_value = "Kharif"

        description_value = self.description_input.toPlainText().strip() if hasattr(self, "description_input") else ""
        remarks_value = ""
        
        if hasattr(self, "remarks_input"):
            remarks_value = self.remarks_input.text().strip() if hasattr(self.remarks_input, "text") else self.remarks_input.toPlainText().strip()
        
        if self.module_name == "Visitor Farmers":
            description_value = ""
            remarks_value = (
                f"District: {self.district_input.currentText().strip()} | "
                f"Tehsil: {self.tehsil_input.currentText().strip()}"
            )
        elif self._is_oft_style_module():
            description_value = self._get_oft_technical_assessment()
            remarks_value = self.remarks_input.text().strip() if hasattr(self, "remarks_input") else ""
        elif self.module_name == "Front Line Demonstrations (FLD)":
            description_value = self._get_fld_technical_assessment()

        # Handle venue information for training and regular modules
        venue_value = ""
        venue_is_offline = False
        venue_village = ""
        venue_taluka = ""
        venue_district = ""
        
        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            venue_value = self.village_input.text().strip()
            venue_is_offline = self.venue_off_radio.isChecked() if hasattr(self, "venue_off_radio") else False
            if not venue_is_offline and not venue_value:
                venue_value = "KVK"
            if venue_is_offline:
                venue_village = self.venue_offline_village_input.text().strip() if hasattr(self, "venue_offline_village_input") else ""
                venue_taluka = self.venue_offline_taluka_input.currentText().strip() if hasattr(self, "venue_offline_taluka_input") else ""
                venue_district = self.venue_offline_district_input.currentText().strip() if hasattr(self, "venue_offline_district_input") else ""
                venue_value = venue_village
        elif not self._is_oft_style_module():
            venue_value = self.village_input.currentText().strip() if hasattr(self, "village_input") else ""

        # Get contact number (not available for training)
        contact_number = ""
        if hasattr(self, "contact_input"):
            contact_number = self.contact_input.text().strip()

        return {
            "module_type": self.module_name,
            "farmer_name": self.farmer_name_input.text().strip() if hasattr(self, "farmer_name_input") else "",
            "village": venue_value,
            "contact_number": contact_number,
            "activity_date": self.date_input.date().toPyDate() if hasattr(self, "date_input") else None,
            "department_id": self.department_combo.currentData(),
            "season": season_value,
            "activity_type": activity_type,
            "description": description_value,
            "remarks": remarks_value,
            "visitor_scientist": self.scientist_input.text().strip() if self.module_name == "Visitor Farmers" and hasattr(self, "scientist_input") else None,
            "visitor_district": self.district_input.currentText().strip() if self.module_name == "Visitor Farmers" and hasattr(self, "district_input") else None,
            "visitor_tehsil": self.tehsil_input.currentText().strip() if self.module_name == "Visitor Farmers" and hasattr(self, "tehsil_input") else None,
            "training_title": self.farmer_name_input.text().strip() if self.module_name in ["Training Programmes", "Vocational Training Programmes"] and hasattr(self, "farmer_name_input") else None,
            "training_type": self.training_type_combo.currentText().strip() if self.module_name in ["Training Programmes", "Vocational Training Programmes"] and hasattr(self, "training_type_combo") else None,
            "training_end_date": self.end_date_input.date().toPyDate() if self.module_name in ["Training Programmes", "Vocational Training Programmes"] and hasattr(self, "end_date_input") else None,
            "clientele": self.clientele_input.currentData() if self.module_name in ["Training Programmes", "Vocational Training Programmes"] and hasattr(self, "clientele_input") else None,
            "thematic_area": None,  # Training modules don't use thematic area in new form
            "venue": venue_value if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else None,
            "venue_is_offline": venue_is_offline if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else None,
            "venue_village": venue_village if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else None,
            "venue_taluka": venue_taluka if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else None,
            "venue_district": venue_district if self.module_name in ["Training Programmes", "Vocational Training Programmes"] else None,
            "training_farmer_count": int(self.training_farmer_count_input.text().strip()) if self.module_name in ["Training Programmes", "Vocational Training Programmes"] and hasattr(self, "training_farmer_count_input") and self.training_farmer_count_input.text().strip().isdigit() else None,
        }


    def _get_fld_technical_assessment(self) -> str:
        if self.module_name != "Front Line Demonstrations (FLD)" or not hasattr(self, "fld_technical_group"):
            return self.description_input.toPlainText().strip()
        checked = self.fld_technical_group.checkedButton()
        if checked is not None:
            return checked.text().strip()
        return self.description_input.toPlainText().strip()

    def _set_fld_technical_assessment(self, value: str) -> None:
        normalized = (value or "").strip().upper()
        self.description_input.setPlainText((value or "").strip())
        if self.module_name != "Front Line Demonstrations (FLD)" or not hasattr(self, "fld_technical_group"):
            return
        for btn in self.fld_technical_group.buttons():
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)
        for btn in self.fld_technical_group.buttons():
            if btn.text().strip().upper() == normalized:
                btn.blockSignals(True)
                btn.setChecked(True)
                btn.blockSignals(False)
                break

    def _clear_fld_technical_assessment(self) -> None:
        self.description_input.clear()
        if self.module_name != "Front Line Demonstrations (FLD)" or not hasattr(self, "fld_technical_group"):
            return
        for btn in self.fld_technical_group.buttons():
            btn.blockSignals(True)
            btn.setChecked(False)
            btn.blockSignals(False)

    def _get_oft_technical_assessment(self) -> str:
        if self.module_name == "On Farm Testing (OFT)" and hasattr(self, "oft_t1_input"):
            return self._compose_oft_technical_assessment(
                self.oft_t1_input.text(),
                self.oft_t2_input.text(),
                self.oft_t3_input.text(),
            )
        return self.description_input.toPlainText().strip()

    def _set_oft_technical_assessment(self, value: str) -> None:
        self.description_input.setPlainText((value or "").strip())
        if self.module_name != "On Farm Testing (OFT)" or not hasattr(self, "oft_t1_input"):
            return
        t1, t2, t3 = self._parse_oft_technical_assessment(value)
        self.oft_t1_input.setText(t1)
        self.oft_t2_input.setText(t2)
        self.oft_t3_input.setText(t3)

    def _clear_oft_technical_assessment(self) -> None:
        self.description_input.clear()
        if self.module_name != "On Farm Testing (OFT)" or not hasattr(self, "oft_t1_input"):
            return
        self.oft_t1_input.clear()
        self.oft_t2_input.clear()
        self.oft_t3_input.clear()

    @staticmethod
    def _compose_oft_technical_assessment(t1: str, t2: str, t3: str) -> str:
        values = [t1.strip(), t2.strip(), t3.strip()]
        if any(not value for value in values):
            return ""
        return f"t1: {values[0]}\nt2: {values[1]}\nt3: {values[2]}"

    @staticmethod
    def _parse_oft_technical_assessment(value: str) -> tuple[str, str, str]:
        raw = (value or "").strip()
        parsed = {"t1": "", "t2": "", "t3": ""}
        found_labeled_value = False

        for line in raw.splitlines():
            label, separator, text = line.partition(":")
            key = label.strip().lower()
            if separator and key in parsed:
                parsed[key] = text.strip()
                found_labeled_value = True

        if raw and not found_labeled_value:
            parsed["t1"] = raw

        return parsed["t1"], parsed["t2"], parsed["t3"]

    def _refresh_activity_type_options(self) -> None:
        current_value = self.activity_type_input.currentText().strip()
        options = self.activity_type_presets.get(self.module_name, ["General Activity"])

        if self._is_oft_style_module():
            has_department = self.department_combo.currentData() is not None
            if not has_department:
                options = ["Select Department First"]
            else:
                options = ["Assessment"]

        self.activity_type_input.blockSignals(True)
        self.activity_type_input.clear()
        self.activity_type_input.addItems(options)

        # OFT and Extension Activities keep strict dropdown options.
        self.activity_type_input.setEditable(self.module_name not in ["On Farm Testing (OFT)", "Front Line Demonstrations (FLD)", "Extension Activities"])
        if self._is_oft_style_module():
            has_department = self.department_combo.currentData() is not None
            self.activity_type_input.setEnabled(has_department)
            if not has_department and self.activity_type_input.count() > 0:
                self.activity_type_input.setCurrentIndex(0)
        elif self.module_name == "Extension Activities":
            self.activity_type_input.setEnabled(True)

        if current_value:
            idx = self.activity_type_input.findText(current_value)
            if idx >= 0:
                self.activity_type_input.setCurrentIndex(idx)
            elif self.activity_type_input.isEditable():
                self.activity_type_input.setEditText(current_value)

        self.activity_type_input.blockSignals(False)
        self._refresh_season_options()
        self._update_oft_form_visibility()

    def _refresh_season_options(self) -> None:
        # Visitor Farmers never uses season field
        if self.module_name == "Visitor Farmers":
            self.season_label.setVisible(False)
            self.season_combo.setVisible(False)
            self.season_combo.setEnabled(False)
            return

        if self._is_oft_style_module():
            self.season_label.setVisible(True)
            self.season_combo.setVisible(True)
            self.season_combo.setEnabled(True)
            return
        
        if not self._is_oft_style_module():
            if self.module_name == "Extension Activities":
                self.department_label.setVisible(False)
                self.department_combo.setVisible(False)
                self.season_label.setVisible(False)
                self.season_combo.setVisible(False)
                self.season_combo.setEnabled(False)
                return

            if self.module_name == "Other Extension Activities":
                self.department_label.setVisible(False)
                self.department_combo.setVisible(False)
                self.season_label.setVisible(False)
                self.season_combo.setVisible(False)
                self.season_combo.setEnabled(False)
                return

            if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
                self.season_label.setVisible(False)
                self.season_combo.setVisible(False)
                self.season_combo.setEnabled(False)
                return

            if self.module_name == "Front Line Demonstrations (FLD)":
                selected_department = self.department_combo.currentText().strip()
                self.season_combo.blockSignals(True)
                self.season_combo.clear()
                self.season_combo.addItems(["Kharif", "Rabi"])
                self.season_combo.blockSignals(False)

                only_for_horticulture = selected_department == "Horticulture"
                self.season_label.setVisible(only_for_horticulture)
                self.season_combo.setVisible(only_for_horticulture)
                self.season_combo.setEnabled(only_for_horticulture)
                return

            if self.season_combo.count() == 0:
                self.season_combo.addItems(["Kharif", "Rabi"])
            self.season_label.setVisible(True)
            self.season_combo.setVisible(True)
            self.season_combo.setEnabled(True)
            return

        selected_department = self.department_combo.currentText().strip()
        selected_type = self.activity_type_input.currentText().strip()
        self.season_combo.blockSignals(True)
        self.season_combo.clear()

        if selected_department != "Agronomy":
            self.season_combo.addItem("Not Required")
            self.season_combo.setEnabled(False)
        elif selected_type == "Assessment":
            self.season_combo.addItems(["Kharif", "Rabi"])
            self.season_combo.setEnabled(True)
        elif selected_type == "Refinement":
            self.season_combo.addItem("Not Required")
            self.season_combo.setEnabled(False)
        else:
            self.season_combo.addItem("Select Activity Type")
            self.season_combo.setEnabled(False)

        self.season_combo.blockSignals(False)

    def _validate_payload(self, payload) -> bool:
        if self.module_name == "Extension Activities":
            required = [
                payload["activity_type"] if self.activity_type_input.currentIndex() > 0 else "",
                payload["activity_date"],
                payload["extension_venue"],
                payload["extension_location"],
                payload["department_id"],
                payload["extension_purpose"],
                payload["extension_farmer_count"],
            ]
            if any(value is None or not str(value).strip() for value in required):
                QMessageBox.warning(self, "Validation", "Please fill all required fields marked with *.")
                return False
            if payload["extension_farmer_count"] <= 0:
                QMessageBox.warning(self, "Validation", "No. of Farmers must be greater than zero.")
                return False
            return True

        if self.module_name == "Other Extension Activities":
            required = [
                payload["activity_type"] if self.activity_type_input.currentIndex() > 0 else "",
                payload["activity_date"],
                payload["department_id"],
                payload["other_extension_title"],
            ]
            if any(value is None or not str(value).strip() for value in required):
                QMessageBox.warning(self, "Validation", "Please fill all required fields marked with *.")
                return False
            return True

        # Training modules have different required fields
        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            if not self.department_combo.currentData():
                QMessageBox.warning(self, "Validation", "Please select Department first.")
                return False
            if payload["training_end_date"] and payload["training_end_date"] < payload["activity_date"]:
                QMessageBox.warning(self, "Validation", "End Date cannot be before Start Date.")
                return False

            required = [
                payload["training_title"],
                payload["village"],
                payload["training_type"],
                payload["clientele"],
                payload["training_farmer_count"],
            ]
            if any(value is None or not str(value).strip() for value in required):
                QMessageBox.warning(self, "Validation", "Please fill all required fields marked with *.")
                return False

            if payload["venue_is_offline"]:
                offline_required = [
                    payload["venue_village"],
                    payload["venue_taluka"] if payload["venue_taluka"] != "Select Taluka" else "",
                    payload["venue_district"] if payload["venue_district"] != "Select District" else "",
                ]
                if any(not value for value in offline_required):
                    QMessageBox.warning(self, "Validation", "Please fill offline venue Village, Taluka, and District.")
                    return False

            if not self.training_farmer_forms:
                QMessageBox.warning(self, "Validation", "Click Show and fill farmer forms before saving.")
                return False
            if payload["training_farmer_count"] != len(self.training_farmer_forms):
                QMessageBox.warning(self, "Validation", "Click Show again after changing No. of Farmers.")
                return False

            return True

        required = [
            payload["farmer_name"],
            payload["village"],
            payload["contact_number"],
        ]

        if self._is_oft_style_module():
            required.extend([payload["description"], self.remarks_input.text().strip()])

        if self.module_name == "Visitor Farmers":
            required.extend(
                [
                    self.tehsil_input.currentText().strip()
                    if self._is_valid_tehsil(self.district_input.currentText().strip(), self.tehsil_input.currentText().strip())
                    else "",
                    self.district_input.currentText().strip()
                    if self._is_valid_district(self.district_input.currentText().strip())
                    else "",
                    self.scientist_input.text().strip(),
                    payload["activity_type"],
                ]
            )

        if self.module_name not in ["Training Programmes", "Vocational Training Programmes"]:
            required.append(payload["activity_type"])
        if any(not x for x in required):
            QMessageBox.warning(self, "Validation", "Please fill all required fields marked with *.")
            return False

        if self._is_oft_style_module():
            if not self.department_combo.currentData():
                QMessageBox.warning(self, "Validation", "Please select Department first.")
                return False
            if self.module_name == "On Farm Testing (OFT)" and hasattr(self, "oft_t1_input"):
                technical_values = [
                    self.oft_t1_input.text().strip(),
                    self.oft_t2_input.text().strip(),
                    self.oft_t3_input.text().strip(),
                ]
                if any(not value for value in technical_values):
                    QMessageBox.warning(self, "Validation", "Please fill technical assessment t1, t2, and t3.")
                    return False
            if payload["activity_type"] != "Assessment":
                QMessageBox.warning(self, "Validation", "Activity Type is fixed to Assessment.")
                return False
            if payload["season"] not in ["Kharif", "Rabi"]:
                QMessageBox.warning(self, "Validation", "Please select Season.")
                return False

        if self._is_oft_style_module():
            if not payload["contact_number"].isdigit():
                QMessageBox.warning(self, "Validation", "No. of Farmers must be numeric.")
                return False
        elif not payload["contact_number"].isdigit() or len(payload["contact_number"]) != 10:
            QMessageBox.warning(self, "Validation", "Mobile number must be exactly 10 digits.")
            return False
        return True

    def _save_record(self) -> None:
        if self._is_oft_style_module():
            self._save_all_oft_records()
            return
        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            self._save_all_training_records()
            return

        payload = self._collect_payload()
        if not self._validate_payload(payload):
            return

        try:
            ActivityService.create_activity(payload, self.current_user.id)
            QMessageBox.information(self, "Saved", "Record saved successfully.")
            self._reset_form()
            self.current_page = 1
            self._load_table()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not save record: {exc}")

    def _save_all_training_records(self) -> None:
        payload = self._collect_payload()
        if not self._validate_payload(payload):
            return

        unsaved_forms = [form for form in self.training_farmer_forms if not form.get("saved")]
        if unsaved_forms:
            first_unsaved = unsaved_forms[0]["index"] + 1
            QMessageBox.warning(self, "Validation", f"Save Farmer Form {first_unsaved} before Save All Training Changes.")
            return

        for form_state in self.training_farmer_forms:
            if not self._validate_training_farmer_form(form_state):
                return

        try:
            for form_state in self.training_farmer_forms:
                farmer_payload = dict(payload)
                district_value = form_state["district"].currentText().strip()
                tehsil_value = form_state["tehsil"].currentText().strip()
                village_value = form_state["village"].currentText().strip()
                farmer_payload["farmer_name"] = form_state["farmer_name"].text().strip()
                farmer_payload["village"] = village_value
                farmer_payload["contact_number"] = form_state["mobile"].text().strip()
                farmer_payload["training_farmer_category"] = form_state["category"].currentText().strip()
                farmer_payload["training_farmer_scientist"] = form_state["scientist"].text().strip()
                farmer_payload["training_farmer_purpose"] = form_state["purpose"].currentText().strip()
                farmer_payload["training_farmer_district"] = district_value
                farmer_payload["training_farmer_tehsil"] = tehsil_value
                ActivityService.create_activity(farmer_payload, self.current_user.id)

            QMessageBox.information(self, "Saved", "Training farmer records saved successfully.")
            self._reset_form()
            self.current_page = 1
            self._load_table()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not save training records: {exc}")

    def _edit_record(self) -> None:
        if not self.selected_activity_id:
            QMessageBox.warning(self, "Selection", "Select a row to edit.")
            return

        if self.module_name == "On Farm Testing (OFT)":
            self._open_oft_edit_dialog()
            return
        if self.module_name == "Front Line Demonstrations (FLD)":
            self._open_fld_edit_dialog()
            return

        payload = self._collect_payload()
        if not self._validate_payload(payload):
            return

        try:
            ActivityService.update_activity(self.selected_activity_id, payload, self.current_user.id)
            QMessageBox.information(self, "Updated", "Record updated successfully.")
            self._reset_form()
            self._load_table()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not update record: {exc}")

    def _open_oft_edit_dialog(self) -> None:
        if self.module_name != "On Farm Testing (OFT)":
            self._open_fld_edit_dialog()
            return

        batch_records = ActivityService.fetch_oft_batch_records(self.selected_activity_id, self.oft_selected_batch_key)
        if not batch_records:
            QMessageBox.warning(self, "Selection", "Could not load OFT data for edit dialog.")
            return

        common = batch_records[0]
        activity_ids = [record["id"] for record in batch_records]
        batch_key = common.get("oft_batch_key", "").strip() or f"OFT-{uuid4().hex[:12]}"

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit OFT Batch")
        dialog.resize(980, 760)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        upper_card = QFrame()
        upper_card.setObjectName("Card")
        upper_form = QFormLayout(upper_card)
        upper_form.setHorizontalSpacing(12)
        upper_form.setVerticalSpacing(8)
        upper_form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        edit_date = QDateEdit()
        edit_date.setCalendarPopup(True)
        date_value = common.get("activity_date")
        if date_value:
            edit_date.setDate(QDate(date_value.year, date_value.month, date_value.day))
        else:
            edit_date.setDate(QDate.currentDate())

        edit_title = QLineEdit(common.get("oft_title", ""))
        edit_crop = QLineEdit(common.get("oft_crop_variety", ""))
        edit_count = QLineEdit(str(common.get("oft_farmer_count") or len(batch_records)))
        edit_count.setReadOnly(True)
        edit_t1_value, edit_t2_value, edit_t3_value = self._parse_oft_technical_assessment(
            common.get("oft_technical_assessment", "")
        )
        edit_technical_widget = QWidget()
        edit_technical_layout = QGridLayout(edit_technical_widget)
        edit_technical_layout.setContentsMargins(0, 0, 0, 0)
        edit_technical_layout.setHorizontalSpacing(8)
        edit_technical_layout.setVerticalSpacing(6)
        edit_t1 = QLineEdit(edit_t1_value)
        edit_t2 = QLineEdit(edit_t2_value)
        edit_t3 = QLineEdit(edit_t3_value)
        for name, widget in (("t1", edit_t1), ("t2", edit_t2), ("t3", edit_t3)):
            widget.setObjectName(name)
            widget.setPlaceholderText(name)
            widget.setMinimumHeight(34)
        edit_technical_layout.addWidget(QLabel("t1"), 0, 0)
        edit_technical_layout.addWidget(edit_t1, 0, 1)
        edit_technical_layout.addWidget(QLabel("t2"), 1, 0)
        edit_technical_layout.addWidget(edit_t2, 1, 1)
        edit_technical_layout.addWidget(QLabel("t3"), 2, 0)
        edit_technical_layout.addWidget(edit_t3, 2, 1)
        edit_technical_layout.setColumnStretch(1, 1)
        edit_area = QLineEdit(common.get("oft_area", ""))

        edit_department = QComboBox()
        edit_department.addItem("Select Department", None)
        for dept in self.departments:
            if dept.name.strip().lower() == "agricultural extension":
                continue
            edit_department.addItem(dept.name, dept.id)
        dept_idx = edit_department.findData(common.get("department_id"))
        if dept_idx >= 0:
            edit_department.setCurrentIndex(dept_idx)

        edit_activity = QComboBox()
        edit_activity.addItems(["Assessment"])

        edit_season = QComboBox()
        edit_season.addItems(["Kharif", "Rabi"])
        season_idx = edit_season.findText(common.get("season", ""))
        if season_idx >= 0:
            edit_season.setCurrentIndex(season_idx)

        upper_form.addRow("Date*", edit_date)
        upper_form.addRow("Title of OFT*", edit_title)
        upper_form.addRow("Crop Variety*", edit_crop)
        upper_form.addRow("No. of Farmers*", edit_count)
        upper_form.addRow("Technical Assessment*", edit_technical_widget)
        upper_form.addRow("Area*", edit_area)
        upper_form.addRow("Department*", edit_department)
        upper_form.addRow("Activity Type*", edit_activity)
        upper_form.addRow("Season*", edit_season)
        content_layout.addWidget(upper_card)

        farmers_title = QLabel("Farmer Details")
        farmers_title.setObjectName("CardTitle")
        content_layout.addWidget(farmers_title)

        dialog_farmer_forms = []
        for index, record in enumerate(batch_records):
            farmer_card = QFrame()
            farmer_card.setObjectName("Card")
            farmer_layout = QFormLayout(farmer_card)
            farmer_layout.setHorizontalSpacing(12)
            farmer_layout.setVerticalSpacing(8)
            farmer_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            farmer_name = QLineEdit(record.get("farmer_name", ""))
            farmer_village = QLineEdit(record.get("village", ""))
            farmer_mobile = QLineEdit(record.get("contact_number", ""))
            self._configure_mobile_input(farmer_mobile)
            farmer_scientist = QLineEdit(record.get("oft_farmer_scientist", ""))
            farmer_purpose = QComboBox()
            farmer_purpose.addItems(["Visitor Entry", "Consultation"])
            purpose_idx = farmer_purpose.findText(record.get("oft_farmer_purpose", ""))
            if purpose_idx >= 0:
                farmer_purpose.setCurrentIndex(purpose_idx)

            farmer_district = QComboBox()
            farmer_district.setEditable(True)
            farmer_district.addItem("Select District", None)
            for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
                farmer_district.addItem(district_name, district_name)
            self._configure_searchable_combo(farmer_district)
            district_text = record.get("oft_farmer_district", "")
            district_idx = farmer_district.findText(district_text)
            if district_idx >= 0:
                farmer_district.setCurrentIndex(district_idx)
            elif district_text:
                farmer_district.setEditText(district_text)

            farmer_tehsil = QComboBox()
            farmer_tehsil.setEditable(True)
            farmer_tehsil.addItem("Select Tehsil", None)
            self._configure_searchable_combo(farmer_tehsil)

            def _refresh_edit_tehsils(_idx: int = -1, district_combo=farmer_district, tehsil_combo=farmer_tehsil, selected_text=record.get("oft_farmer_tehsil", "")) -> None:
                district_value = district_combo.currentText().strip()
                tehsil_combo.blockSignals(True)
                tehsil_combo.clear()
                tehsil_combo.addItem("Select Tehsil", None)
                if self._is_valid_district(district_value):
                    for tehsil_name in MH_DISTRICT_TEHSILS.get(district_value, []):
                        tehsil_combo.addItem(tehsil_name, tehsil_name)
                    tehsil_combo.setEnabled(True)
                else:
                    tehsil_combo.setEnabled(False)
                if selected_text:
                    text_idx = tehsil_combo.findText(selected_text)
                    if text_idx >= 0:
                        tehsil_combo.setCurrentIndex(text_idx)
                    else:
                        tehsil_combo.setEditText(selected_text)
                else:
                    tehsil_combo.setCurrentIndex(0)
                tehsil_combo.blockSignals(False)

            _refresh_edit_tehsils()
            farmer_district.currentIndexChanged.connect(_refresh_edit_tehsils)

            farmer_layout.addRow(f"Farmer {index + 1} Name*", farmer_name)
            farmer_layout.addRow("Farmer Village*", farmer_village)
            farmer_layout.addRow("Mobile No.*", farmer_mobile)
            farmer_layout.addRow("Scientist*", farmer_scientist)
            farmer_layout.addRow("Purpose*", farmer_purpose)
            farmer_layout.addRow("District*", farmer_district)
            farmer_layout.addRow("Tehsil*", farmer_tehsil)

            dialog_farmer_forms.append(
                {
                    "farmer_name": farmer_name,
                    "village": farmer_village,
                    "mobile": farmer_mobile,
                    "scientist": farmer_scientist,
                    "purpose": farmer_purpose,
                    "district": farmer_district,
                    "tehsil": farmer_tehsil,
                }
            )
            content_layout.addWidget(farmer_card)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        root.addWidget(buttons)
        buttons.rejected.connect(dialog.reject)

        def _save_dialog_changes() -> None:
            technical_assessment_value = self._compose_oft_technical_assessment(
                edit_t1.text(),
                edit_t2.text(),
                edit_t3.text(),
            )
            if not edit_title.text().strip() or not edit_crop.text().strip() or not technical_assessment_value or not edit_area.text().strip():
                QMessageBox.warning(dialog, "Validation", "Please fill all required OFT upper fields, including t1, t2, and t3.")
                return
            if edit_department.currentData() is None:
                QMessageBox.warning(dialog, "Validation", "Please select Department.")
                return

            try:
                for index, form in enumerate(dialog_farmer_forms):
                    farmer_name = form["farmer_name"].text().strip()
                    village = form["village"].text().strip()
                    mobile = form["mobile"].text().strip()
                    scientist = form["scientist"].text().strip()
                    purpose = form["purpose"].currentText().strip()
                    district = form["district"].currentText().strip()
                    tehsil = form["tehsil"].currentText().strip()

                    if not farmer_name or not village or not scientist or not purpose:
                        QMessageBox.warning(dialog, "Validation", f"Please fill all farmer fields in Farmer Form {index + 1}.")
                        return
                    if not mobile.isdigit() or len(mobile) != 10:
                        QMessageBox.warning(dialog, "Validation", f"Enter exactly 10 digits for mobile number in Farmer Form {index + 1}.")
                        return
                    if not self._is_valid_district(district) or not self._is_valid_tehsil(district, tehsil):
                        QMessageBox.warning(dialog, "Validation", f"Select valid district/tehsil in Farmer Form {index + 1}.")
                        return

                    payload = {
                        "module_type": self.module_name,
                        "farmer_name": farmer_name,
                        "village": village,
                        "contact_number": mobile,
                        "activity_date": edit_date.date().toPyDate(),
                        "department_id": edit_department.currentData(),
                        "season": edit_season.currentText().strip(),
                        "activity_type": edit_activity.currentText().strip(),
                        "description": technical_assessment_value,
                        "remarks": f"OFT_META|District: {district}|Tehsil: {tehsil}",
                        "oft_title": edit_title.text().strip(),
                        "oft_batch_key": batch_key,
                        "oft_crop_variety": edit_crop.text().strip(),
                        "oft_farmer_count": len(dialog_farmer_forms),
                        "oft_technical_assessment": technical_assessment_value,
                        "oft_area": edit_area.text().strip(),
                        "oft_farmer_scientist": scientist,
                        "oft_farmer_purpose": purpose,
                        "oft_farmer_district": district,
                        "oft_farmer_tehsil": tehsil,
                    }
                    ActivityService.update_activity(activity_ids[index], payload, self.current_user.id)

                QMessageBox.information(dialog, "Updated", "OFT batch updated successfully.")
                dialog.accept()
                self._reset_form()
                self._load_table()
            except Exception as exc:
                QMessageBox.critical(dialog, "Error", f"Could not update OFT batch: {exc}")

        buttons.accepted.connect(_save_dialog_changes)
        dialog.exec_()

    def _open_fld_edit_dialog(self) -> None:
        if self.module_name != "Front Line Demonstrations (FLD)":
            return
        if not self.selected_activity_id:
            QMessageBox.warning(self, "Selection", "Select an FLD row first.")
            return

        batch_records = ActivityService.fetch_oft_batch_records(self.selected_activity_id, "")
        if not batch_records:
            QMessageBox.warning(self, "Selection", "Could not load FLD data for edit dialog.")
            return

        common = batch_records[0]
        activity_ids = [record["id"] for record in batch_records]

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit FLD Batch")
        dialog.resize(980, 760)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        upper_card = QFrame()
        upper_card.setObjectName("Card")
        upper_form = QFormLayout(upper_card)
        upper_form.setHorizontalSpacing(12)
        upper_form.setVerticalSpacing(8)
        upper_form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        edit_date = QDateEdit()
        edit_date.setCalendarPopup(True)
        date_value = common.get("activity_date")
        if date_value:
            edit_date.setDate(QDate(date_value.year, date_value.month, date_value.day))
        else:
            edit_date.setDate(QDate.currentDate())

        edit_title = QLineEdit(common.get("oft_title", ""))
        edit_crop = QLineEdit(common.get("oft_crop_variety", ""))
        edit_count = QLineEdit(str(common.get("oft_farmer_count") or len(batch_records)))
        edit_count.setReadOnly(True)
        edit_area = QLineEdit(common.get("oft_area", ""))

        edit_department = QComboBox()
        edit_department.addItem("Select Department", None)
        for dept in self.departments:
            if dept.name.strip().lower() == "agricultural extension":
                continue
            edit_department.addItem(dept.name, dept.id)
        dept_idx = edit_department.findData(common.get("department_id"))
        if dept_idx >= 0:
            edit_department.setCurrentIndex(dept_idx)

        edit_activity = QComboBox()
        edit_activity.addItems(["Demonstration"])

        edit_season = QComboBox()
        edit_season.addItems(["Kharif", "Rabi"])
        season_idx = edit_season.findText(common.get("season", ""))
        if season_idx >= 0:
            edit_season.setCurrentIndex(season_idx)

        upper_form.addRow("Date*", edit_date)
        upper_form.addRow("Title of FLD*", edit_title)
        upper_form.addRow("Crop Variety*", edit_crop)
        upper_form.addRow("No. of Farmers*", edit_count)
        upper_form.addRow("Area*", edit_area)
        upper_form.addRow("Department*", edit_department)
        upper_form.addRow("Activity Type*", edit_activity)
        upper_form.addRow("Season*", edit_season)
        content_layout.addWidget(upper_card)

        farmers_title = QLabel("Farmer Details")
        farmers_title.setObjectName("CardTitle")
        content_layout.addWidget(farmers_title)

        dialog_farmer_forms = []
        for index, record in enumerate(batch_records):
            farmer_card = QFrame()
            farmer_card.setObjectName("Card")
            farmer_layout = QFormLayout(farmer_card)
            farmer_layout.setHorizontalSpacing(12)
            farmer_layout.setVerticalSpacing(8)
            farmer_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            farmer_name = QLineEdit(record.get("farmer_name", ""))
            farmer_village = QLineEdit(record.get("village", ""))
            farmer_mobile = QLineEdit(record.get("contact_number", ""))
            self._configure_mobile_input(farmer_mobile)
            farmer_scientist = QLineEdit(record.get("oft_farmer_scientist", ""))
            farmer_purpose = QComboBox()
            farmer_purpose.addItems(["Visitor Entry", "Consultation"])
            purpose_idx = farmer_purpose.findText(record.get("oft_farmer_purpose", ""))
            if purpose_idx >= 0:
                farmer_purpose.setCurrentIndex(purpose_idx)

            farmer_district = QComboBox()
            farmer_district.setEditable(True)
            farmer_district.addItem("Select District", None)
            for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
                farmer_district.addItem(district_name, district_name)
            self._configure_searchable_combo(farmer_district)
            district_text = record.get("oft_farmer_district", "")
            district_idx = farmer_district.findText(district_text)
            if district_idx >= 0:
                farmer_district.setCurrentIndex(district_idx)
            elif district_text:
                farmer_district.setEditText(district_text)

            farmer_tehsil = QComboBox()
            farmer_tehsil.setEditable(True)
            farmer_tehsil.addItem("Select Tehsil", None)
            self._configure_searchable_combo(farmer_tehsil)

            def _refresh_edit_tehsils(_idx: int = -1, district_combo=farmer_district, tehsil_combo=farmer_tehsil, selected_text=record.get("oft_farmer_tehsil", "")) -> None:
                district_value = district_combo.currentText().strip()
                tehsil_combo.blockSignals(True)
                tehsil_combo.clear()
                tehsil_combo.addItem("Select Tehsil", None)
                if self._is_valid_district(district_value):
                    for tehsil_name in MH_DISTRICT_TEHSILS.get(district_value, []):
                        tehsil_combo.addItem(tehsil_name, tehsil_name)
                    tehsil_combo.setEnabled(True)
                else:
                    tehsil_combo.setEnabled(False)
                if selected_text:
                    text_idx = tehsil_combo.findText(selected_text)
                    if text_idx >= 0:
                        tehsil_combo.setCurrentIndex(text_idx)
                    else:
                        tehsil_combo.setEditText(selected_text)
                else:
                    tehsil_combo.setCurrentIndex(0)
                tehsil_combo.blockSignals(False)

            _refresh_edit_tehsils()
            farmer_district.currentIndexChanged.connect(_refresh_edit_tehsils)

            farmer_layout.addRow(f"Farmer {index + 1} Name*", farmer_name)
            farmer_layout.addRow("Farmer Village*", farmer_village)
            farmer_layout.addRow("Mobile No.*", farmer_mobile)
            farmer_layout.addRow("Scientist*", farmer_scientist)
            farmer_layout.addRow("Purpose*", farmer_purpose)
            farmer_layout.addRow("District*", farmer_district)
            farmer_layout.addRow("Tehsil*", farmer_tehsil)

            dialog_farmer_forms.append(
                {
                    "farmer_name": farmer_name,
                    "village": farmer_village,
                    "mobile": farmer_mobile,
                    "scientist": farmer_scientist,
                    "purpose": farmer_purpose,
                    "district": farmer_district,
                    "tehsil": farmer_tehsil,
                }
            )
            content_layout.addWidget(farmer_card)

        content_layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        root.addWidget(buttons)
        buttons.rejected.connect(dialog.reject)

        def _save_fld_dialog_changes() -> None:
            if not edit_title.text().strip() or not edit_crop.text().strip() or not edit_area.text().strip():
                QMessageBox.warning(dialog, "Validation", "Please fill all required FLD upper fields.")
                return
            if edit_department.currentData() is None:
                QMessageBox.warning(dialog, "Validation", "Please select Department.")
                return

            try:
                for index, form in enumerate(dialog_farmer_forms):
                    farmer_name = form["farmer_name"].text().strip()
                    village = form["village"].text().strip()
                    mobile = form["mobile"].text().strip()
                    scientist = form["scientist"].text().strip()
                    purpose = form["purpose"].currentText().strip()
                    district = form["district"].currentText().strip()
                    tehsil = form["tehsil"].currentText().strip()

                    if not farmer_name or not village or not scientist or not purpose:
                        QMessageBox.warning(dialog, "Validation", f"Please fill all farmer fields in Farmer Form {index + 1}.")
                        return
                    if not mobile.isdigit() or len(mobile) != 10:
                        QMessageBox.warning(dialog, "Validation", f"Enter exactly 10 digits for mobile number in Farmer Form {index + 1}.")
                        return
                    if not self._is_valid_district(district) or not self._is_valid_tehsil(district, tehsil):
                        QMessageBox.warning(dialog, "Validation", f"Select valid district/tehsil in Farmer Form {index + 1}.")
                        return

                    payload = {
                        "module_type": self.module_name,
                        "farmer_name": farmer_name,
                        "village": village,
                        "contact_number": mobile,
                        "activity_date": edit_date.date().toPyDate(),
                        "department_id": edit_department.currentData(),
                        "season": edit_season.currentText().strip(),
                        "activity_type": edit_activity.currentText().strip(),
                        "description": "",
                        "remarks": f"OFT_META|District: {district}|Tehsil: {tehsil}",
                        "oft_title": edit_title.text().strip(),
                        "oft_batch_key": common.get("oft_batch_key", ""),
                        "oft_crop_variety": edit_crop.text().strip(),
                        "oft_farmer_count": len(dialog_farmer_forms),
                        "oft_technical_assessment": "",
                        "oft_area": edit_area.text().strip(),
                        "oft_farmer_scientist": scientist,
                        "oft_farmer_purpose": purpose,
                        "oft_farmer_district": district,
                        "oft_farmer_tehsil": tehsil,
                    }
                    ActivityService.update_activity(activity_ids[index], payload, self.current_user.id)

                QMessageBox.information(dialog, "Updated", "FLD batch updated successfully.")
                dialog.accept()
                self._reset_form()
                self._load_table()
            except Exception as exc:
                QMessageBox.critical(dialog, "Error", f"Could not update FLD batch: {exc}")

        buttons.accepted.connect(_save_fld_dialog_changes)
        dialog.exec_()

    def _open_visitor_farmers_edit_dialog(self) -> None:
        if self.module_name != "Visitor Farmers":
            return
        if not self.selected_activity_id:
            QMessageBox.warning(self, "Selection", "Select a Visitor Farmers row to edit.")
            return

        row_data = self._table_row_records[self.table.currentRow()] if self.table.currentRow() < len(self._table_row_records) else None
        if not row_data:
            QMessageBox.warning(self, "Selection", "Could not load Visitor Farmers record.")
            return

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit Visitor Farmer")
        dialog.resize(600, 700)

        root = QVBoxLayout(dialog)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(10)

        farmer_card = QFrame()
        farmer_card.setObjectName("Card")
        farmer_layout = QFormLayout(farmer_card)
        farmer_layout.setHorizontalSpacing(12)
        farmer_layout.setVerticalSpacing(8)
        farmer_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        edit_date = QDateEdit()
        edit_date.setCalendarPopup(True)
        date_value = row_data.get("activity_date")
        if date_value:
            if hasattr(date_value, 'year'):
                edit_date.setDate(QDate(date_value.year, date_value.month, date_value.day))
            else:
                edit_date.setDate(QDate.fromString(str(date_value), "yyyy-MM-dd"))
        else:
            edit_date.setDate(QDate.currentDate())

        edit_farmer_name = QLineEdit(row_data.get("farmer_name", ""))
        edit_mobile = QLineEdit(row_data.get("contact_number", ""))
        self._configure_mobile_input(edit_mobile)
        edit_scientist = QLineEdit(row_data.get("visitor_scientist", "") or row_data.get("description", ""))
        edit_village = QLineEdit(row_data.get("village", ""))

        edit_department = QComboBox()
        edit_department.addItem("Select Department", None)
        for dept in self.departments:
            edit_department.addItem(dept.name, dept.id)
        dept_idx = edit_department.findData(row_data.get("department_id"))
        if dept_idx >= 0:
            edit_department.setCurrentIndex(dept_idx)

        edit_activity = QComboBox()
        edit_activity.addItems(["Visitor Entry", "Consultation"])
        activity_idx = edit_activity.findText(row_data.get("activity_type", ""))
        if activity_idx >= 0:
            edit_activity.setCurrentIndex(activity_idx)

        edit_district = QComboBox()
        edit_district.setEditable(True)
        edit_district.addItem("Select District", None)
        for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
            edit_district.addItem(district_name, district_name)
        self._configure_searchable_combo(edit_district)
        
        district_value = row_data.get("district", "")
        district_idx = edit_district.findText(district_value)
        if district_idx >= 0:
            edit_district.setCurrentIndex(district_idx)
        elif district_value:
            edit_district.setEditText(district_value)

        edit_tehsil = QComboBox()
        edit_tehsil.setEditable(True)
        edit_tehsil.addItem("Select Tehsil", None)
        self._configure_searchable_combo(edit_tehsil)

        def _refresh_edit_tehsils(_idx: int = -1, district_combo=edit_district, tehsil_combo=edit_tehsil, selected_text=row_data.get("tehsil", "")) -> None:
            district_value = district_combo.currentText().strip()
            tehsil_combo.blockSignals(True)
            tehsil_combo.clear()
            tehsil_combo.addItem("Select Tehsil", None)
            if self._is_valid_district(district_value):
                for tehsil_name in MH_DISTRICT_TEHSILS.get(district_value, []):
                    tehsil_combo.addItem(tehsil_name, tehsil_name)
                tehsil_combo.setEnabled(True)
            else:
                tehsil_combo.setEnabled(False)
            if selected_text:
                text_idx = tehsil_combo.findText(selected_text)
                if text_idx >= 0:
                    tehsil_combo.setCurrentIndex(text_idx)
                else:
                    tehsil_combo.setEditText(selected_text)
            else:
                tehsil_combo.setCurrentIndex(0)
            tehsil_combo.blockSignals(False)

        _refresh_edit_tehsils()
        edit_district.currentIndexChanged.connect(_refresh_edit_tehsils)

        farmer_layout.addRow("Date*", edit_date)
        farmer_layout.addRow("Name of Farmer*", edit_farmer_name)
        farmer_layout.addRow("Mobile No.*", edit_mobile)
        farmer_layout.addRow("Name of Scientist*", edit_scientist)
        farmer_layout.addRow("Village*", edit_village)
        farmer_layout.addRow("District*", edit_district)
        farmer_layout.addRow("Tehsil*", edit_tehsil)
        farmer_layout.addRow("Department*", edit_department)
        farmer_layout.addRow("Purpose*", edit_activity)

        content_layout.addWidget(farmer_card)
        content_layout.addStretch(1)
        scroll.setWidget(content)
        root.addWidget(scroll)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        root.addWidget(buttons)
        buttons.rejected.connect(dialog.reject)

        def _save_visitor_dialog_changes() -> None:
            farmer_name = edit_farmer_name.text().strip()
            mobile = edit_mobile.text().strip()
            scientist = edit_scientist.text().strip()
            village = edit_village.text().strip()
            district = edit_district.currentText().strip()
            tehsil = edit_tehsil.currentText().strip()
            activity = edit_activity.currentText().strip()

            if not farmer_name or not mobile or not scientist or not village or not activity:
                QMessageBox.warning(dialog, "Validation", "Please fill all required fields.")
                return
            if not mobile.isdigit() or len(mobile) != 10:
                QMessageBox.warning(dialog, "Validation", "Enter exactly 10 digits for mobile number.")
                return
            if edit_department.currentData() is None:
                QMessageBox.warning(dialog, "Validation", "Please select Department.")
                return
            if not self._is_valid_district(district):
                QMessageBox.warning(dialog, "Validation", "Please select valid District.")
                return
            if not self._is_valid_tehsil(district, tehsil):
                QMessageBox.warning(dialog, "Validation", "Please select valid Tehsil.")
                return

            try:
                payload = {
                    "module_type": self.module_name,
                    "farmer_name": farmer_name,
                    "village": village,
                    "contact_number": mobile,
                    "activity_date": edit_date.date().toPyDate(),
                    "department_id": edit_department.currentData(),
                    "season": "Kharif",
                    "activity_type": activity,
                    "description": "",
                    "remarks": f"District: {district}|Tehsil: {tehsil}",
                    "visitor_scientist": scientist,
                    "visitor_district": district,
                    "visitor_tehsil": tehsil,
                }
                ActivityService.update_activity(self.selected_activity_id, payload, self.current_user.id)
                QMessageBox.information(dialog, "Updated", "Visitor Farmer record updated successfully.")
                dialog.accept()
                self._reset_form()
                self._load_table()
            except Exception as exc:
                QMessageBox.critical(dialog, "Error", f"Could not update Visitor Farmer record: {exc}")

        buttons.accepted.connect(_save_visitor_dialog_changes)
        dialog.exec_()

    def _edit_oft_batch_records(self) -> None:
        common_payload = self._collect_oft_common_payload()
        if common_payload is None:
            return

        if not self.oft_selected_activity_ids:
            QMessageBox.warning(self, "Selection", "No OFT batch selected for edit.")
            return

        if len(self.oft_farmer_forms) != len(self.oft_selected_activity_ids):
            QMessageBox.warning(self, "Validation", "Farmer form count does not match saved OFT batch.")
            return

        unsaved_forms = [form_state for form_state in self.oft_farmer_forms if not form_state.get("saved")]
        if unsaved_forms:
            first_unsaved = unsaved_forms[0]["index"] + 1
            QMessageBox.warning(self, "Validation", f"Save Farmer Form {first_unsaved} before editing all records.")
            return

        try:
            for idx, form_state in enumerate(self.oft_farmer_forms):
                district_value = form_state["district"].currentText().strip()
                tehsil_value = form_state["tehsil"].currentText().strip()
                village_value = form_state["village"].currentText().strip()
                scientist_value = form_state["scientist"].text().strip()
                purpose_value = form_state["purpose"].currentText().strip()

                payload = {
                    "module_type": self.module_name,
                    "farmer_name": form_state["farmer_name"].text().strip(),
                    "village": village_value,
                    "contact_number": form_state["mobile"].text().strip(),
                    "activity_date": common_payload["activity_date"],
                    "department_id": common_payload["department_id"],
                    "season": common_payload["season"],
                    "activity_type": common_payload["activity_type"],
                    "description": common_payload["description"],
                    "remarks": f"OFT_META|District: {district_value}|Tehsil: {tehsil_value}",
                    "oft_title": common_payload["farmer_name"],
                    "oft_batch_key": self.oft_selected_batch_key,
                    "oft_crop_variety": common_payload["village"],
                    "oft_farmer_count": int(common_payload["contact_number"]),
                    "oft_technical_assessment": common_payload["description"],
                    "oft_area": common_payload["remarks"],
                    "oft_farmer_scientist": scientist_value,
                    "oft_farmer_purpose": purpose_value,
                    "oft_farmer_district": district_value,
                    "oft_farmer_tehsil": tehsil_value,
                }
                ActivityService.update_activity(self.oft_selected_activity_ids[idx], payload, self.current_user.id)

            QMessageBox.information(self, "Updated", "All OFT farmer records updated successfully.")
            self._reset_form()
            self._load_table()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not update OFT records: {exc}")

    def _delete_record(self) -> None:
        if not self.selected_activity_id:
            QMessageBox.warning(self, "Selection", "Select a row to delete.")
            return

        if self._is_oft_style_module() and self.oft_selected_activity_ids:
            module_short = "OFT" if self.module_name == "On Farm Testing (OFT)" else "FLD"
            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Delete selected {module_short} batch ({len(self.oft_selected_activity_ids)} farmer records)?",
            )
        else:
            confirm = QMessageBox.question(self, "Confirm Delete", "Delete selected record?")
        if confirm != QMessageBox.Yes:
            return

        try:
            if self._is_oft_style_module() and self.oft_selected_activity_ids:
                for activity_id in self.oft_selected_activity_ids:
                    ActivityService.delete_activity(activity_id, self.current_user.id)
                module_short = "OFT" if self.module_name == "On Farm Testing (OFT)" else "FLD"
                QMessageBox.information(self, "Deleted", f"Selected {module_short} batch deleted successfully.")
            else:
                ActivityService.delete_activity(self.selected_activity_id, self.current_user.id)
                QMessageBox.information(self, "Deleted", "Record deleted successfully.")
            self._reset_form()
            self._load_table()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not delete record: {exc}")

    def _reset_form(self) -> None:
        self.selected_activity_id = None
        self.oft_selected_activity_ids = []
        self.oft_selected_batch_key = ""
        if hasattr(self, "oft_table_edit_btn"):
            self.oft_table_edit_btn.setEnabled(False)
        if hasattr(self, "oft_table_delete_btn"):
            self.oft_table_delete_btn.setEnabled(False)
        if hasattr(self, "table_delete_btn") and self.table_delete_btn is not None:
            self.table_delete_btn.setEnabled(False)
        
        if self.module_name == "Extension Activities":
            self.activity_type_input.setCurrentIndex(0)
            self.date_input.setDate(QDate.currentDate())
            self.extension_venue_input.clear()
            self.extension_location_input.clear()
            ext_idx = self.department_combo.findText("Agricultural Extension")
            self.department_combo.setCurrentIndex(ext_idx if ext_idx >= 0 else 0)
            self.extension_purpose_input.clear()
            self.extension_farmer_count_input.clear()
            self._on_extension_activity_changed()
        elif self.module_name == "Other Extension Activities":
            self.activity_type_input.setCurrentIndex(0)
            self.date_input.setDate(QDate.currentDate())
            self.other_extension_title_input.clear()
            ext_idx = self.department_combo.findText("Agricultural Extension")
            self.department_combo.setCurrentIndex(ext_idx if ext_idx >= 0 else 0)
            self._on_other_extension_activity_changed()
        elif self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            # Reset training form
            self.training_type_combo.setCurrentIndex(0 if self.module_name == "Training Programmes" else 1)
            self.department_combo.setCurrentIndex(0)
            self.date_input.setDate(QDate.currentDate())
            self.end_date_input.setDate(QDate.currentDate())
            self.farmer_name_input.clear()
            self.clientele_input.setCurrentIndex(0)
            self.village_input.setText("KVK")
            self.venue_on_radio.setChecked(True)
            self._update_training_venue_mode()
            self.venue_offline_village_input.clear()
            self.venue_offline_taluka_input.setCurrentIndex(0)
            self.venue_offline_district_input.setCurrentIndex(0)
            self.training_farmer_count_input.clear()
            self.description_input.clear()
            self.remarks_input.clear()
            
            # Clear farmer forms
            while self.training_farmer_boxes_layout.count():
                item = self.training_farmer_boxes_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.training_farmer_forms = []
            self.training_boxes_visible = False
            if hasattr(self, "training_farmer_boxes_card"):
                self.training_farmer_boxes_card.hide()
            if hasattr(self, "training_boxes_scroll"):
                self.training_boxes_scroll.hide()
            if hasattr(self, "training_saved_summary_label"):
                self.training_saved_summary_label.setText("Saved farmer forms: 0")
            self._update_training_form_visibility()
        elif hasattr(self, "farmer_name_input"):
            self.farmer_name_input.clear()
        
        if hasattr(self, "contact_input"):
            self.contact_input.clear()
        
        if hasattr(self, "date_input"):
            self.date_input.setDate(QDate.currentDate())
        
        if self.module_name not in ["Extension Activities", "Other Extension Activities"]:
            self.department_combo.setCurrentIndex(0)
        if hasattr(self, "activity_type_input") and self.module_name not in ["Extension Activities", "Other Extension Activities"]:
            self._refresh_activity_type_options()
            self._refresh_season_options()
            if self.activity_type_input.count() > 0:
                self.activity_type_input.setCurrentIndex(0)

        if self.module_name == "Visitor Farmers":
            self.district_input.setCurrentIndex(0)
            self._on_district_changed()
            self.scientist_input.clear()
            if hasattr(self.village_input, "setCurrentIndex"):
                self.village_input.setCurrentIndex(-1)
        elif self._is_oft_style_module():
            self.season_combo.setCurrentIndex(0)
            self.farmer_name_input.clear()
            self.village_input.clear()
            self.contact_input.clear()
            if self.module_name == "On Farm Testing (OFT)":
                self._clear_oft_technical_assessment()
            while self.oft_farmer_boxes_layout.count():
                item = self.oft_farmer_boxes_layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
            self.oft_farmer_forms = []
            self.current_farmer_index = 0
            self.oft_boxes_visible = False
            if hasattr(self, "oft_farmer_boxes_card"):
                self.oft_farmer_boxes_card.hide()
            if hasattr(self, "oft_boxes_scroll"):
                self.oft_boxes_scroll.hide()
            if hasattr(self, "oft_saved_summary_label"):
                self.oft_saved_summary_label.setText("Saved farmer forms: 0")
        elif self.module_name not in ["Training Programmes", "Vocational Training Programmes", "Extension Activities", "Other Extension Activities"]:
            if hasattr(self.village_input, "setCurrentIndex"):
                self.village_input.setCurrentIndex(-1)
            if hasattr(self, "description_input"):
                self.description_input.clear()
            if hasattr(self, "remarks_input"):
                self.remarks_input.clear()
            if self.module_name == "Front Line Demonstrations (FLD)":
                self._clear_fld_technical_assessment()

        self._load_table()

    def _on_filter_date_mode_changed(self, mode: str) -> None:
        show_custom = mode == "Custom Range"
        self.filter_from_date.setVisible(show_custom)
        self.filter_to_date.setVisible(show_custom)

    def _current_filters(self) -> dict:
        mode = self.filter_date_mode_combo.currentText()
        start_date = None
        end_date = None

        if mode == "Today":
            today = QDate.currentDate().toPyDate()
            start_date = today
            end_date = today
        elif mode == "Last 7 Days":
            end_date = QDate.currentDate().toPyDate()
            start_date = end_date - timedelta(days=7)
        elif mode == "Last 30 Days":
            end_date = QDate.currentDate().toPyDate()
            start_date = end_date - timedelta(days=30)
        elif mode == "Custom Range":
            start_date = self.filter_from_date.date().toPyDate()
            end_date = self.filter_to_date.date().toPyDate()

        return {
            "search_text": self.search_input.text().strip(),
            "department_id": self.filter_department_combo.currentData(),
            "season": self.filter_season_combo.currentText(),
            "start_date": start_date,
            "end_date": end_date,
        }

    def _apply_filters(self) -> None:
        self.current_page = 1
        self._load_table()

    def _clear_filters(self) -> None:
        self.search_input.clear()
        self.filter_department_combo.setCurrentIndex(0)
        self.filter_season_combo.setCurrentIndex(0)
        self.filter_date_mode_combo.setCurrentIndex(0)
        self.filter_from_date.setDate(QDate.currentDate().addDays(-30))
        self.filter_to_date.setDate(QDate.currentDate())
        self.current_page = 1
        self._load_table()

    def _on_row_selected(self, row: int, _column: int) -> None:
        row_data = self._table_row_records[row] if row < len(self._table_row_records) else None
        self.selected_activity_id = int(row_data["id"]) if row_data else None
        if hasattr(self, "oft_table_edit_btn"):
            self.oft_table_edit_btn.setEnabled(True)
        if hasattr(self, "oft_table_delete_btn"):
            self.oft_table_delete_btn.setEnabled(True)
        if hasattr(self, "table_edit_btn") and self.table_edit_btn is not None:
            self.table_edit_btn.setEnabled(True)
        if hasattr(self, "table_delete_btn") and self.table_delete_btn is not None:
            self.table_delete_btn.setEnabled(True)
        
        if self.module_name == "Extension Activities":
            if row_data:
                activity_idx = self.activity_type_input.findText(row_data.get("activity_type", ""))
                if activity_idx >= 0:
                    self.activity_type_input.setCurrentIndex(activity_idx)
                self.date_input.setDate(QDate.fromString(str(row_data["activity_date"]), "yyyy-MM-dd"))
                self.extension_venue_input.setText(row_data.get("extension_venue", ""))
                self.extension_location_input.setText(row_data.get("extension_location", ""))
                department_name = row_data.get("extension_department", "") or row_data.get("department", "")
                dept_idx = self.department_combo.findText(department_name)
                if dept_idx >= 0:
                    self.department_combo.setCurrentIndex(dept_idx)
                self.extension_purpose_input.setPlainText(row_data.get("extension_purpose", "") or row_data.get("description", ""))
                farmer_count = row_data.get("extension_farmer_count")
                self.extension_farmer_count_input.setText(str(farmer_count or ""))
                self._on_extension_activity_changed()
            return

        if self.module_name == "Other Extension Activities":
            if row_data:
                activity_idx = self.activity_type_input.findText(row_data.get("activity_type", ""))
                if activity_idx >= 0:
                    self.activity_type_input.setCurrentIndex(activity_idx)
                self.date_input.setDate(QDate.fromString(str(row_data["activity_date"]), "yyyy-MM-dd"))
                self.other_extension_title_input.setText(
                    row_data.get("other_extension_title", "") or row_data.get("description", "")
                )
                self._on_other_extension_activity_changed()
            return

        # Training Programmes and Vocational Training Programmes
        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            if row_data:
                # Load training data from the selected farmer row.
                self.farmer_name_input.setText(self.table.item(row, 1).text())  # Title
                
                department_name = self.table.item(row, 5).text()
                idx = self.department_combo.findText(department_name)
                if idx >= 0:
                    self.department_combo.setCurrentIndex(idx)
                
                training_type = self.table.item(row, 6).text()
                type_idx = self.training_type_combo.findText(training_type)
                if type_idx >= 0:
                    self.training_type_combo.setCurrentIndex(type_idx)
                
                # Date
                self.date_input.setDate(QDate.fromString(self.table.item(row, 4).text(), "yyyy-MM-dd"))
                end_date = row_data.get("training_end_date")
                if end_date:
                    self.end_date_input.setDate(QDate(end_date.year, end_date.month, end_date.day))
                else:
                    self.end_date_input.setDate(self.date_input.date())
                
                # Venue
                venue = self.table.item(row, 2).text()
                self.village_input.setText(venue)
                if row_data.get("venue_is_offline"):
                    self.venue_off_radio.setChecked(True)
                else:
                    self.venue_on_radio.setChecked(True)
                self._update_training_venue_mode()
                if row_data.get("venue_is_offline"):
                    self.venue_offline_village_input.setText(row_data.get("venue_village", ""))
                    district_idx = self.venue_offline_district_input.findText(row_data.get("venue_district", ""))
                    self.venue_offline_district_input.setCurrentIndex(district_idx if district_idx >= 0 else 0)
                    taluka_idx = self.venue_offline_taluka_input.findText(row_data.get("venue_taluka", ""))
                    self.venue_offline_taluka_input.setCurrentIndex(taluka_idx if taluka_idx >= 0 else 0)

                clientele = row_data.get("clientele", "")
                clientele_idx = self.clientele_input.findText(clientele)
                self.clientele_input.setCurrentIndex(clientele_idx if clientele_idx >= 0 else 0)
                
                # Farmers count
                self.training_farmer_count_input.setText(str(row_data.get("training_farmer_count") or ""))
                
                # Description and Remarks
                self.description_input.setPlainText(row_data.get("description", ""))
                self.remarks_input.setPlainText(row_data.get("remarks", ""))
        elif self.module_name != "Visitor Farmers" and not self._is_oft_style_module():
            self.farmer_name_input.setText(self.table.item(row, 1).text())
            village_value = self.table.item(row, 2).text().strip()
            self.contact_input.setText(self.table.item(row, 3).text())
            self.date_input.setDate(QDate.fromString(self.table.item(row, 4).text(), "yyyy-MM-dd"))

            department_name = self.table.item(row, 5).text()
            idx = self.department_combo.findText(department_name)
            if idx >= 0:
                self.department_combo.setCurrentIndex(idx)

            self._refresh_activity_type_options()
            self._update_oft_form_visibility()
        else:
            self._refresh_activity_type_options()
            self._update_oft_form_visibility()
        if self._is_oft_style_module():
            oft_batch_key = (row_data or {}).get("oft_batch_key", "").strip() if row_data else ""
            batch_records = ActivityService.fetch_oft_batch_records(self.selected_activity_id, oft_batch_key)
            if not batch_records:
                batch_records = [row_data] if row_data else []

            if not batch_records:
                QMessageBox.warning(self, "Selection", "Could not load OFT farmer records.")
                return

            common = batch_records[0]
            self.oft_selected_activity_ids = [record["id"] for record in batch_records]
            self.oft_selected_batch_key = common.get("oft_batch_key", "")
        elif self.module_name not in ["Training Programmes", "Vocational Training Programmes"]:
            # For other modules: Season is at column 6, Activity at column 7
            activity_type = self.table.item(row, 7).text()
            if self.module_name != "Front Line Demonstrations (FLD)":
                type_idx = self.activity_type_input.findText(activity_type)
                if type_idx >= 0:
                    self.activity_type_input.setCurrentIndex(type_idx)
                elif self.activity_type_input.isEditable():
                    self.activity_type_input.setEditText(activity_type)

            self._refresh_season_options()
            season = self.table.item(row, 6).text()
            season_idx = self.season_combo.findText(season)
            if season_idx >= 0:
                self.season_combo.setCurrentIndex(season_idx)
            
            if self.module_name == "Front Line Demonstrations (FLD)":
                self._set_fld_technical_assessment(self.table.item(row, 8).text())
            else:
                self.description_input.setText(self.table.item(row, 8).text())
            self.remarks_input.setText(self.table.item(row, 9).text())

    def _on_district_changed(
        self,
        _index: int = -1,
        selected_tehsil: str = "",
        selected_village: str = "",
    ) -> None:
        selected_district = self.district_input.currentText().strip()
        has_district = self._is_valid_district(selected_district)

        self.tehsil_input.blockSignals(True)
        self.tehsil_input.clear()
        self.tehsil_input.addItem("Select Tehsil", None)
        if has_district:
            for tehsil_name in MH_DISTRICT_TEHSILS.get(selected_district, []):
                self.tehsil_input.addItem(tehsil_name, tehsil_name)
            self.tehsil_input.setEnabled(True)
        else:
            self.tehsil_input.setEnabled(False)
        self.tehsil_input.setCurrentIndex(0)

        if selected_tehsil:
            tehsil_idx = self.tehsil_input.findText(selected_tehsil)
            if tehsil_idx >= 0:
                self.tehsil_input.setCurrentIndex(tehsil_idx)
                self.tehsil_input.setEditText(selected_tehsil)

        self.tehsil_input.blockSignals(False)
        self._refresh_village_options(selected_village=selected_village)

    def _on_tehsil_changed(self, _index: int = -1) -> None:
        self._refresh_village_options()

    def _on_oft_district_changed(self, _index: int = -1, selected_tehsil: str = "") -> None:
        selected_district = self.oft_district_input.currentText().strip()
        has_district = self._is_valid_district(selected_district)

        self.oft_taluka_input.blockSignals(True)
        self.oft_taluka_input.clear()
        self.oft_taluka_input.addItem("Select Tehsil", None)
        if has_district:
            for tehsil_name in MH_DISTRICT_TEHSILS.get(selected_district, []):
                self.oft_taluka_input.addItem(tehsil_name, tehsil_name)
            self.oft_taluka_input.setEnabled(True)
        else:
            self.oft_taluka_input.setEnabled(False)

        self.oft_taluka_input.setCurrentIndex(0)
        if selected_tehsil:
            tehsil_idx = self.oft_taluka_input.findText(selected_tehsil)
            if tehsil_idx >= 0:
                self.oft_taluka_input.setCurrentIndex(tehsil_idx)
                self.oft_taluka_input.setEditText(selected_tehsil)

        self.oft_taluka_input.blockSignals(False)
        self._refresh_village_options()

    def _on_oft_tehsil_changed(self, _index: int = -1) -> None:
        self._refresh_village_options()

    def _refresh_village_options(self, selected_village: str = "") -> None:
        if self.module_name == "Visitor Farmers":
            district_value = self.district_input.currentText().strip()
            tehsil_value = self.tehsil_input.currentText().strip()
            has_district = self._is_valid_district(district_value)
            has_tehsil = self._is_valid_tehsil(district_value, tehsil_value)

            if has_district and has_tehsil:
                self.villages = ActivityService.list_villages_for_visitor(district_value, tehsil_value)
            else:
                self.villages = []
        elif self._is_oft_style_module():
            district_value = self.oft_district_input.currentText().strip()
            tehsil_value = self.oft_taluka_input.currentText().strip()
            has_district = self._is_valid_district(district_value)
            has_tehsil = self._is_valid_tehsil(district_value, tehsil_value)

            if has_district and has_tehsil:
                self.villages = ActivityService.list_villages_for_oft(district_value, tehsil_value, self.module_name)
                self.village_input.setEnabled(True)
            else:
                self.villages = []
                self.village_input.setEnabled(False)
        else:
            self.villages = ActivityService.list_villages()

        self.village_input.blockSignals(True)
        self.village_input.clear()
        self.village_input.addItems(self.villages)
        self.village_input.setCurrentIndex(-1)
        self.village_input.setEditText(selected_village)
        self.village_input.blockSignals(False)

    @staticmethod
    def _configure_searchable_combo(combo: QComboBox) -> None:
        combo.setInsertPolicy(QComboBox.NoInsert)
        completer = QCompleter(combo.model(), combo)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        completer.setFilterMode(Qt.MatchContains)
        completer.setCompletionMode(QCompleter.PopupCompletion)
        combo.setCompleter(completer)

    def _configure_mobile_input(self, line_edit: QLineEdit) -> None:
        line_edit.setMaxLength(10)
        line_edit.setValidator(QRegExpValidator(QRegExp(r"\d{0,10}"), line_edit))
        if not line_edit.placeholderText():
            line_edit.setPlaceholderText("10 digit mobile number")
        if hasattr(line_edit, "inputRejected"):
            line_edit.inputRejected.connect(self._show_mobile_input_error)

    def _show_mobile_input_error(self) -> None:
        QMessageBox.warning(self, "Validation", "Mobile number must contain only 10 digits.")

    @staticmethod
    def _is_valid_district(district: str) -> bool:
        return district in MH_DISTRICT_TEHSILS

    @staticmethod
    def _is_valid_tehsil(district: str, tehsil: str) -> bool:
        return tehsil in MH_DISTRICT_TEHSILS.get(district, [])

    def _format_season_for_display(self, row_data: dict) -> str:
        season_value = (row_data.get("season") or "").strip()
        department_name = (row_data.get("department") or "").strip()
        activity_type = (row_data.get("activity_type") or "").strip()

        if self.module_name in [
            "Training Programmes",
            "Vocational Training Programmes",
            "Extension Activities",
            "Other Extension Activities",
        ]:
            return "N/A"

        if not season_value or season_value.lower() in {"not required", "na", "n/a", "none", "null"}:
            return "N/A"

        return season_value

    def _format_activity_for_display(self, row_data: dict) -> str:
        activity_value = (row_data.get("activity_type") or "").strip()
        department_name = (row_data.get("department") or "").strip()

        if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
            return "N/A"

        if not activity_value or activity_value.lower() in {
            "not applicable",
            "not required",
            "na",
            "n/a",
            "none",
            "null",
            "select activity type",
            "select department first",
        }:
            return "N/A"

        return activity_value

    @staticmethod
    def _format_optional_text_for_display(value) -> str:
        text_value = str(value).strip() if value is not None else ""
        return text_value if text_value else "N/A"

    @staticmethod
    def _compose_oft_remarks(district: str, tehsil: str, remarks: str) -> str:
        return f"OFT_META|District:{district}|Tehsil:{tehsil}|Remarks:{remarks}"

    @staticmethod
    def _parse_oft_remarks(raw_remarks: str) -> tuple[str, str, str]:
        raw = (raw_remarks or "").strip()
        if not raw.startswith("OFT_META|"):
            return "", "", raw

        payload = raw[len("OFT_META|"):]
        district = ""
        tehsil = ""
        remarks = ""
        for part in payload.split("|"):
            if part.startswith("District:"):
                district = part.replace("District:", "", 1).strip()
            elif part.startswith("Taluka:"):
                tehsil = part.replace("Taluka:", "", 1).strip()
            elif part.startswith("Tehsil:"):
                tehsil = part.replace("Tehsil:", "", 1).strip()
            elif part.startswith("Remarks:"):
                remarks = part.replace("Remarks:", "", 1).strip()
        return district, tehsil, remarks

    def _load_table(self) -> None:
        from contextlib import nullcontext

        from ui.loading_overlay import busy

        holder = busy(self, "Loading records") if self.isVisible() else nullcontext()
        with holder:
            records, total = ActivityService.fetch_activities(
                module_type=self.module_name,
                page=self.current_page,
                page_size=self.page_size,
                filters=self._current_filters(),
            )
        self.total_records = total
        self._table_row_records = records
        serial_start = (self.current_page - 1) * self.page_size

        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(records):
            self.table.insertRow(row_idx)
            serial_number = serial_start + row_idx + 1
            display_season = self._format_season_for_display(row_data)
            display_activity = self._format_activity_for_display(row_data)
            oft_district, oft_taluka, oft_remarks = self._parse_oft_remarks(row_data.get("remarks", ""))
            
            if self.module_name in ["Training Programmes", "Vocational Training Programmes"]:
                # Training table shows one row per saved farmer.
                training_type = row_data.get("training_type", "Regular")
                training_category = row_data.get("training_farmer_category", "Other")
                values = [
                    serial_number,
                    self._format_optional_text_for_display(row_data.get("training_title", "")),
                    self._format_optional_text_for_display(row_data.get("venue") or row_data["village"]),
                    self._format_optional_text_for_display(row_data.get("clientele", "")),
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data["department"]),
                    self._format_optional_text_for_display(training_type),
                    self._format_optional_text_for_display(row_data["farmer_name"]),
                    self._format_optional_text_for_display(row_data.get("farmer_code", "")),
                    self._format_optional_text_for_display(row_data["village"]),
                    self._format_optional_text_for_display(row_data["contact_number"]),
                    self._format_optional_text_for_display(row_data.get("training_farmer_scientist", "")),
                    self._format_optional_text_for_display(row_data.get("training_farmer_purpose", "")),
                    self._format_optional_text_for_display(training_category),
                    self._format_optional_text_for_display(row_data.get("training_farmer_district", "")),
                    self._format_optional_text_for_display(row_data.get("training_farmer_tehsil", "")),
                    self._format_optional_text_for_display(row_data["description"]),
                    self._format_optional_text_for_display(row_data["remarks"]),
                ]
            elif self.module_name == "Extension Activities":
                values = [
                    serial_number,
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data.get("activity_type", "")),
                    self._format_optional_text_for_display(row_data.get("extension_venue", "")),
                    self._format_optional_text_for_display(row_data.get("extension_location", "")),
                    self._format_optional_text_for_display(row_data.get("extension_department", "") or row_data.get("department", "")),
                    self._format_optional_text_for_display(row_data.get("extension_purpose", "") or row_data.get("description", "")),
                    self._format_optional_text_for_display(row_data.get("extension_farmer_count", "")),
                ]
            elif self.module_name == "Other Extension Activities":
                values = [
                    serial_number,
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data.get("activity_type", "")),
                    self._format_optional_text_for_display(row_data.get("other_extension_title", "") or row_data.get("description", "")),
                ]
            elif self.module_name == "Visitor Farmers":
                district_value = row_data.get("visitor_district", "") or ActivityService._extract_district_tehsil(row_data.get("remarks", ""))[0]
                tehsil_value = row_data.get("visitor_tehsil", "") or ActivityService._extract_district_tehsil(row_data.get("remarks", ""))[1]
                description_value = row_data.get("visitor_scientist", "") or row_data.get("description", "")
                values = [
                    serial_number,
                    row_data["farmer_name"],
                    row_data.get("farmer_code", ""),
                    row_data["village"],
                    row_data["contact_number"],
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data["department"]),
                    self._format_optional_text_for_display(district_value),
                    self._format_optional_text_for_display(tehsil_value),
                    display_activity,
                    self._format_optional_text_for_display(description_value),
                    self._format_optional_text_for_display(row_data["remarks"]),
                ]
            elif self._is_oft_style_module():
                values = [
                    serial_number,
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data.get("oft_title", "")),
                    self._format_optional_text_for_display(row_data.get("oft_crop_variety", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_count", "")),
                    self._format_optional_text_for_display(row_data["farmer_name"]),
                    self._format_optional_text_for_display(row_data.get("farmer_code", "")),
                    self._format_optional_text_for_display(row_data["village"]),
                    self._format_optional_text_for_display(row_data["contact_number"]),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_scientist", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_purpose", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_district", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_tehsil", "")),
                ]
                if self.module_name == "On Farm Testing (OFT)":
                    t1_value, t2_value, t3_value = self._parse_oft_technical_assessment(
                        row_data.get("oft_technical_assessment", "")
                    )
                    values.extend([
                        self._format_optional_text_for_display(t1_value),
                        self._format_optional_text_for_display(t2_value),
                        self._format_optional_text_for_display(t3_value),
                    ])
                values.extend([
                    self._format_optional_text_for_display(row_data.get("oft_area", "")),
                    self._format_optional_text_for_display(row_data["department"]),
                    display_activity,
                    display_season,
                ])
            else:
                values = [
                    serial_number,
                    row_data["farmer_name"],
                    row_data["village"],
                    row_data["contact_number"],
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data["department"]),
                    display_season,
                    display_activity,
                    self._format_optional_text_for_display(row_data["description"]),
                    self._format_optional_text_for_display(row_data["remarks"]),
                ]
            for col, value in enumerate(values):
                self.table.setItem(row_idx, col, QTableWidgetItem(str(value)))

        total_pages = max(1, ceil(self.total_records / self.page_size))
        self.page_label.setText(f"Page {self.current_page} of {total_pages} | Total records: {self.total_records}")

    def _prev_page(self) -> None:
        if self.current_page > 1:
            self.current_page -= 1
            self._load_table()

    def _next_page(self) -> None:
        total_pages = max(1, ceil(self.total_records / self.page_size))
        if self.current_page < total_pages:
            self.current_page += 1
            self._load_table()
