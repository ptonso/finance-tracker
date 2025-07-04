
from abc import ABC, abstractmethod
from bokeh.layouts import column, row
from bokeh.models import TabPanel

class BaseDashboard(ABC):
    """Abstract base class for all dashboards"""
    
    def __init__(self, data):
        self.data = data
        self.layout = None
        self.setup()
    
    @abstractmethod
    def setup(self):
        """Setup dashboard components and layout"""
        pass
    
    @abstractmethod
    def update_data(self, attr, old, new):
        """Update dashboard data and visuals"""
        pass
    
    def create_tab_panel(self):
        """Create a TabPanel for this dashboard"""
        return TabPanel(child=self.layout, title=self.title)