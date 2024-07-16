from django.contrib import admin

from .models import Card, User, Log, Access_reader


@admin.register(Card)
class CardAdmin(admin.ModelAdmin):
    list_display = ('id', 'uid', 'user', 'active', 'label', 'updated_at')
    list_filter = ('active',)
    search_fields = ('user__name', 'label', 'uid')
    list_editable = ('active', )


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ('id', 'created_at', 'user', 'reader', 'card_or_unknown_card', 'comment')
    list_filter = ('created_at', 'reader')
    search_fields = ('user__name', 'comment')
    list_display_links = ('created_at',)

    def card_or_unknown_card(self, obj):
        if obj.card:
            return obj.card.uid + ' (label: '+obj.card.label+')'
        else:
            return 'Unknown card: '+ str(obj.unknown_card)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'active', 'updated_at')  #,'allowed_accesses'
    list_filter = ('active',)
    search_fields = ('name',)
    list_editable = ('active', )
    filter_horizontal = ('allowed_accesses',)


@admin.register (Access_reader)
class Access_readerAdmin(admin.ModelAdmin):
    list_display = ('id' , 'label', 'listen_topic' , 'answer_topic' , 'message_topic', 'active')
    list_filter = ('active',)
    search_fields = ('label',)
    list_editable = ('active',)
