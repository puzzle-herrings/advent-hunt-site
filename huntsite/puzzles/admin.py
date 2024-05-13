from django.contrib import admin

import huntsite.puzzles.models as models

admin.site.register(models.Puzzle)
admin.site.register(models.Guess)
admin.site.register(models.Solve)
