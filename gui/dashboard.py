# Add to existing PyQt5 dashboard
# This adds a tool browser panel

class ToolBrowser(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        
        # Category selector
        self.category_combo = QComboBox()
        self.category_combo.addItems(["All", "Recon", "Scanner", "Web", "Cracker", "Exploitation", "Wireless"])
        self.category_combo.currentTextChanged.connect(self.filter_tools)
        layout.addWidget(self.category_combo)
        
        # Tool list
        self.tool_list = QListWidget()
        self.tool_list.itemClicked.connect(self.on_tool_selected)
        layout.addWidget(self.tool_list)
        
        # Tool info
        self.tool_info = QTextEdit()
        self.tool_info.setReadOnly(True)
        self.tool_info.setMaximumHeight(100)
        layout.addWidget(self.tool_info)
        
        # Run button
        self.run_btn = QPushButton("Run Tool")
        self.run_btn.clicked.connect(self.run_selected_tool)
        layout.addWidget(self.run_btn)
        
        self.setLayout(layout)
        self.load_tools()
    
    def load_tools(self):
        # Load from tool_sources.json
        import json
        with open('/usr/local/pisecos/configs/tool_sources.json') as f:
            self.tools_data = json.load(f)
        
        self.all_tools = list(self.tools_data['known_tools'].keys())
        self.tool_list.addItems(self.all_tools)
    
    def filter_tools(self, category):
        self.tool_list.clear()
        if category == "All":
            self.tool_list.addItems(self.all_tools)
        else:
            cat_key = category.lower()
            if cat_key in self.tools_data['categories']:
                tools = self.tools_data['categories'][cat_key]
                self.tool_list.addItems(tools)
    
    def on_tool_selected(self, item):
        tool_name = item.text()
        if tool_name in self.tools_data['known_tools']:
            info = self.tools_data['known_tools'][tool_name]
            self.tool_info.setText(
                f"Description: {info.get('description', 'N/A')}\n"
                f"Type: {info.get('type', 'N/A')}\n"
                f"ARM Support: {info.get('arm_support', False)}"
            )
    
    def run_selected_tool(self):
        item = self.tool_list.currentItem()
        if item and self.parent().current_target:
            tool = item.text()
            target = self.parent().current_target
            # Run in terminal panel
            self.parent().run_tool(tool, target)