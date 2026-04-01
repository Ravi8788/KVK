from math import ceil
from datetime import timedelta

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (
    QCompleter,
    QComboBox,
    QDateEdit,
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

    def __init__(self, module_name: str, current_user, read_only: bool = False):
        super().__init__()
        self.module_name = module_name
        self.current_user = current_user
        self.read_only = read_only
        self.departments = ActivityService.list_departments()
        self.villages = ActivityService.list_villages()
        self.activity_type_presets = {
            "On Farm Testing (OFT)": ["Assessment", "Refinement"],
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
        self.current_page = 1
        self.page_size = 100
        self.total_records = 0

        self._build_ui()
        self._apply_role_permissions()
        self._load_table()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(10, 10, 10, 10)
        root.setSpacing(10)

        header = QLabel(self.module_name)
        header.setObjectName("CardTitle")
        root.addWidget(header)

        self.mode_label = QLabel("")
        root.addWidget(self.mode_label)

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
        if self.module_name == "On Farm Testing (OFT)":
            self.department_combo.addItem("Select Department", None)
        for dept in self.departments:
            self.department_combo.addItem(dept.name, dept.id)

        self.season_combo = QComboBox()
        self.season_combo.addItems(["Kharif", "Rabi"])

        self.activity_type_input = QComboBox()
        self.description_input = QTextEdit()
        self.remarks_input = QTextEdit()
        self.description_input.setFixedHeight(65)
        self.remarks_input.setFixedHeight(65)

        self.department_label = QLabel("Department*")
        self.season_label = QLabel("Season*")
        self.activity_type_label = QLabel("Activity Type*")

        if self.module_name == "Visitor Farmers":
            form_left.addRow("Date*", self.date_input)
            form_left.addRow("Name of Farmer*", self.farmer_name_input)
            form_left.addRow("District*", self.district_input)
            form_left.addRow("Tehsil*", self.tehsil_input)
            form_left.addRow("Village*", self.village_input)

            form_right.addRow("Mobile No.*", self.contact_input)
            form_right.addRow("Name of Scientist*", self.scientist_input)
            self.department_label.setText("Name of Dept.*")
            form_right.addRow(self.department_label, self.department_combo)
            self.activity_type_label.setText("Purpose*")
            form_right.addRow(self.activity_type_label, self.activity_type_input)
            
            # Hide season and description/remarks fields entirely for Visitor Farmers
            self.season_label.hide()
            self.season_combo.hide()
            self.description_input.hide()
            self.remarks_input.hide()
        else:
            form_left.addRow("Farmer Name*", self.farmer_name_input)
            form_left.addRow("Village*", self.village_input)
            form_left.addRow("Contact Number*", self.contact_input)
            form_left.addRow("Date*", self.date_input)

            form_right.addRow(self.department_label, self.department_combo)
            form_right.addRow(self.season_label, self.season_combo)
            form_right.addRow(self.activity_type_label, self.activity_type_input)
            form_right.addRow("Description", self.description_input)
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
        if self.module_name == "Visitor Farmers":
            self.district_input.currentIndexChanged.connect(self._on_district_changed)
            self.tehsil_input.currentIndexChanged.connect(self._on_tehsil_changed)
        self._refresh_activity_type_options()
        self._refresh_season_options()

        form_layout.addLayout(form_left, 0, 0)
        form_layout.addLayout(form_right, 0, 1)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.reset_btn = QPushButton("Reset")
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")

        self.save_btn.clicked.connect(self._save_record)
        self.reset_btn.clicked.connect(self._reset_form)
        self.edit_btn.clicked.connect(self._edit_record)
        self.delete_btn.clicked.connect(self._delete_record)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addStretch(1)
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

        # Visitor Farmers uses 9 columns (no Season), other modules use 10
        col_count = 9 if self.module_name == "Visitor Farmers" else 10
        self.table = QTableWidget(0, col_count)
        
        if self.module_name == "Visitor Farmers":
            headers = [
                "ID",
                "Farmer",
                "Village",
                "Contact",
                "Date",
                "Department",
                "Activity",
                "Description",
                "Remarks",
            ]
        else:
            headers = [
                "ID",
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

    def _apply_role_permissions(self) -> None:
        if not self.read_only:
            self.mode_label.setText("Mode: Full access")
            return

        self.mode_label.setText("Mode: Staff read-only for this module")
        self.farmer_name_input.setReadOnly(True)
        self.village_input.setEnabled(False)
        self.contact_input.setReadOnly(True)
        self.tehsil_input.setEnabled(False)
        self.district_input.setEnabled(False)
        self.scientist_input.setReadOnly(True)
        self.date_input.setEnabled(False)
        self.department_combo.setEnabled(False)
        self.season_combo.setEnabled(False)
        self.activity_type_input.setEnabled(False)
        self.description_input.setReadOnly(True)
        self.remarks_input.setReadOnly(True)
        self.save_btn.setEnabled(False)
        self.edit_btn.setEnabled(False)
        self.delete_btn.setEnabled(False)

    def _collect_payload(self):
        activity_type = self.activity_type_input.currentText().strip()
        season_value = self.season_combo.currentText()
        selected_department = self.department_combo.currentText().strip()

        if self.module_name == "Visitor Farmers":
            # Visitor Farmers uses a custom field sequence and keeps season as internal default.
            season_value = "Kharif"
        elif self.module_name == "On Farm Testing (OFT)":
            # For non-Agronomy departments, keep these as internal defaults.
            if selected_department != "Agronomy":
                activity_type = "General OFT"
                season_value = "Kharif"
            # Refinement does not require a visible season in UI; keep valid DB fallback.
            elif activity_type == "Refinement":
                season_value = "Kharif"
        elif self.module_name == "Front Line Demonstrations (FLD)":
            # FLD does not use activity type in UI; store a stable default value.
            activity_type = "FLD Entry"
            if selected_department != "Horticulture":
                season_value = "Kharif"
        elif self.module_name == "Training Programmes":
            # Training Programmes use department only in UI.
            activity_type = "Training Entry"
            season_value = "Kharif"
        elif self.module_name == "Vocational Training Programmes":
            # Vocational Training Programmes use department only in UI.
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

        description_value = self.description_input.toPlainText().strip()
        remarks_value = self.remarks_input.toPlainText().strip()
        if self.module_name == "Visitor Farmers":
            description_value = self.scientist_input.text().strip()
            remarks_value = (
                f"District: {self.district_input.currentText().strip()} | "
                f"Tehsil: {self.tehsil_input.currentText().strip()}"
            )

        return {
            "module_type": self.module_name,
            "farmer_name": self.farmer_name_input.text().strip(),
            "village": self.village_input.currentText().strip(),
            "contact_number": self.contact_input.text().strip(),
            "activity_date": self.date_input.date().toPyDate(),
            "department_id": self.department_combo.currentData(),
            "season": season_value,
            "activity_type": activity_type,
            "description": description_value,
            "remarks": remarks_value,
        }

    def _refresh_activity_type_options(self) -> None:
        current_value = self.activity_type_input.currentText().strip()
        options = self.activity_type_presets.get(self.module_name, ["General Activity"])

        if self.module_name == "On Farm Testing (OFT)":
            has_department = self.department_combo.currentData() is not None
            if not has_department:
                options = ["Select Department First"]
            else:
                selected_department = self.department_combo.currentText().strip()
                if selected_department == "Agronomy":
                    options = ["Select Activity Type", "Assessment", "Refinement"]
                else:
                    options = ["Not Applicable"]

        self.activity_type_input.blockSignals(True)
        self.activity_type_input.clear()
        self.activity_type_input.addItems(options)

        # OFT and Extension Activities keep strict dropdown options.
        self.activity_type_input.setEditable(self.module_name not in ["On Farm Testing (OFT)", "Extension Activities"])
        if self.module_name == "On Farm Testing (OFT)":
            has_department = self.department_combo.currentData() is not None
            is_agronomy = self.department_combo.currentText().strip() == "Agronomy"
            self.activity_type_input.setEnabled(has_department and is_agronomy)
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

    def _refresh_season_options(self) -> None:
        # Visitor Farmers never uses season field
        if self.module_name == "Visitor Farmers":
            self.season_label.setVisible(False)
            self.season_combo.setVisible(False)
            self.season_combo.setEnabled(False)
            return
        
        if self.module_name != "On Farm Testing (OFT)":
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
        required = [
            payload["farmer_name"],
            payload["village"],
            payload["contact_number"],
        ]

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

        if self.module_name not in ["Front Line Demonstrations (FLD)", "Training Programmes", "Vocational Training Programmes"]:
            required.append(payload["activity_type"])
        if any(not x for x in required):
            QMessageBox.warning(self, "Validation", "Please fill all required fields marked with *.")
            return False

        if self.module_name == "On Farm Testing (OFT)":
            if self.department_combo.currentData() is None:
                QMessageBox.warning(self, "Validation", "Please select Department first.")
                return False
            selected_department = self.department_combo.currentText().strip()
            if selected_department == "Agronomy" and payload["activity_type"] not in ["Assessment", "Refinement"]:
                QMessageBox.warning(self, "Validation", "Please select valid OFT Activity Type.")
                return False

        if not payload["contact_number"].isdigit() or len(payload["contact_number"]) < 10:
            QMessageBox.warning(self, "Validation", "Contact number must be numeric and at least 10 digits.")
            return False
        return True

    def _save_record(self) -> None:
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

    def _edit_record(self) -> None:
        if not self.selected_activity_id:
            QMessageBox.warning(self, "Selection", "Select a row to edit.")
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

    def _delete_record(self) -> None:
        if not self.selected_activity_id:
            QMessageBox.warning(self, "Selection", "Select a row to delete.")
            return

        confirm = QMessageBox.question(self, "Confirm Delete", "Delete selected record?")
        if confirm != QMessageBox.Yes:
            return

        try:
            ActivityService.delete_activity(self.selected_activity_id, self.current_user.id)
            QMessageBox.information(self, "Deleted", "Record deleted successfully.")
            self._reset_form()
            self._load_table()
        except Exception as exc:
            QMessageBox.critical(self, "Error", f"Could not delete record: {exc}")

    def _reset_form(self) -> None:
        self.selected_activity_id = None
        self.farmer_name_input.clear()
        self._refresh_village_options()
        self.contact_input.clear()
        self.district_input.setCurrentIndex(0)
        self._on_district_changed()
        self.scientist_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.department_combo.setCurrentIndex(0)
        self._refresh_activity_type_options()
        self._refresh_season_options()
        if self.activity_type_input.count() > 0:
            self.activity_type_input.setCurrentIndex(0)
        self.description_input.clear()
        self.remarks_input.clear()

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
        self.selected_activity_id = int(self.table.item(row, 0).text())
        self.farmer_name_input.setText(self.table.item(row, 1).text())
        village_value = self.table.item(row, 2).text().strip()
        self._refresh_village_options(selected_village=village_value)
        self.contact_input.setText(self.table.item(row, 3).text())
        self.date_input.setDate(QDate.fromString(self.table.item(row, 4).text(), "yyyy-MM-dd"))

        department_name = self.table.item(row, 5).text()
        idx = self.department_combo.findText(department_name)
        if idx >= 0:
            self.department_combo.setCurrentIndex(idx)

        self._refresh_activity_type_options()
        
        if self.module_name == "Visitor Farmers":
            # For Visitor Farmers: no Season column, so columns shift
            activity_type = self.table.item(row, 6).text()
            if activity_type:
                type_idx = self.activity_type_input.findText(activity_type)
                if type_idx >= 0:
                    self.activity_type_input.setCurrentIndex(type_idx)
                elif self.activity_type_input.isEditable():
                    self.activity_type_input.setEditText(activity_type)
            
            self.scientist_input.setText(self.table.item(row, 7).text())
            tehsil_value = ""
            district_value = ""
            remarks_value = self.table.item(row, 8).text().strip()
            if "District:" in remarks_value and "| Tehsil:" in remarks_value:
                district_part, tehsil_part = remarks_value.split("| Tehsil:", 1)
                district_value = district_part.replace("District:", "").strip()
                tehsil_value = tehsil_part.strip()
            elif "Tehsil:" in remarks_value and "| District:" in remarks_value:
                # Backward compatibility for older saved records.
                tehsil_part, district_part = remarks_value.split("| District:", 1)
                tehsil_value = tehsil_part.replace("Tehsil:", "").strip()
                district_value = district_part.strip()
            district_idx = self.district_input.findText(district_value)
            if district_idx >= 0:
                self.district_input.setCurrentIndex(district_idx)
                self._on_district_changed(selected_tehsil=tehsil_value, selected_village=village_value)
            tehsil_idx = self.tehsil_input.findText(tehsil_value)
            if tehsil_idx >= 0:
                self.tehsil_input.setCurrentIndex(tehsil_idx)
            self._refresh_village_options(selected_village=village_value)
        else:
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

        if self.module_name == "Front Line Demonstrations (FLD)" and department_name != "Horticulture":
            return "N/A"

        if self.module_name == "On Farm Testing (OFT)" and (
            department_name != "Agronomy" or activity_type == "Refinement"
        ):
            return "N/A"

        if not season_value or season_value.lower() in {"not required", "na", "n/a", "none", "null"}:
            return "N/A"

        return season_value

    def _format_activity_for_display(self, row_data: dict) -> str:
        activity_value = (row_data.get("activity_type") or "").strip()
        department_name = (row_data.get("department") or "").strip()

        if self.module_name in ["Front Line Demonstrations (FLD)", "Training Programmes", "Vocational Training Programmes"]:
            return "N/A"

        if self.module_name == "On Farm Testing (OFT)" and department_name != "Agronomy":
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

    def _load_table(self) -> None:
        records, total = ActivityService.fetch_activities(
            module_type=self.module_name,
            page=self.current_page,
            page_size=self.page_size,
            filters=self._current_filters(),
        )
        self.total_records = total

        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(records):
            self.table.insertRow(row_idx)
            display_season = self._format_season_for_display(row_data)
            display_activity = self._format_activity_for_display(row_data)
            
            if self.module_name == "Visitor Farmers":
                values = [
                    row_data["id"],
                    row_data["farmer_name"],
                    row_data["village"],
                    row_data["contact_number"],
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data["department"]),
                    display_activity,
                    self._format_optional_text_for_display(row_data["description"]),
                    self._format_optional_text_for_display(row_data["remarks"]),
                ]
            else:
                values = [
                    row_data["id"],
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
