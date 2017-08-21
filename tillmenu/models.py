from django.db import models
from django.core.urlresolvers import reverse

default_menu = """# Any line starting with '#' is ignored
# Blank lines are also ignored

# Submenus are introduced by indenting with spaces.  Don't use tabs.
# You can choose the number of spaces to indent by, but be consistent!

# Prices follow ":" at the end of each line and must have two decimal places.
# They are optional - if you leave a price out it's treated as zero.

# If an item with a price has a submenu, the items in that submenu are
# interpreted as options and/or optional extras for that item.

# Submenus on optional extras are ignored.

Starters
  First starter: 1.00
  Second starter: 2.00

Main courses
  First main course: 3.00

  Second main course: 4.00
    Option on second main course
    Optional extra on second main course: 1.00
      This will be ignored.
Zero-price instruction to chef
*** Takeaway ***
"""

class Menu(models.Model):
    name = models.CharField(max_length=80)
    contents = models.TextField()

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("tillmenu-detail", args=[self.id])
