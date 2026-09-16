from django.db import models


class Fabric(models.Model):
    name = models.CharField("Название ткани", max_length=200)
    price = models.DecimalField("Цена за костюм ($)", max_digits=10, decimal_places=2, default=300)  # Добавь это!
    composition = models.TextField("Состав")
    description = models.TextField("Описание для каталога")
    main_image = models.ImageField("Основное фото образца", upload_to='fabrics/')
    country = models.CharField("Страна производства", max_length=100)
    category = models.CharField("Ценовая категория", max_length=100)
    show_on_main = models.BooleanField("Показывать на главной?", default=False)
    order = models.IntegerField("Порядок вывода", default=0)

    class Meta:
        verbose_name = "Ткань"
        verbose_name_plural = "Ткани"

    def __str__(self):
        return self.name


class FabricImage(models.Model):
    fabric = models.ForeignKey(Fabric, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField("Дополнительный цвет/фото", upload_to='fabrics/gallery/')

    class Meta:
        verbose_name = "Дополнительное фото"
        verbose_name_plural = "Дополнительные фото"


# --- НОВАЯ МОДЕЛЬ ДЛЯ ЗАКАЗОВ ---

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый заказ (Ожидание закройщика)'),
        ('confirmed', 'Подтвержден / В пошиве'),
        ('ready', 'Готов к отправке'),
        ('completed', 'Завершен'),
        ('canceled', 'Отменен'),
    ]

    # Личные данные (придут из Telegram)
    client_name = models.CharField("Имя клиента", max_length=255)
    telegram_id = models.BigIntegerField("ID в Telegram", )
    telegram_username = models.CharField("Username Telegram", max_length=150, blank=True, null=True)

    # Детали костюма
    selected_fabric = models.CharField("Выбранная ткань", max_length=255)
    measurements_data = models.TextField("Мерки по инструкции")
    client_comment = models.TextField("Пожелания клиента", blank=True)

    # Контроль доходов (для Креативного Директора)
    final_price = models.DecimalField("Итоговая цена ($)", max_digits=10, decimal_places=2, default=0)
    is_commission_received = models.BooleanField("Мой процент получен", default=False)

    # Служебная информация
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    updated_at = models.DateTimeField("Последнее изменение", auto_now=True)

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        ordering = ['-created_at']

    def __str__(self):
        return f"Заказ #{self.id} — {self.client_name}"