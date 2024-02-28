from django.contrib import admin
from .models import Question, Answer, Test, UserTestResult, ErrorLog, Profile





class ProfileAdmin(admin.ModelAdmin):
    list_display = ('name', 'phone_number', 'created_at', 'user_link')
    list_filter = ('created_at',)
    search_fields = ('name', 'phone_number', 'user__username')
    readonly_fields = ('created_at',)
    fieldsets = (
        (None, {'fields': ('user', 'name', 'phone_number')}),
        ('Date Information', {'fields': ('created_at',), 'classes': ('collapse',)}),
    )

    def user_link(self, obj):
        link = f'<a href="/admin/auth/user/{obj.user_id}/change/">{obj.user}</a>'
        return link

    user_link.allow_tags = True
    user_link.short_description = 'User'

class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 3

class QuestionAdmin(admin.ModelAdmin):
    inlines = [AnswerInline]

class TestAdmin(admin.ModelAdmin):
    filter_horizontal = ('questions',)

class UserTestResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'test', 'score', 'date_taken')
    list_filter = ('user', 'test', 'date_taken')
    search_fields = ('user__username', 'test__title')
    date_hierarchy = 'date_taken'


class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['error_number', 'error_message', 'user_agent', 'ip_address','created_at']
    list_filter = [ 'created_at']
    search_fields = ['error_message', 'user_agent', 'ip_address', 'error_number']
    readonly_fields = ['error_number', 'error_message', 'user_agent', 'ip_address', 'created_at']
    ordering = ['-created_at']

admin.site.register(ErrorLog, ErrorLogAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Test, TestAdmin)
admin.site.register(UserTestResult, UserTestResultAdmin)
admin.site.register(Profile, ProfileAdmin)
