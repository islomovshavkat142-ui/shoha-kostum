from django.contrib import admin
from .models import Fabric, FabricImage, Order  # Добавили Order в импорт


# Блок для загрузки дополнительных фото (цветов)
class FabricImageInline(admin.TabularInline):
    model = FabricImage
    extra = 3
    verbose_name = "Дополнительный цвет"
    verbose_name_plural = "Дополнительные цвета"


@admin.register(Fabric)
class FabricAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'category', 'show_on_main', 'order')
    list_filter = ('country', 'category', 'show_on_main')
    list_editable = ('show_on_main', 'order')
    inlines = [FabricImageInline]


# --- НОВЫЙ БЛОК ДЛЯ ЗАКАЗОВ ---

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    # Колонки, которые важны для тебя как для креативного директора
    list_display = ('id', 'client_name', 'selected_fabric', 'final_price', 'status', 'is_commission_received',
                    'created_at')

    # Фильтры помогут быстро найти неоплаченные заказы или новые заявки
    list_filter = ('status', 'is_commission_received', 'created_at')

    # Поиск по имени клиента или названию ткани
    search_fields = ('client_name', 'selected_fabric', 'telegram_username')

    # Эти поля можно редактировать прямо в списке (удобно проставлять цены и галочки комиссий)
    list_editable = ('status', 'is_commission_received', 'final_price')

    # Группировка данных внутри карточки заказа для порядка
    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('client_name', 'telegram_id', 'telegram_username')
        }),
        ('Детали костюма', {
            'fields': ('selected_fabric', 'measurements_data', 'client_comment')
        }),
        ('Финансы и статус', {
            'fields': ('final_price', 'is_commission_received', 'status')
        }),
    )
    # Запрещаем редактировать ID телеграма вручную, чтобы ничего не сломать
    readonly_fields = ('telegram_id', 'created_at', 'updated_at')