from django.contrib import admin

from .models import Question, Option


class OptionInline(admin.StackedInline):
    model = Option
    extra = 0
    fields = ('option_a', 'option_b', 'option_c', 'option_d', 'correct_option', 'rationale')


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'category', 'created_at')
    list_filter = ('category',)
    search_fields = ('text', 'category')
    inlines = [OptionInline]


@admin.register(Option)
class OptionAdmin(admin.ModelAdmin):
    list_display = ('question', 'correct_option', 'created_at')
    list_filter = ('correct_option',)
    search_fields = ('question__text', 'rationale')

