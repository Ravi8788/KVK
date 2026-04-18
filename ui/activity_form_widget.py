from math import ceil
from datetime import timedelta
from uuid import uuid4

from PyQt5.QtCore import QDate, Qt
from PyQt5.QtWidgets import (
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

    def __init__(self, module_name: str, current_user, read_only: bool = False):
        super().__init__()
        self.module_name = module_name
        self.current_user = current_user
        self.read_only = read_only
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

        self._build_ui()
        self._apply_role_permissions()
        self._load_table()

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

        if self.module_name == "On Farm Testing (OFT)":
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

        if self.module_name == "Visitor Farmers":
            form_layout.addLayout(form_left, 0, 0)
        else:
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
            col_count = 11
        elif self.module_name == "On Farm Testing (OFT)":
            col_count = 10
        else:
            col_count = 10
        self.table = QTableWidget(0, col_count)
        
        if self.module_name == "Visitor Farmers":
            headers = [
                "ID",
                "Farmer",
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
                "ID",
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
        self.fld_table_edit_btn = None
        self.fld_table_delete_btn = None
        if self.module_name == "Front Line Demonstrations (FLD)":
            self.fld_table_edit_btn = QPushButton("Open Edit Dialog")
            self.fld_table_delete_btn = QPushButton("Delete Selected")
            self.fld_table_edit_btn.setEnabled(False)
            self.fld_table_delete_btn.setEnabled(False)
            self.fld_table_edit_btn.clicked.connect(self._open_fld_edit_dialog)
            self.fld_table_delete_btn.clicked.connect(self._delete_record)
        self.page_label = QLabel("Page 1")

        self.prev_btn.clicked.connect(self._prev_page)
        self.next_btn.clicked.connect(self._next_page)

        pager_row.addWidget(self.prev_btn)
        pager_row.addWidget(self.next_btn)
        if self.fld_table_edit_btn is not None:
            pager_row.addWidget(self.fld_table_edit_btn)
            pager_row.addWidget(self.fld_table_delete_btn)
        pager_row.addWidget(self.page_label)
        pager_row.addStretch(1)

        table_layout.addWidget(self.table)
        table_layout.addLayout(pager_row)

        root.addWidget(table_card)

    def _build_oft_ui(self, root: QVBoxLayout) -> None:
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
        self.description_input.setPlaceholderText("Enter technical assessment")
        self.description_input.setFixedHeight(90)

        self.remarks_input = QLineEdit()
        self.remarks_input.setPlaceholderText("Enter area")
        self.remarks_input.setMinimumHeight(34)

        self.date_input.setMinimumHeight(34)
        self.department_combo.setMinimumHeight(34)
        self.activity_type_input.setMinimumHeight(34)
        self.season_combo.setMinimumHeight(34)

        form_layout.addRow("Date*", self.date_input)
        form_layout.addRow("Title of OFT*", self.farmer_name_input)
        form_layout.addRow("Crop Variety*", self.village_input)
        farmers_row = QHBoxLayout()
        farmers_row.setSpacing(8)
        farmers_row.addWidget(self.contact_input)
        farmers_row.addWidget(self.oft_show_btn)
        farmers_row.addStretch(1)
        form_layout.addRow("No. of Farmers*", farmers_row)
        form_layout.addRow("Technical Assessment*", self.description_input)
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
        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")

        self.save_btn.setMinimumHeight(34)
        self.reset_btn.setMinimumHeight(34)
        self.edit_btn.setMinimumHeight(34)
        self.delete_btn.setMinimumHeight(34)
        self.edit_btn.setText("Edit (Dialog)")

        self.save_btn.clicked.connect(self._save_record)
        self.reset_btn.clicked.connect(self._reset_form)
        self.edit_btn.clicked.connect(self._edit_record)
        self.delete_btn.clicked.connect(self._delete_record)

        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.reset_btn)
        btn_row.addWidget(self.edit_btn)
        btn_row.addWidget(self.delete_btn)
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
        self.oft_boxes_scroll.setMinimumHeight(220)
        self.oft_boxes_scroll.setMaximumHeight(360)
        self.oft_boxes_scroll.verticalScrollBar().setSingleStep(18)
        self.oft_boxes_scroll.hide()
        root.addWidget(self.oft_boxes_scroll)

        save_all_row = QHBoxLayout()
        self.oft_save_all_btn = QPushButton("Save All Changes")
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

        self.table = QTableWidget(0, 17)
        headers = [
            "ID",
            "Date",
            "Title of OFT",
            "Crop Variety",
            "No. of Farmers",
            "Farmer Name",
            "Farmer Village",
            "Mobile No.",
            "Scientist",
            "Purpose",
            "District",
            "Tehsil",
            "Technical Assessment",
            "Area",
            "Department",
            "Activity",
            "Season",
        ]
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.cellClicked.connect(self._on_row_selected)

        pager_row = QHBoxLayout()
        self.prev_btn = QPushButton("Previous")
        self.next_btn = QPushButton("Next")
        self.oft_table_edit_btn = QPushButton("Open Edit Dialog")
        self.oft_table_delete_btn = QPushButton("Delete Selected")
        self.oft_table_edit_btn.setEnabled(False)
        self.oft_table_delete_btn.setEnabled(False)
        self.oft_table_edit_btn.clicked.connect(self._open_oft_edit_dialog)
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

    def _update_oft_form_visibility(self) -> None:
        if self.module_name != "On Farm Testing (OFT)":
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
        self.edit_btn.setEnabled(header_ready and self.selected_activity_id is not None)
        self.delete_btn.setEnabled(header_ready and self.selected_activity_id is not None)

    def _show_oft_farmer_boxes(self) -> None:
        if self.module_name != "On Farm Testing (OFT)":
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

        for index in range(farmer_count):
            box = QFrame()
            box.setObjectName("Card")
            box_layout = QFormLayout(box)
            box_layout.setHorizontalSpacing(12)
            box_layout.setVerticalSpacing(8)
            box_layout.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

            box_title = QLabel(f"Farmer Form {index + 1} of {farmer_count}")
            box_title.setObjectName("CardTitle")
            box_layout.addRow(box_title)

            farmer_name = QLineEdit()
            farmer_name.setMinimumHeight(32)
            district = QComboBox()
            district.setEditable(True)
            district.addItem("Select District", None)
            for district_name in sorted(MH_DISTRICT_TEHSILS.keys()):
                district.addItem(district_name, district_name)
            district.lineEdit().setPlaceholderText("Select district")
            self._configure_searchable_combo(district)
            district.setMinimumHeight(32)

            tehsil = QComboBox()
            tehsil.setEditable(True)
            tehsil.addItem("Select Tehsil", None)
            tehsil.setEnabled(False)
            tehsil.lineEdit().setPlaceholderText("Select tehsil")
            self._configure_searchable_combo(tehsil)
            tehsil.setMinimumHeight(32)

            village = QComboBox()
            village.setEditable(True)
            village.setInsertPolicy(QComboBox.NoInsert)
            village.setCurrentIndex(-1)
            village.setEnabled(False)
            village.lineEdit().setPlaceholderText("Select village")
            self._configure_searchable_combo(village)
            village.setMinimumHeight(32)

            mobile = QLineEdit()
            mobile.setMinimumHeight(32)
            scientist = QLineEdit()
            scientist.setMinimumHeight(32)
            purpose = QComboBox()
            purpose.addItems(["Visitor Entry", "Consultation"])
            purpose.setMinimumHeight(32)

            save_farmer_btn = QPushButton("Save Farmer Data")
            save_farmer_btn.setMinimumHeight(32)
            farmer_save_state = QLabel("Not saved")

            def _refresh_box_villages(_index: int = -1, district_combo=district, tehsil_combo=tehsil, village_combo=village) -> None:
                district_value = district_combo.currentText().strip()
                tehsil_value = tehsil_combo.currentText().strip()
                if self._is_valid_district(district_value) and self._is_valid_tehsil(district_value, tehsil_value):
                    village_combo.setEnabled(True)
                    villages = ActivityService.list_villages_for_visitor(district_value, tehsil_value)
                else:
                    village_combo.setEnabled(False)
                    villages = []
                village_combo.blockSignals(True)
                village_combo.clear()
                village_combo.addItems(villages)
                village_combo.setCurrentIndex(-1)
                village_combo.blockSignals(False)

            def _refresh_tehsils(_index: int = -1, district_combo=district, tehsil_combo=tehsil, village_combo=village) -> None:
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
                tehsil_combo.setCurrentIndex(0)
                tehsil_combo.blockSignals(False)
                _refresh_box_villages()

            district.currentIndexChanged.connect(_refresh_tehsils)
            tehsil.currentIndexChanged.connect(_refresh_box_villages)

            box_layout.addRow(f"Farmer {index + 1} Name*", farmer_name)
            box_layout.addRow("District*", district)
            box_layout.addRow("Tehsil*", tehsil)
            box_layout.addRow("Village*", village)
            box_layout.addRow("Mobile No.*", mobile)
            box_layout.addRow("Name of Scientist*", scientist)
            box_layout.addRow("Purpose*", purpose)
            farmer_btn_row = QHBoxLayout()
            farmer_btn_row.addWidget(save_farmer_btn)
            farmer_btn_row.addWidget(farmer_save_state)
            farmer_btn_row.addStretch(1)
            box_layout.addRow(farmer_btn_row)

            form_state = {
                "index": index,
                "farmer_name": farmer_name,
                "district": district,
                "tehsil": tehsil,
                "village": village,
                "mobile": mobile,
                "scientist": scientist,
                "purpose": purpose,
                "saved": False,
                "state_label": farmer_save_state,
                "save_btn": save_farmer_btn,
            }
            self.oft_farmer_forms.append(form_state)

            save_farmer_btn.clicked.connect(lambda _checked=False, form=form_state: self._save_oft_farmer_form(form))

            self.oft_farmer_boxes_layout.addWidget(box)

        self.oft_boxes_visible = True
        self.oft_farmer_boxes_card.setVisible(True)
        self.oft_boxes_scroll.setVisible(True)
        self._update_oft_saved_summary()
        self._update_oft_form_visibility()

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
        if not mobile_value.isdigit() or len(mobile_value) < 10:
            QMessageBox.warning(self, "Validation", f"Enter valid mobile number in Farmer Form {form_state['index'] + 1}.")
            return False
        if not scientist_value:
            QMessageBox.warning(self, "Validation", f"Enter scientist name in Farmer Form {form_state['index'] + 1}.")
            return False
        if not purpose_value:
            QMessageBox.warning(self, "Validation", f"Select purpose in Farmer Form {form_state['index'] + 1}.")
            return False
        return True

    def _save_oft_farmer_form(self, form_state) -> None:
        if self.module_name != "On Farm Testing (OFT)":
            return

        common_payload = self._collect_oft_common_payload()
        if common_payload is None:
            return

        if not self._validate_oft_farmer_form(form_state):
            return

        form_state["saved"] = True
        form_state["state_label"].setText("Saved")
        form_state["save_btn"].setText("Saved")
        self._update_oft_saved_summary()

    def _update_oft_saved_summary(self) -> None:
        if self.module_name != "On Farm Testing (OFT)":
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

            QMessageBox.information(self, "Saved", "All OFT farmer records saved successfully.")
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
        if hasattr(self, "oft_save_all_btn"):
            self.oft_save_all_btn.setEnabled(False)

    def _collect_payload(self):
        activity_type = self.activity_type_input.currentText().strip()
        season_value = self.season_combo.currentText()
        selected_department = self.department_combo.currentText().strip()

        if self.module_name == "Visitor Farmers":
            # Visitor Farmers uses a custom field sequence and keeps season as internal default.
            season_value = "Kharif"
        elif self.module_name == "On Farm Testing (OFT)":
            season_value = self.season_combo.currentText().strip()
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
        remarks_value = self.remarks_input.text().strip() if hasattr(self.remarks_input, "text") else self.remarks_input.toPlainText().strip()
        if self.module_name == "Visitor Farmers":
            description_value = self.scientist_input.text().strip()
            remarks_value = (
                f"District: {self.district_input.currentText().strip()} | "
                f"Tehsil: {self.tehsil_input.currentText().strip()}"
            )
        elif self.module_name == "On Farm Testing (OFT)":
            description_value = self.description_input.toPlainText().strip()
            remarks_value = self.remarks_input.text().strip()

        return {
            "module_type": self.module_name,
            "farmer_name": self.farmer_name_input.text().strip(),
            "village": self.village_input.text().strip() if self.module_name == "On Farm Testing (OFT)" else self.village_input.currentText().strip(),
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
                options = ["Assessment"]

        self.activity_type_input.blockSignals(True)
        self.activity_type_input.clear()
        self.activity_type_input.addItems(options)

        # OFT and Extension Activities keep strict dropdown options.
        self.activity_type_input.setEditable(self.module_name not in ["On Farm Testing (OFT)", "Extension Activities"])
        if self.module_name == "On Farm Testing (OFT)":
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

        if self.module_name == "On Farm Testing (OFT)":
            self.season_label.setVisible(True)
            self.season_combo.setVisible(True)
            self.season_combo.setEnabled(True)
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

        if self.module_name == "On Farm Testing (OFT)":
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

        if self.module_name not in ["Front Line Demonstrations (FLD)", "Training Programmes", "Vocational Training Programmes"]:
            required.append(payload["activity_type"])
        if any(not x for x in required):
            QMessageBox.warning(self, "Validation", "Please fill all required fields marked with *.")
            return False

        if self.module_name == "On Farm Testing (OFT)":
            if not self.department_combo.currentData():
                QMessageBox.warning(self, "Validation", "Please select Department first.")
                return False
            if payload["activity_type"] != "Assessment":
                QMessageBox.warning(self, "Validation", "Activity Type is fixed to Assessment for OFT.")
                return False
            if payload["season"] not in ["Kharif", "Rabi"]:
                QMessageBox.warning(self, "Validation", "Please select OFT Season.")
                return False

        if self.module_name == "On Farm Testing (OFT)":
            if not payload["contact_number"].isdigit():
                QMessageBox.warning(self, "Validation", "No. of Farmers must be numeric.")
                return False
        elif not payload["contact_number"].isdigit() or len(payload["contact_number"]) < 10:
            QMessageBox.warning(self, "Validation", "Contact number must be numeric and at least 10 digits.")
            return False
        return True

    def _save_record(self) -> None:
        if self.module_name == "On Farm Testing (OFT)":
            self._save_all_oft_records()
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

    def _edit_record(self) -> None:
        if not self.selected_activity_id:
            QMessageBox.warning(self, "Selection", "Select a row to edit.")
            return

        if self.module_name == "On Farm Testing (OFT)":
            self._open_oft_edit_dialog()
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
        edit_technical = QTextEdit(common.get("oft_technical_assessment", ""))
        edit_technical.setFixedHeight(90)
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
        upper_form.addRow("Technical Assessment*", edit_technical)
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
            if not edit_title.text().strip() or not edit_crop.text().strip() or not edit_technical.toPlainText().strip() or not edit_area.text().strip():
                QMessageBox.warning(dialog, "Validation", "Please fill all required OFT upper fields.")
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
                    if not mobile.isdigit() or len(mobile) < 10:
                        QMessageBox.warning(dialog, "Validation", f"Enter valid mobile number in Farmer Form {index + 1}.")
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
                        "description": edit_technical.toPlainText().strip(),
                        "remarks": f"OFT_META|District: {district}|Tehsil: {tehsil}",
                        "oft_title": edit_title.text().strip(),
                        "oft_batch_key": batch_key,
                        "oft_crop_variety": edit_crop.text().strip(),
                        "oft_farmer_count": len(dialog_farmer_forms),
                        "oft_technical_assessment": edit_technical.toPlainText().strip(),
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

        dialog = QDialog(self)
        dialog.setWindowTitle("Edit FLD Record")
        dialog.resize(720, 560)

        root = QVBoxLayout(dialog)
        form = QFormLayout()
        form.setHorizontalSpacing(12)
        form.setVerticalSpacing(8)
        form.setLabelAlignment(Qt.AlignLeft | Qt.AlignVCenter)

        edit_farmer_name = QLineEdit(self.farmer_name_input.text().strip())
        edit_village = QComboBox()
        edit_village.setEditable(True)
        edit_village.setInsertPolicy(QComboBox.NoInsert)
        edit_village.addItems(ActivityService.list_villages())
        self._configure_searchable_combo(edit_village)
        edit_village.setCurrentText(self.village_input.currentText().strip())

        edit_contact = QLineEdit(self.contact_input.text().strip())
        edit_date = QDateEdit()
        edit_date.setCalendarPopup(True)
        edit_date.setDate(self.date_input.date())

        edit_department = QComboBox()
        edit_department.addItem("Select Department", None)
        for dept in self.departments:
            edit_department.addItem(dept.name, dept.id)
        dept_idx = edit_department.findData(self.department_combo.currentData())
        if dept_idx >= 0:
            edit_department.setCurrentIndex(dept_idx)

        edit_season = QComboBox()
        edit_season.addItems(["Kharif", "Rabi"])
        season_idx = edit_season.findText(self.season_combo.currentText().strip())
        if season_idx >= 0:
            edit_season.setCurrentIndex(season_idx)

        edit_description = QTextEdit(self.description_input.toPlainText().strip())
        edit_description.setFixedHeight(90)
        edit_remarks = QTextEdit(self.remarks_input.toPlainText().strip())
        edit_remarks.setFixedHeight(90)

        form.addRow("Farmer Name*", edit_farmer_name)
        form.addRow("Village*", edit_village)
        form.addRow("Contact Number*", edit_contact)
        form.addRow("Date*", edit_date)
        form.addRow("Department*", edit_department)
        form.addRow("Season*", edit_season)
        form.addRow("Description", edit_description)
        form.addRow("Remarks", edit_remarks)
        root.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.rejected.connect(dialog.reject)
        root.addWidget(buttons)

        def _save_fld_dialog_changes() -> None:
            farmer_name = edit_farmer_name.text().strip()
            village = edit_village.currentText().strip()
            contact = edit_contact.text().strip()
            department_id = edit_department.currentData()
            season = edit_season.currentText().strip()
            description = edit_description.toPlainText().strip()
            remarks = edit_remarks.toPlainText().strip()

            if not farmer_name or not village or not contact:
                QMessageBox.warning(dialog, "Validation", "Please fill all required fields marked with *.")
                return
            if not contact.isdigit() or len(contact) < 10:
                QMessageBox.warning(dialog, "Validation", "Contact number must be numeric and at least 10 digits.")
                return
            if department_id is None:
                QMessageBox.warning(dialog, "Validation", "Please select Department.")
                return

            department_name = edit_department.currentText().strip()
            if department_name != "Horticulture":
                season = "Kharif"

            payload = {
                "module_type": self.module_name,
                "farmer_name": farmer_name,
                "village": village,
                "contact_number": contact,
                "activity_date": edit_date.date().toPyDate(),
                "department_id": department_id,
                "season": season,
                "activity_type": "FLD Entry",
                "description": description,
                "remarks": remarks,
            }

            try:
                ActivityService.update_activity(self.selected_activity_id, payload, self.current_user.id)
                QMessageBox.information(dialog, "Updated", "FLD record updated successfully.")
                dialog.accept()
                self._reset_form()
                self._load_table()
            except Exception as exc:
                QMessageBox.critical(dialog, "Error", f"Could not update FLD record: {exc}")

        buttons.accepted.connect(_save_fld_dialog_changes)
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

        if self.module_name == "On Farm Testing (OFT)" and self.oft_selected_activity_ids:
            confirm = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Delete selected OFT batch ({len(self.oft_selected_activity_ids)} farmer records)?",
            )
        else:
            confirm = QMessageBox.question(self, "Confirm Delete", "Delete selected record?")
        if confirm != QMessageBox.Yes:
            return

        try:
            if self.module_name == "On Farm Testing (OFT)" and self.oft_selected_activity_ids:
                for activity_id in self.oft_selected_activity_ids:
                    ActivityService.delete_activity(activity_id, self.current_user.id)
                QMessageBox.information(self, "Deleted", "Selected OFT batch deleted successfully.")
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
        if hasattr(self, "fld_table_edit_btn") and self.fld_table_edit_btn is not None:
            self.fld_table_edit_btn.setEnabled(False)
        if hasattr(self, "fld_table_delete_btn") and self.fld_table_delete_btn is not None:
            self.fld_table_delete_btn.setEnabled(False)
        self.farmer_name_input.clear()
        self.contact_input.clear()
        self.date_input.setDate(QDate.currentDate())
        self.department_combo.setCurrentIndex(0)
        self._refresh_activity_type_options()
        self._refresh_season_options()
        if self.activity_type_input.count() > 0:
            self.activity_type_input.setCurrentIndex(0)
        if self.module_name == "Visitor Farmers":
            self.district_input.setCurrentIndex(0)
            self._on_district_changed()
            self.scientist_input.clear()
        elif self.module_name == "On Farm Testing (OFT)":
            self.season_combo.setCurrentIndex(0)
            self.farmer_name_input.clear()
            self.village_input.clear()
            self.contact_input.clear()
            self.description_input.clear()
            self.remarks_input.clear()
            self.oft_farmer_forms = []
            self.oft_boxes_visible = False
            if hasattr(self, "oft_farmer_boxes_card"):
                while self.oft_farmer_boxes_layout.count():
                    item = self.oft_farmer_boxes_layout.takeAt(0)
                    widget = item.widget()
                    if widget is not None:
                        widget.deleteLater()
                self.oft_farmer_boxes_card.hide()
                self.oft_boxes_scroll.hide()
            self._update_oft_saved_summary()
        else:
            self.description_input.clear()
            self.remarks_input.clear()
        self._update_oft_form_visibility()

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
        self.selected_activity_id = int(self.table.item(row, 0).text())
        if hasattr(self, "oft_table_edit_btn"):
            self.oft_table_edit_btn.setEnabled(True)
        if hasattr(self, "oft_table_delete_btn"):
            self.oft_table_delete_btn.setEnabled(True)
        if hasattr(self, "fld_table_edit_btn") and self.fld_table_edit_btn is not None:
            self.fld_table_edit_btn.setEnabled(True)
        if hasattr(self, "fld_table_delete_btn") and self.fld_table_delete_btn is not None:
            self.fld_table_delete_btn.setEnabled(True)
        self.farmer_name_input.setText(self.table.item(row, 1).text())
        village_value = self.table.item(row, 2).text().strip()
        if self.module_name != "On Farm Testing (OFT)":
            self._refresh_village_options(selected_village=village_value)
        self.contact_input.setText(self.table.item(row, 3).text())
        self.date_input.setDate(QDate.fromString(self.table.item(row, 4).text(), "yyyy-MM-dd"))

        department_name = self.table.item(row, 5).text()
        idx = self.department_combo.findText(department_name)
        if idx >= 0:
            self.department_combo.setCurrentIndex(idx)

        self._refresh_activity_type_options()
        self._update_oft_form_visibility()
        
        if self.module_name == "Visitor Farmers":
            # Visitor Farmers includes District and Tehsil columns.
            activity_type = self.table.item(row, 8).text()
            if activity_type:
                type_idx = self.activity_type_input.findText(activity_type)
                if type_idx >= 0:
                    self.activity_type_input.setCurrentIndex(type_idx)
                elif self.activity_type_input.isEditable():
                    self.activity_type_input.setEditText(activity_type)
            
            self.scientist_input.setText(self.table.item(row, 9).text())
            district_value = self.table.item(row, 6).text().strip()
            tehsil_value = self.table.item(row, 7).text().strip()
            remarks_value = self.table.item(row, 10).text().strip()
            if district_value in {"", "N/A"} or tehsil_value in {"", "N/A"}:
                parsed_district, parsed_tehsil = ActivityService._extract_district_tehsil(remarks_value)
                district_value = parsed_district or district_value
                tehsil_value = parsed_tehsil or tehsil_value
            district_idx = self.district_input.findText(district_value)
            if district_idx >= 0:
                self.district_input.setCurrentIndex(district_idx)
                self._on_district_changed(selected_tehsil=tehsil_value, selected_village=village_value)
            tehsil_idx = self.tehsil_input.findText(tehsil_value)
            if tehsil_idx >= 0:
                self.tehsil_input.setCurrentIndex(tehsil_idx)
            self._refresh_village_options(selected_village=village_value)
        elif self.module_name == "On Farm Testing (OFT)":
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

            date_value = common.get("activity_date")
            if date_value:
                self.date_input.setDate(QDate(date_value.year, date_value.month, date_value.day))

            self.farmer_name_input.setText(common.get("oft_title", ""))
            self.village_input.setText(common.get("oft_crop_variety", ""))
            self.contact_input.setText(str(common.get("oft_farmer_count") or len(batch_records)))
            self.description_input.setText(common.get("oft_technical_assessment", ""))
            self.remarks_input.setText(common.get("oft_area", ""))

            activity_type = common.get("activity_type", "")
            type_idx = self.activity_type_input.findText(activity_type)
            if type_idx >= 0:
                self.activity_type_input.setCurrentIndex(type_idx)

            season = common.get("season", "")
            season_idx = self.season_combo.findText(season)
            if season_idx >= 0:
                self.season_combo.setCurrentIndex(season_idx)

            self._show_oft_farmer_boxes()

            for idx, record in enumerate(batch_records):
                if idx >= len(self.oft_farmer_forms):
                    break
                form_state = self.oft_farmer_forms[idx]
                form_state["farmer_name"].setText(record.get("farmer_name", ""))
                form_state["mobile"].setText(record.get("contact_number", ""))
                form_state["scientist"].setText(record.get("oft_farmer_scientist", ""))

                purpose_text = record.get("oft_farmer_purpose", "")
                purpose_idx = form_state["purpose"].findText(purpose_text)
                if purpose_idx >= 0:
                    form_state["purpose"].setCurrentIndex(purpose_idx)
                elif purpose_text:
                    form_state["purpose"].setCurrentText(purpose_text)

                district_text = record.get("oft_farmer_district", "")
                district_idx = form_state["district"].findText(district_text)
                if district_idx >= 0:
                    form_state["district"].setCurrentIndex(district_idx)
                elif district_text:
                    form_state["district"].setEditText(district_text)

                tehsil_text = record.get("oft_farmer_tehsil", "")
                tehsil_idx = form_state["tehsil"].findText(tehsil_text)
                if tehsil_idx >= 0:
                    form_state["tehsil"].setCurrentIndex(tehsil_idx)
                elif tehsil_text:
                    form_state["tehsil"].setEditText(tehsil_text)

                village_text = record.get("village", "")
                village_idx = form_state["village"].findText(village_text)
                if village_idx >= 0:
                    form_state["village"].setCurrentIndex(village_idx)
                elif village_text:
                    form_state["village"].setEditText(village_text)

                form_state["saved"] = True
                form_state["state_label"].setText("Saved")
                form_state["save_btn"].setText("Saved")

            self._update_oft_saved_summary()
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
        elif self.module_name == "On Farm Testing (OFT)":
            district_value = self.oft_district_input.currentText().strip()
            tehsil_value = self.oft_taluka_input.currentText().strip()
            has_district = self._is_valid_district(district_value)
            has_tehsil = self._is_valid_tehsil(district_value, tehsil_value)

            if has_district and has_tehsil:
                self.villages = ActivityService.list_villages_for_oft(district_value, tehsil_value)
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

        if not season_value or season_value.lower() in {"not required", "na", "n/a", "none", "null"}:
            return "N/A"

        return season_value

    def _format_activity_for_display(self, row_data: dict) -> str:
        activity_value = (row_data.get("activity_type") or "").strip()
        department_name = (row_data.get("department") or "").strip()

        if self.module_name in ["Front Line Demonstrations (FLD)", "Training Programmes", "Vocational Training Programmes"]:
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
        records, total = ActivityService.fetch_activities(
            module_type=self.module_name,
            page=self.current_page,
            page_size=self.page_size,
            filters=self._current_filters(),
        )
        self.total_records = total
        self._table_row_records = records

        self.table.setRowCount(0)
        for row_idx, row_data in enumerate(records):
            self.table.insertRow(row_idx)
            display_season = self._format_season_for_display(row_data)
            display_activity = self._format_activity_for_display(row_data)
            oft_district, oft_taluka, oft_remarks = self._parse_oft_remarks(row_data.get("remarks", ""))
            
            if self.module_name == "Visitor Farmers":
                district_value, tehsil_value = ActivityService._extract_district_tehsil(row_data.get("remarks", ""))
                values = [
                    row_data["id"],
                    row_data["farmer_name"],
                    row_data["village"],
                    row_data["contact_number"],
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data["department"]),
                    self._format_optional_text_for_display(district_value),
                    self._format_optional_text_for_display(tehsil_value),
                    display_activity,
                    self._format_optional_text_for_display(row_data["description"]),
                    self._format_optional_text_for_display(row_data["remarks"]),
                ]
            elif self.module_name == "On Farm Testing (OFT)":
                values = [
                    row_data["id"],
                    str(row_data["activity_date"]),
                    self._format_optional_text_for_display(row_data.get("oft_title", "")),
                    self._format_optional_text_for_display(row_data.get("oft_crop_variety", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_count", "")),
                    self._format_optional_text_for_display(row_data["farmer_name"]),
                    self._format_optional_text_for_display(row_data["village"]),
                    self._format_optional_text_for_display(row_data["contact_number"]),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_scientist", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_purpose", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_district", "")),
                    self._format_optional_text_for_display(row_data.get("oft_farmer_tehsil", "")),
                    self._format_optional_text_for_display(row_data.get("oft_technical_assessment", "")),
                    self._format_optional_text_for_display(row_data.get("oft_area", "")),
                    self._format_optional_text_for_display(row_data["department"]),
                    display_activity,
                    display_season,
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
