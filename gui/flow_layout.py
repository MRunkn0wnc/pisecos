from PyQt5.QtWidgets import QLayout
from PyQt5.QtCore import QRect, QSize, QPoint

class QFlowLayout(QLayout):
    """Custom flow layout for suggestion chips"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.item_list = []
        
    def __del__(self):
        while self.item_list:
            item = self.item_list.pop()
            item.deleteLater()
    
    def addItem(self, item):
        self.item_list.append(item)
    
    def count(self):
        return len(self.item_list)
    
    def itemAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list[index]
        return None
    
    def takeAt(self, index):
        if 0 <= index < len(self.item_list):
            return self.item_list.pop(index)
        return None
    
    def expandingDirections(self):
        return Qt.Orientation(0)
    
    def hasHeightForWidth(self):
        return True
    
    def heightForWidth(self, width):
        return self.do_layout(QRect(0, 0, width, 0), True)
    
    def setGeometry(self, rect):
        super().setGeometry(rect)
        self.do_layout(rect, False)
    
    def sizeHint(self):
        return self.minimumSize()
    
    def minimumSize(self):
        size = QSize()
        for item in self.item_list:
            size = size.expandedTo(item.minimumSize())
        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size
    
    def do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()
        
        for item in self.item_list:
            style = item.widget().style() if item.widget() else None
            space = spacing + (style.pixelMetric(style.PM_LayoutHorizontalSpacing) if style else 0)
            next_x = x + item.sizeHint().width() + space
            
            if next_x - space > rect.right() and line_height > 0:
                x = rect.x()
                y = y + line_height + space
                next_x = x + item.sizeHint().width() + space
                line_height = 0
            
            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), item.sizeHint()))
            
            x = next_x
            line_height = max(line_height, item.sizeHint().height())
        
        return y + line_height - rect.y()